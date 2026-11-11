"""Declarations of a page's hints, mirroring Driver.js's hints.

A hint is a pulsing beacon on an element. A visitor opens it, in any order, to
read a popover about the element, while the page stays usable. Pressing the
popover's button dismisses the hint, and the browser remembers that it was
dismissed until the hints' version is raised.

See https://driverjs.com/docs/hints.
"""

from collections.abc import Sequence
from dataclasses import dataclass
from typing import ClassVar

from django.utils.functional import Promise
from django.utils.translation import pgettext_lazy

from page_tours.driver import Alignment, DriverObject, Guide, PopoverContent, Side

# The default text of a hint's button: lazy, so the active language applies.
GOT_IT_LABEL = pgettext_lazy("page hint control", "Got it")


@dataclass(frozen=True, kw_only=True)
class Beacon(DriverObject):
    """Where a hint's beacon sits on its element, and how it looks.

    Every field left as ``None`` falls back to the hints' beacon, then to
    Driver.js's default: the top edge, at its end, pulsing.

    Args:
        side: The edge of the element the beacon sits on.
        align: Where along that edge it sits.
        animate: Whether the beacon pulses. It never does for a visitor who
            prefers reduced motion.
        className: A class added to the beacon.
        offsetX: Pixels to move the beacon right, or left when negative.
        offsetY: Pixels to move the beacon down, or up when negative.
    """

    side: Side | None = None
    align: Alignment | None = None
    animate: bool | None = None
    className: str | None = None
    offsetX: int | None = None
    offsetY: int | None = None


@dataclass(frozen=True, kw_only=True)
class Hint(PopoverContent):
    """One hint: a beacon on an element and the popover it opens.

    The popover's fields sit on the hint, as on a tour step, and reach Driver.js
    inside the hint's ``popover``.

    Args:
        element: A CSS selector for the element the hint is about.
        id: What the browser remembers the hint's dismissal under. Defaults to
            the element.
        beacon: Where this hint's beacon sits, in place of the hints' beacon.
        showButton: Whether the popover shows its button.
        buttonText: The text of this hint's button.
    """

    element: str
    id: str | None = None
    beacon: Beacon | None = None
    showButton: bool | None = None
    buttonText: str | Promise | None = None

    nested: ClassVar[dict[str, frozenset[str]]] = {
        "popover": PopoverContent.popover_fields | {"showButton", "buttonText"}
    }


@dataclass(frozen=True, kw_only=True)
class Hints(Guide):
    """A page's hints: Driver.js's hints configuration, as a Python class.

    A view puts them in its template context, and ``{{ hints }}`` renders them.
    The fields after ``version`` are Driver.js's options, named and defaulted as
    in Driver.js 1.11.0. Options that take a JavaScript function are not
    available.

    Args:
        hints: The hints, in the order a keyboard reaches their beacons.
        beacon: Where every beacon sits, unless a hint says otherwise.
        buttonText: The text of every hint's button.
        popoverClass: A class added to every hint's popover.
        popoverOffset: The distance between a popover and its beacon, in pixels.
        overlay: Whether the page is dimmed while a hint is open.
        overlayColor: The colour of that overlay.
        overlayOpacity: Its opacity, from 0 to 1.
    """

    hints: Sequence[Hint]
    beacon: Beacon | None = None
    buttonText: str | Promise = GOT_IT_LABEL
    popoverClass: str = ""
    popoverOffset: int = 10
    overlay: bool = False
    overlayColor: str = "#000"
    overlayOpacity: float = 0.7

    kind: ClassVar[str] = "hints"

    def __post_init__(self):
        """Freeze the hints and record them under their name."""
        object.__setattr__(self, "hints", tuple(self.hints))
        super().__post_init__()
