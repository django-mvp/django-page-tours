"""Python declarations of Driver.js objects, and what every page guide shares.

Every class the package declares a Driver.js object with is a frozen dataclass on
``DriverObject``. Its fields are named exactly as Driver.js names the options, and
``as_driver()`` turns it into the object Driver.js takes, with no code of its own:

- a field left as ``None`` is left out, so Driver.js's own default applies
- a translated string renders in the active language
- a nested object, or a list of them, is converted too
- a field named in ``nested`` goes into the inner object Driver.js reads it from,
  such as a step's ``popover``

``Guide`` is what a page renders with ``{{ … }}``: a tour, a set of hints or a
checklist. It carries the package's own fields, the name and the version, which
a browser remembers what a visitor did under.
"""

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
    """Convert one field's value to what Driver.js takes.

    Args:
        value: The value of a field.

    Returns:
        A guide inside another object as its whole payload, which the script
        builds, another Driver.js object as its own object, a list for a tuple or
        list, a string for a translated string, and anything else as it is.
    """
    if isinstance(value, Guide):
        return value.payload()
    if isinstance(value, DriverObject):
        return value.as_driver()
    if isinstance(value, tuple | list):
        return [driver_value(item) for item in value]
    if isinstance(value, Promise):
        return str(value)
    return value


@dataclass(frozen=True)
class DriverObject:
    """A Driver.js object declared in Python.

    Attributes:
        package_fields: Fields that are the package's own, never sent to Driver.js.
        nested: The inner objects Driver.js reads some fields from, by key.
    """

    package_fields: ClassVar[frozenset[str]] = frozenset()
    nested: ClassVar[dict[str, frozenset[str]]] = {}

    def as_driver(self) -> dict[str, Any]:
        """Return the object Driver.js takes.

        Returns:
            Every field that is not the package's own and not ``None``, under its
            own name, inside the inner object ``nested`` names for it.
        """
        result: dict[str, Any] = {}
        for field in fields(self):
            if field.name in self.package_fields:
                continue
            value = driver_value(getattr(self, field.name))
            if value is None:
                continue
            target = result
            for key, names in self.nested.items():
                if field.name in names:
                    target = result.setdefault(key, {})
            target[field.name] = value
        return result


@dataclass(frozen=True)
class PopoverContent(DriverObject):
    """What a popover says, and where it sits. Shared by a tour step and a hint.

    Args:
        title: The heading of the popover. Without one, it shows no heading.
        description: The body of the popover.
        side: Which side of the element the popover sits on.
        align: How the popover lines up along that side.
        popoverClass: A class added to the popover.
    """

    title: str | Promise | None = None
    description: str | Promise | None = None
    side: Side | None = None
    align: Alignment | None = None
    popoverClass: str | None = None

    popover_fields: ClassVar[frozenset[str]] = frozenset(
        {"title", "description", "side", "align", "popoverClass"}
    )


# Every guide that exists, by name. The references are weak, and each removes
# itself when its guide is collected, so a guide built per request leaves nothing.
declared: dict[str, list[weakref.ref["Guide"]]] = {}


def forget(name: str, ref: weakref.ref["Guide"]) -> None:
    """Drop the record of a collected guide, and its name once no guide has it.

    Args:
        name: The name the guide was declared with.
        ref: The weak reference to the guide, which the collector has cleared.
    """
    refs = declared.get(name, [])
    if ref in refs:
        refs.remove(ref)
    if not refs:
        declared.pop(name, None)


@dataclass(frozen=True, kw_only=True)
class Guide(DriverObject):
    """What a page renders with ``{{ … }}``: a tour, hints or a checklist.

    Args:
        name: The name the guide is known by. A browser remembers what a visitor
            did under it, and ``PAGE_TOURS_OVERRIDES`` changes the guide by it. A
            reusable app names its guides ``"<app_label>.<guide>"``.
        version: Raise it to show the guide afresh to people who have used it.

    Attributes:
        kind: What the script plays the guide as.
    """

    name: str
    version: int = 1

    kind: ClassVar[str]
    package_fields: ClassVar[frozenset[str]] = frozenset({"name", "version"})

    def __post_init__(self):
        """Refuse a guide with no name or a bad version, and record it."""
        if not isinstance(self.name, str) or not self.name.strip():
            raise ImproperlyConfigured(_("A guide needs a name."))
        if (
            not isinstance(self.version, int)
            or isinstance(self.version, bool)
            or self.version < 1
        ):
            raise ImproperlyConfigured(
                _("A guide's version must be a whole number of 1 or more.")
            )
        declared.setdefault(self.name, []).append(
            weakref.ref(self, partial(forget, self.name))
        )

    def payload(self, version: int | None = None) -> dict[str, Any]:
        """Return everything the script needs to play the guide.

        Args:
            version: The version to play at, when it is not the guide's own.

        Returns:
            The guide's kind, name and version, the classes each part carries and
            its Driver.js object.
        """
        return {
            "kind": self.kind,
            "id": self.name,
            "version": version or self.version,
            "parts": TourParts.classes(),
            "config": self.as_driver(),
        }

    def __html__(self) -> SafeString:
        """Render the guide as the element the package's script plays it from.

        When ``PAGE_TOURS_OVERRIDES`` names the guide, the replacement renders in
        its place, keeping this guide's name, or nothing when the setting turns it
        off.

        Returns:
            A ``<script id="page-tours-<kind>" type="application/json">`` element,
            or an empty string when the guide is turned off.
        """
        played: Guide = self
        version = self.version
        overrides = getattr(settings, "PAGE_TOURS_OVERRIDES", {})
        if self.name in overrides:
            replacement = resolve_override(self.name, overrides[self.name])
            if replacement is None:
                return SafeString("")
            played = replacement
            version = self.version + replacement.version - 1
        payload = played.payload(version)
        payload["id"] = self.name
        return json_script(payload, f"page-tours-{self.kind}")

    def __str__(self) -> SafeString:
        """Render the guide, as ``__html__`` does, so ``{{ guide }}`` is not escaped.

        Returns:
            What ``__html__`` returns.
        """
        return self.__html__()


def resolve_override(name: str, value: Any) -> Guide | None:
    """Resolve one entry of the ``PAGE_TOURS_OVERRIDES`` setting.

    Args:
        name: The name of the guide the entry changes, for the error message.
        value: A dotted path to a guide, or ``None`` to turn the guide off.

    Returns:
        The replacement, or ``None`` when the guide is turned off.

    Raises:
        ImproperlyConfigured: If the entry is not a path to a guide or ``None``.
    """
    if value is None:
        return None
    if not isinstance(value, str):
        raise ImproperlyConfigured(
            _(
                "PAGE_TOURS_OVERRIDES[%(name)s] must be the dotted path of a Tour "
                "or None."
            )
            % {"name": name}
        )
    try:
        replacement = import_string(value)
    except ImportError as error:
        raise ImproperlyConfigured(
            _("PAGE_TOURS_OVERRIDES[%(name)s]: %(path)s cannot be imported.")
            % {"name": name, "path": value}
        ) from error
    if not isinstance(replacement, Guide):
        raise ImproperlyConfigured(
            _("PAGE_TOURS_OVERRIDES[%(name)s]: %(path)s is not a Tour.")
            % {"name": name, "path": value}
        )
    return replacement


def guide_overrides() -> dict[str, Guide | None]:
    """Resolve every entry of the ``PAGE_TOURS_OVERRIDES`` setting.

    Returns:
        The replacement, or ``None`` for a guide turned off, by name.
    """
    overrides = getattr(settings, "PAGE_TOURS_OVERRIDES", {})
    return {name: resolve_override(name, value) for name, value in overrides.items()}


def declared_guides() -> dict[str, list[Guide]]:
    """Return every guide that exists, by its name.

    Returns:
        The guides declared under each name, in the order they were made.
    """
    guides: dict[str, list[Guide]] = {}
    for name, refs in list(declared.items()):
        alive = [guide for ref in list(refs) if (guide := ref()) is not None]
        if alive:
            guides[name] = alive
    return guides
