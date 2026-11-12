"""Declarations of a tour and its steps."""

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any, ClassVar, Literal

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.functional import Promise
from django.utils.translation import gettext_lazy as _
from django.utils.translation import pgettext_lazy

from page_tours.driver import Declaration, PopoverContent

Button = Literal["next", "previous", "close"]

# The default texts of the controls, from PAGE_TOURS_TEXT or else the package's
# own: lazy, so the active language applies when the tour renders.
SITE_TEXT = getattr(settings, "PAGE_TOURS_TEXT", {}).get("tour", {})
PROGRESS_TEXT = SITE_TEXT.get(
    "progressText", pgettext_lazy("page tour control", "{{current}} of {{total}}")
)
NEXT_LABEL = SITE_TEXT.get("nextBtnText", pgettext_lazy("page tour control", "Next"))
PREVIOUS_LABEL = SITE_TEXT.get(
    "prevBtnText", pgettext_lazy("page tour control", "Previous")
)
DONE_LABEL = SITE_TEXT.get("doneBtnText", pgettext_lazy("page tour control", "Done"))
CLOSE_LABEL = SITE_TEXT.get(
    "closeBtnLabel", pgettext_lazy("page tour control", "Close")
)


@dataclass(frozen=True, kw_only=True)
class TourStep(PopoverContent):
    """One step of a tour, as Driver.js 1.11.0 takes it.

    The fields are named as Driver.js names them. See
    https://driverjs.com/docs/configuration for what each one does. An option left
    as ``None`` falls back to the tour's value of the same name. Title,
    description and the button texts are passed to Driver.js as they are, and it
    writes them into the page as HTML.

    Args:
        title: The heading of the popover. Without one, the popover shows no
            heading.
        description: The body of the popover.
        element: A CSS selector for the element the step points at. Empty means
            the step is attached to nothing.
        disableActiveInteraction: Whether the highlighted element ignores clicks
            on this step.
        advanceOn: The event on the element that moves to the next step, such as
            ``"click"``, a tuple of events, or ``False`` for none.
        waitForElement: How long to wait for the element to appear, in
            milliseconds.
        allowedElements: A CSS selector, or a tuple of them, for elements besides
            the highlighted one that stay usable on this step.
        skipMissingElement: ``False`` shows this step attached to nothing when
            its element is missing or hidden, instead of skipping it.
        side: Which side of the element the popover sits on.
        align: How the popover lines up along that side.
        popoverClass: A class added to this step's popover.
        showButtons: The buttons this step's popover shows, from ``"next"``,
            ``"previous"`` and ``"close"``.
        disableButtons: The buttons that show but cannot be pressed on this step.
        showProgress: Whether this step's popover shows how far through the tour
            it is.
        progressText: The progress text, with ``{{current}}`` and ``{{total}}``
            standing for the step's number and the number of steps.
        nextBtnText: The text of the next button on this step.
        prevBtnText: The text of the previous button on this step.
        doneBtnText: The text of the button when this is the last step.
        closeBtnLabel: The accessible name of the close button on this step.
    """

    nested = {
        "popover": PopoverContent.popover_fields
        | {
            "showButtons",
            "disableButtons",
            "showProgress",
            "progressText",
            "nextBtnText",
            "prevBtnText",
            "doneBtnText",
            "closeBtnLabel",
        }
    }

    element: str = ""
    disableActiveInteraction: bool | None = None
    advanceOn: Literal[False] | str | tuple[str, ...] | None = None
    waitForElement: int | None = None
    allowedElements: str | tuple[str, ...] | None = None
    skipMissingElement: bool | None = None
    showButtons: tuple[Button, ...] | None = None
    disableButtons: tuple[Button, ...] | None = None
    showProgress: bool | None = None
    progressText: str | None = None
    nextBtnText: str | Promise | None = None
    prevBtnText: str | Promise | None = None
    doneBtnText: str | Promise | None = None
    closeBtnLabel: str | Promise | None = None


@dataclass(frozen=True, kw_only=True)
class Tour(Declaration):
    """A guided tour of one page.

    A view puts the tour in its template context, and ``{{ tour }}`` in the
    page's template renders it. Every tour is recorded under its name when it is
    made, so the system checks can report a name declared twice or a
    ``PAGE_TOURS_OVERRIDES`` key that names no tour.

    The fields after ``version`` are Driver.js's configuration options, named and
    defaulting to the value Driver.js 1.11.0 itself uses. See
    https://driverjs.com/docs/configuration for what each one does. Options that
    take a JavaScript function are not available. Driver.js writes the button
    texts and the progress text into the page as HTML, so they are passed on as
    they are.

    Args:
        name: The name the tour is known by: a browser remembers that it has seen
            the tour under it, and ``PAGE_TOURS_OVERRIDES`` changes the tour by it.
            Plain text, never empty. A reusable app names its tours
            ``"<app_label>.<tour>"``.
        steps: The steps in the order they are shown. At least one.
        autoplay: Whether the tour plays by itself the first time a browser opens
            the page.
        version: A whole number of 1 or more. Raise it when the tour has changed
            enough that people who saw it should see it again: a browser that saw
            another version plays it by itself once more.
        animate: Whether to animate the tour.
        duration: How long the animation takes, in milliseconds.
        allowClose: Whether a visitor can close the tour before its last step.
        allowScroll: Whether the page can be scrolled while the tour shows.
        overlayClickBehavior: What clicking the overlay does: ``"close"`` the tour,
            go to the ``"nextStep"``, or ``"none"``.
        overlayColor: The colour of the overlay.
        overlayOpacity: The opacity of the overlay, from 0 to 1.
        smoothScroll: Whether to scroll smoothly to each step's element.
        disableActiveInteraction: Whether the highlighted element ignores clicks.
        allowKeyboardControl: Whether the arrow and escape keys move through and
            close the tour.
        advanceOn: The event on a step's element that moves to the next step,
            such as ``"click"``, a tuple of events, or ``False`` for none.
        waitForElement: How long to wait for a step's element to appear, in
            milliseconds.
        allowedElements: A CSS selector, or a tuple of them, for elements besides
            the highlighted one that stay usable on every step. Driver.js has no
            default, so ``None`` leaves none.
        stagePadding: The space around the highlighted element, in pixels.
        stageRadius: The corner radius of the highlight, in pixels.
        popoverOffset: The distance between the popover and the element, in pixels.
        popoverClass: A class added to every popover.
        showButtons: The buttons the popover shows, from ``"next"``,
            ``"previous"`` and ``"close"``.
        disableButtons: The buttons that show but cannot be pressed.
        showProgress: Whether the popover shows how far through the tour it is.
        progressText: The progress text, with ``{{current}}`` and ``{{total}}``
            standing for the step's number and the number of steps.
        nextBtnText: The text of the next button, in the active language by
            default.
        prevBtnText: The text of the previous button, in the active language by
            default.
        doneBtnText: The text of the button on the last step, in the active
            language by default.
        closeBtnLabel: The accessible name of the close button, in the active
            language by default.

    Raises:
        ImproperlyConfigured: If ``name`` is not a string with something in it,
            ``steps`` is empty or ``version`` is not a whole number of 1 or more.
    """

    kind: ClassVar[str] = "tour"
    content_field: ClassVar[str] = "steps"
    package_fields = Declaration.package_fields | {"autoplay"}

    steps: Sequence[TourStep]
    autoplay: bool = True
    animate: bool = True
    duration: int = 400
    allowClose: bool = True
    allowScroll: bool = True
    overlayClickBehavior: Literal["close", "nextStep", "none"] = "close"
    overlayColor: str = "#000"
    overlayOpacity: float = 0.7
    smoothScroll: bool = False
    disableActiveInteraction: bool = False
    allowKeyboardControl: bool = True
    advanceOn: Literal[False] | str | tuple[str, ...] = False
    waitForElement: int = 0
    allowedElements: str | tuple[str, ...] | None = None
    stagePadding: int = 10
    stageRadius: int = 5
    popoverOffset: int = 10
    popoverClass: str = ""
    showButtons: tuple[Button, ...] = ("next", "previous", "close")
    disableButtons: tuple[Button, ...] = ()
    showProgress: bool = False
    progressText: str | Promise = PROGRESS_TEXT
    nextBtnText: str | Promise = NEXT_LABEL
    prevBtnText: str | Promise = PREVIOUS_LABEL
    doneBtnText: str | Promise = DONE_LABEL
    closeBtnLabel: str | Promise = CLOSE_LABEL

    def __post_init__(self):
        """Refuse a tour without steps, freeze its steps and declare it."""
        if not self.steps:
            raise ImproperlyConfigured(_("A tour needs at least one step."))
        object.__setattr__(self, "steps", tuple(self.steps))
        super().__post_init__()

    def payload(self, name: str, version: int) -> dict[str, Any]:
        """Return what the browser needs to play the tour.

        Args:
            name: The name the browser remembers the tour by.
            version: The version it remembers it at.

        Returns:
            What every declaration sends, with whether the tour plays by itself.
        """
        return {**super().payload(name, version), "autoplay": self.autoplay}
