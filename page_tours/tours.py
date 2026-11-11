"""Declarations of a tour and its steps, mirroring Driver.js's own."""

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any, ClassVar, Literal

from django.core.exceptions import ImproperlyConfigured
from django.utils.functional import Promise
from django.utils.translation import gettext_lazy as _
from django.utils.translation import pgettext_lazy

from page_tours.driver import (
    Guide,
    PopoverContent,
    declared_guides,
    guide_overrides,
    resolve_override,
)

Button = Literal["next", "previous", "close"]

# An event, or several, on the step's element that moves to the next step.
AdvanceOn = Literal[False] | str | tuple[str, ...]

# Driver.js's own default progress text.
PROGRESS_TEXT = "{{current}} of {{total}}"

# The default labels of the controls: lazy, so the active language applies when
# the tour renders.
NEXT_LABEL = pgettext_lazy("page tour control", "Next")
PREVIOUS_LABEL = pgettext_lazy("page tour control", "Previous")
DONE_LABEL = pgettext_lazy("page tour control", "Done")
CLOSE_LABEL = pgettext_lazy("page tour control", "Close")


@dataclass(frozen=True)
class TourStep(PopoverContent):
    """One step of a tour, as Driver.js 1.11.0 takes it.

    The fields are named as Driver.js names them; see
    https://driverjs.com/docs/configuration. A field left as ``None`` falls back to
    the tour's value of the same name. The popover's fields sit on the step itself,
    and reach Driver.js inside the step's ``popover``.

    Args:
        element: A CSS selector for the element the step points at. ``None``
            attaches the step to nothing.
        disableActiveInteraction: Whether the element ignores clicks on this step.
        advanceOn: The event, or events, on the element that move to the next step.
        waitForElement: How long to wait for the element to appear, in ms.
        showButtons: The buttons this step's popover shows.
        disableButtons: The buttons that show but cannot be pressed.
        showProgress: Whether the popover shows how far through the tour it is.
        progressText: The progress text, with ``{{current}}`` and ``{{total}}``.
        nextBtnText: The text of the next button on this step.
        prevBtnText: The text of the previous button on this step.
        doneBtnText: The text of the button when this is the last step.
    """

    element: str | None = None
    disableActiveInteraction: bool | None = None
    advanceOn: AdvanceOn | None = None
    waitForElement: int | None = None
    showButtons: tuple[Button, ...] | None = None
    disableButtons: tuple[Button, ...] | None = None
    showProgress: bool | None = None
    progressText: str | Promise | None = None
    nextBtnText: str | Promise | None = None
    prevBtnText: str | Promise | None = None
    doneBtnText: str | Promise | None = None

    nested: ClassVar[dict[str, frozenset[str]]] = {
        "popover": PopoverContent.popover_fields
        | {
            "showButtons",
            "disableButtons",
            "showProgress",
            "progressText",
            "nextBtnText",
            "prevBtnText",
            "doneBtnText",
        }
    }


@dataclass(frozen=True, kw_only=True)
class Tour(Guide):
    """A guided tour of one page: Driver.js's configuration, as a Python class.

    A view puts the tour in its template context, and ``{{ tour }}`` renders it.
    ``steps`` and every field after ``autoplay`` are Driver.js's options, named
    and defaulted as in Driver.js 1.11.0; see
    https://driverjs.com/docs/configuration. Options that take a JavaScript
    function are not available.

    Args:
        steps: The steps in the order they are shown. At least one.
        autoplay: Whether the tour plays by itself the first time a browser opens
            the page. The package's own.
    """

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
    advanceOn: AdvanceOn = False
    waitForElement: int = 0
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

    kind: ClassVar[str] = "tour"
    package_fields: ClassVar[frozenset[str]] = Guide.package_fields | {"autoplay"}

    def __post_init__(self):
        """Refuse a tour with no steps, freeze its steps and record it."""
        if not self.steps:
            raise ImproperlyConfigured(_("A tour needs at least one step."))
        object.__setattr__(self, "steps", tuple(self.steps))
        super().__post_init__()

    def payload(self, version: int | None = None) -> dict[str, Any]:
        """Return what the script plays the tour from, with whether it autoplays.

        Args:
            version: The version to play at, when it is not the tour's own.

        Returns:
            What every guide's payload holds, and ``autoplay``.
        """
        return {**super().payload(version), "autoplay": self.autoplay}


def tour_overrides():
    """Resolve every entry of the ``PAGE_TOURS_OVERRIDES`` setting.

    Returns:
        What ``guide_overrides`` returns.
    """
    return guide_overrides()


def declared_tours():
    """Return every guide that exists, by its name.

    Returns:
        What ``declared_guides`` returns.
    """
    return declared_guides()


__all__ = [
    "Tour",
    "TourStep",
    "declared_tours",
    "resolve_override",
    "tour_overrides",
]
