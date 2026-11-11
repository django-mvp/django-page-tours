"""The shared bases of everything a page declares for Driver.js."""

from dataclasses import dataclass, fields
from typing import Any, ClassVar, Literal

from django.utils.functional import Promise

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
