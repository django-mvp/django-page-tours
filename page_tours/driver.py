"""The shared bases of everything a page declares for Driver.js."""

import weakref
from dataclasses import dataclass, fields
from functools import partial
from typing import Any, ClassVar, Literal

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.functional import Promise
from django.utils.html import json_script
from django.utils.module_loading import import_string
from django.utils.safestring import SafeString
from django.utils.translation import gettext_lazy as _

from page_tours.parts import TourParts

Side = Literal["top", "right", "bottom", "left"]
Alignment = Literal["start", "center", "end"]


def driver_value(value: Any) -> Any:
    """Convert one value of a field to the form Driver.js takes.

    Args:
        value: A declared object, a tuple or list, a lazy string or any other
            value.

    Returns:
        The object's ``as_driver()``, a list of the converted items, the string
        a lazy string stands for in the active language, or the value as it is.
    """
    if isinstance(value, DriverObject):
        return value.as_driver()
    if isinstance(value, tuple | list):
        return [driver_value(item) for item in value]
    if isinstance(value, Promise):
        return str(value)
    return value


@dataclass(frozen=True, kw_only=True)
class DriverObject:
    """A declaration that mirrors one object of Driver.js.

    The fields are named as Driver.js names them. A field left as ``None`` is
    left out, so the value Driver.js falls back to applies.

    Attributes:
        package_fields: The fields that are the package's own, which Driver.js
            never receives.
        nested: The fields that Driver.js reads from an inner object, by the
            name of that object.
    """

    package_fields: ClassVar[frozenset[str]] = frozenset()
    nested: ClassVar[dict[str, frozenset[str]]] = {}

    def as_driver(self) -> dict[str, Any]:
        """Convert the object to the form Driver.js takes.

        Every inner object named in ``nested`` is created, even when nothing goes
        into it. Translated text is converted when this is called, so the active
        language applies.

        Returns:
            The fields that are neither package fields nor ``None``, each
            converted, with the nested ones inside their inner object.
        """
        driver: dict[str, Any] = {name: {} for name in self.nested}
        for field in fields(self):
            value = getattr(self, field.name)
            if field.name in self.package_fields or value is None:
                continue
            level = driver
            for name, members in self.nested.items():
                if field.name in members:
                    level = driver[name]
            level[field.name] = driver_value(value)
        return driver


@dataclass(frozen=True, kw_only=True)
class PopoverContent(DriverObject):
    """What a popover says and where it sits.

    See https://driverjs.com/docs/popover for what each field does.

    Attributes:
        popover_fields: The names of the fields below, which Driver.js reads from
            a popover.

    Args:
        title: The heading of the popover. Without one, the popover shows no
            heading.
        description: The body of the popover.
        side: Which side of the element the popover sits on.
        align: How the popover lines up along that side.
        popoverClass: A class added to the popover.
    """

    popover_fields: ClassVar[frozenset[str]] = frozenset(
        {"title", "description", "side", "align", "popoverClass"}
    )

    title: str | Promise | None = None
    description: str | Promise | None = None
    side: Side | None = None
    align: Alignment | None = None
    popoverClass: str | None = None


# Every declaration that exists, by name. The references are weak, and each
# removes itself when its declaration is collected, so one built per request
# leaves nothing.
declared: dict[str, list[weakref.ref["Declaration"]]] = {}


def forget(name: str, ref: weakref.ref["Declaration"]) -> None:
    """Drop the record of a collected declaration, and its name once none has it.

    Args:
        name: The name the declaration was declared with.
        ref: The weak reference to the declaration, which the collector has
            cleared.
    """
    refs = declared.get(name, [])
    if ref in refs:
        refs.remove(ref)
    if not refs:
        declared.pop(name, None)


@dataclass(frozen=True, kw_only=True)
class Declaration(DriverObject):
    """What a page renders: a name, a version and Driver.js's configuration.

    A subclass is one kind of declaration, such as a tour. It is recorded under
    its name when it is made, so the system checks can report a name declared
    twice or a ``PAGE_TOURS_OVERRIDES`` key that names nothing.

    Attributes:
        kind: What the declaration is called in the browser, such as ``"tour"``.
        content_field: The field that holds what the declaration shows, which the
            system checks compare to tell two declarations of one name apart.

    Args:
        name: The name the declaration is known by: a browser remembers what a
            visitor did under it, and ``PAGE_TOURS_OVERRIDES`` changes the
            declaration by it. Plain text, never empty.
        version: A whole number of 1 or more. Raise it when the declaration has
            changed enough that what a browser remembers should be forgotten.

    Raises:
        ImproperlyConfigured: If ``name`` is not a string with something in it or
            ``version`` is not a whole number of 1 or more.
    """

    kind: ClassVar[str]
    content_field: ClassVar[str]
    package_fields = frozenset({"name", "version"})

    name: str
    version: int = 1

    def __post_init__(self):
        """Refuse a bad name or version and record the declaration under its name."""
        cls = type(self).__name__
        if not isinstance(self.name, str) or not self.name.strip():
            raise ImproperlyConfigured(_("%(cls)s needs a name.") % {"cls": cls})
        if (
            not isinstance(self.version, int)
            or isinstance(self.version, bool)
            or self.version < 1
        ):
            raise ImproperlyConfigured(
                _("The version of %(cls)s must be a whole number of 1 or more.")
                % {"cls": cls}
            )
        declared.setdefault(self.name, []).append(
            weakref.ref(self, partial(forget, self.name))
        )

    def payload(self, name: str, version: int) -> dict[str, Any]:
        """Return what the browser needs to play the declaration.

        Args:
            name: The name the browser remembers the declaration by.
            version: The version it remembers it at.

        Returns:
            The kind, name, version, the classes of each part and the
            declaration as Driver.js takes it.
        """
        return {
            "kind": self.kind,
            "id": name,
            "version": version,
            "parts": TourParts.classes(),
            "config": self.as_driver(),
        }

    def __html__(self) -> SafeString:
        """Render the declaration as the element the package's script plays it from.

        This is what ``{{ declaration }}`` outputs in a template: a
        ``<script id="page-tours-<kind>" type="application/json">`` element.

        When the ``PAGE_TOURS_OVERRIDES`` setting names the declaration, the
        replacement is rendered in its place, or nothing when the setting turns it
        off. The replacement keeps this declaration's name, and plays at this
        declaration's version plus its own, less one, so a browser that saw this
        one does not see the replacement until the replacement's own version is
        raised. The setting is read every time the declaration renders.

        Returns:
            The element, marked safe so the template does not escape it, or an
            empty string when the declaration is turned off.

        Raises:
            ImproperlyConfigured: If the setting's entry for this declaration is
                not valid or names a replacement of another class.
        """
        played = self
        version = self.version
        overrides = getattr(settings, "PAGE_TOURS_OVERRIDES", {})
        if self.name in overrides:
            replacement = resolve_override(self.name, overrides[self.name], type(self))
            if replacement is None:
                return SafeString("")
            played = replacement
            version = self.version + replacement.version - 1
        return json_script(
            played.payload(self.name, version), f"page-tours-{self.kind}"
        )

    def __str__(self) -> SafeString:
        """Render the declaration, as ``__html__`` does.

        A template converts a value with ``str()`` before it escapes it, so this
        has to return the same safe string for the declaration to arrive
        unescaped.

        Returns:
            What ``__html__`` returns.
        """
        return self.__html__()


def resolve_override(
    name: str, value: Any, cls: type[Declaration] = Declaration
) -> Declaration | None:
    """Resolve one entry of the ``PAGE_TOURS_OVERRIDES`` setting.

    Args:
        name: The name of the declaration the entry changes, for the error
            message.
        value: A dotted path to a declaration, or ``None`` to turn it off.
        cls: The class the replacement has to be.

    Returns:
        The replacement, or ``None`` when the declaration is turned off.

    Raises:
        ImproperlyConfigured: If ``value`` is neither a string nor ``None``, the
            path does not import, or it names something that is not a ``cls``.
            A module whose own declaration is invalid raises its own error.
    """
    if value is None:
        return None
    if not isinstance(value, str):
        raise ImproperlyConfigured(
            _(
                "PAGE_TOURS_OVERRIDES[%(name)s] must be the dotted path of a "
                "%(cls)s or None."
            )
            % {"name": name, "cls": cls.__name__}
        )
    try:
        replacement = import_string(value)
    except ImportError as error:
        raise ImproperlyConfigured(
            _("PAGE_TOURS_OVERRIDES[%(name)s]: %(path)s cannot be imported.")
            % {"name": name, "path": value}
        ) from error
    if not isinstance(replacement, cls):
        raise ImproperlyConfigured(
            _("PAGE_TOURS_OVERRIDES[%(name)s]: %(path)s is not a %(cls)s.")
            % {"name": name, "path": value, "cls": cls.__name__}
        )
    return replacement


def declaration_overrides() -> dict[str, Declaration | None]:
    """Resolve every entry of the ``PAGE_TOURS_OVERRIDES`` setting.

    Returns:
        The replacement, or ``None`` for a declaration turned off, by name.

    Raises:
        ImproperlyConfigured: If any entry is not valid.
    """
    overrides = getattr(settings, "PAGE_TOURS_OVERRIDES", {})
    return {name: resolve_override(name, value) for name, value in overrides.items()}


def declarations() -> dict[str, list[Declaration]]:
    """Return every declaration that exists, by its name.

    A declaration is declared when it is made, which for one in a module is when
    the module is imported. One that nothing refers to any more is left out.

    Returns:
        The declarations under each name, in the order they were made.
    """
    found: dict[str, list[Declaration]] = {}
    for name, refs in list(declared.items()):
        alive = [item for ref in list(refs) if (item := ref()) is not None]
        if alive:
            found[name] = alive
    return found
