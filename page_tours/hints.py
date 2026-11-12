"""Declarations of hints: pointers on a page that open a popover when pressed."""

from collections.abc import Sequence
from dataclasses import dataclass
from typing import ClassVar

from django.utils.functional import Promise
from django.utils.translation import pgettext_lazy

from page_tours.driver import Alignment, Declaration, DriverObject, PopoverContent, Side

# The default label of a hint's button: lazy, so the active language applies when
# the hints render.
GOT_IT_LABEL = pgettext_lazy("page hint control", "Got it")


@dataclass(frozen=True, kw_only=True)
class Beacon(DriverObject):
    """The marker that shows where a hint is, as Driver.js takes it.

    The fields are named as Driver.js names them. An option left as ``None`` is
    left out, so the value Driver.js falls back to applies. Set on a hint, it
    applies to that hint; set on the hints, it applies to every hint without one.

    Args:
        side: Which side of the element the beacon sits on.
        align: How the beacon lines up along that side.
        animate: Whether the beacon pulses.
        className: A class added to the beacon.
        offsetX: How far the beacon moves across, in pixels.
        offsetY: How far the beacon moves down, in pixels.
    """

    side: Side | None = None
    align: Alignment | None = None
    animate: bool | None = None
    className: str | None = None
    offsetX: int | None = None
    offsetY: int | None = None


@dataclass(frozen=True, kw_only=True)
class Hint(PopoverContent):
    """One hint on a page, as Driver.js takes it.

    The fields are named as Driver.js names them. An option left as ``None`` falls
    back to the value of the same name on the hints. Title, description and the
    button text are passed to Driver.js as they are, and it writes them into the
    page as HTML. Give every hint a title: it names the hint's beacon.

    Args:
        title: The heading of the popover.
        description: The body of the popover.
        element: A CSS selector for the element the hint points at.
        id: What a browser remembers the hint was dismissed under. Without one,
            the hint's position among the hints stands in for it.
        beacon: The marker of this hint.
        showButton: Whether the popover shows its button.
        buttonText: The text of the popover's button.
        side: Which side of the element the popover sits on.
        align: How the popover lines up along that side.
        popoverClass: A class added to this hint's popover.
    """

    nested = {"popover": PopoverContent.popover_fields | {"showButton", "buttonText"}}

    element: str
    id: str | None = None
    beacon: Beacon | None = None
    showButton: bool | None = None
    buttonText: str | Promise | None = None


@dataclass(frozen=True, kw_only=True)
class Hints(Declaration):
    """Hints on one page.

    A view puts the hints in its template context, and ``{{ hints }}`` in the
    page's template renders them. Every set of hints is recorded under its name
    when it is made, so the system checks can report a name declared twice or a
    ``PAGE_TOURS_OVERRIDES`` key that names nothing.

    The fields after ``version`` are Driver.js's hint options, named and
    defaulting to the value Driver.js itself uses. Options that take a JavaScript
    function are not available. Driver.js writes the button text into the page as
    HTML, so it is passed on as it is.

    Args:
        name: The name the hints are known by: a browser remembers which were
            dismissed under it, and ``PAGE_TOURS_OVERRIDES`` changes the hints by
            it. Plain text, never empty, and not shared with a tour.
        hints: The hints, in order. At least one.
        version: A whole number of 1 or more. Raise it when the hints have changed
            enough that dismissed ones should show again.
        beacon: The marker of every hint that has none of its own.
        buttonText: The text of the popover's button, in the active language by
            default.
        popoverClass: A class added to every popover.
        popoverOffset: The distance between the popover and the element, in pixels.
        overlay: Whether the page is dimmed while a popover is open.
        overlayColor: The colour of the overlay.
        overlayOpacity: The opacity of the overlay, from 0 to 1.

    Raises:
        ImproperlyConfigured: If ``name`` is not a string with something in it or
            ``version`` is not a whole number of 1 or more.
    """

    kind: ClassVar[str] = "hints"
    content_field: ClassVar[str] = "hints"
    text_kind: ClassVar[str] = "hint"
    text_fields: ClassVar[frozenset[str]] = frozenset({"buttonText"})

    hints: Sequence[Hint]
    beacon: Beacon | None = None
    buttonText: str | Promise = GOT_IT_LABEL
    popoverClass: str = ""
    popoverOffset: int = 10
    overlay: bool = False
    overlayColor: str = "#000"
    overlayOpacity: float = 0.7

    def __post_init__(self):
        """Freeze the hints and declare them under their name."""
        object.__setattr__(self, "hints", tuple(self.hints))
        super().__post_init__()
