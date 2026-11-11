"""Declarations of a tour and its steps."""

import weakref
from collections.abc import Sequence
from dataclasses import dataclass, fields
from functools import partial
from typing import Any, Literal

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.functional import Promise
from django.utils.html import json_script
from django.utils.module_loading import import_string
from django.utils.safestring import SafeString
from django.utils.translation import gettext_lazy as _
from django.utils.translation import pgettext_lazy

from page_tours.parts import TourParts

# Every tour that exists, by name. The references are weak, and each removes
# itself when its tour is collected, so a tour built per request leaves nothing.
_declared: dict[str, list[weakref.ref["Tour"]]] = {}

# The fields of Tour that are the package's own. Every other field is a
# Driver.js option, passed to the browser under its own name.
PACKAGE_FIELDS = {"name", "steps", "autoplay", "version"}

# The fields of TourStep that Driver.js reads from the step itself. Every other
# field is read from the step's popover.
STEP_LEVEL_FIELDS = {
    "element",
    "disableActiveInteraction",
    "advanceOnClick",
    "waitForElement",
}

Button = Literal["next", "previous", "close"]

# Driver.js's own default progress text.
PROGRESS_TEXT = "{{current}} of {{total}}"

# The default labels of the controls: lazy, so the active language applies when
# the tour renders.
NEXT_LABEL = pgettext_lazy("page tour control", "Next")
PREVIOUS_LABEL = pgettext_lazy("page tour control", "Previous")
DONE_LABEL = pgettext_lazy("page tour control", "Done")
CLOSE_LABEL = pgettext_lazy("page tour control", "Close")


def _forget(name: str, ref: weakref.ref["Tour"]) -> None:
    """Drop the record of a collected tour, and its name once no tour has it.

    Args:
        name: The name the tour was declared with.
        ref: The weak reference to the tour, which the collector has cleared.
    """
    refs = _declared.get(name, [])
    if ref in refs:
        refs.remove(ref)
    if not refs:
        _declared.pop(name, None)


@dataclass(frozen=True)
class TourStep:
    """One step of a tour, as Driver.js 1.10.2 takes it.

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
        advanceOnClick: Whether clicking the element moves to the next step.
        waitForElement: How long to wait for the element to appear, in
            milliseconds.
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
    """

    title: str | Promise = ""
    description: str | Promise = ""
    element: str = ""
    disableActiveInteraction: bool | None = None
    advanceOnClick: bool | None = None
    waitForElement: int | None = None
    side: Literal["top", "right", "bottom", "left"] | None = None
    align: Literal["start", "center", "end"] | None = None
    popoverClass: str | None = None
    showButtons: tuple[Button, ...] | None = None
    disableButtons: tuple[Button, ...] | None = None
    showProgress: bool | None = None
    progressText: str | None = None
    nextBtnText: str | Promise | None = None
    prevBtnText: str | Promise | None = None
    doneBtnText: str | Promise | None = None


@dataclass(frozen=True)
class Tour:
    """A guided tour of one page.

    A view puts the tour in its template context, and ``{{ tour }}`` in the
    page's template renders it. Every tour is recorded under its name when it is
    made, so the system checks can report a name declared twice or a
    ``PAGE_TOURS_OVERRIDES`` key that names no tour.

    The fields after ``version`` are Driver.js's configuration options, named and
    defaulting to the value Driver.js 1.10.2 itself uses. See
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
        overlayClickBehavior: What clicking the overlay does: ``"close"`` the tour
            or go to the ``"nextStep"``.
        overlayColor: The colour of the overlay.
        overlayOpacity: The opacity of the overlay, from 0 to 1.
        smoothScroll: Whether to scroll smoothly to each step's element.
        disableActiveInteraction: Whether the highlighted element ignores clicks.
        allowKeyboardControl: Whether the arrow and escape keys move through and
            close the tour.
        advanceOnClick: Whether clicking a step's element moves to the next step.
        waitForElement: How long to wait for a step's element to appear, in
            milliseconds.
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

    name: str
    steps: Sequence[TourStep]
    autoplay: bool = True
    version: int = 1
    animate: bool = True
    duration: int = 400
    allowClose: bool = True
    allowScroll: bool = True
    overlayClickBehavior: Literal["close", "nextStep"] = "close"
    overlayColor: str = "#000"
    overlayOpacity: float = 0.7
    smoothScroll: bool = False
    disableActiveInteraction: bool = False
    allowKeyboardControl: bool = True
    advanceOnClick: bool = False
    waitForElement: int = 0
    stagePadding: int = 10
    stageRadius: int = 5
    popoverOffset: int = 10
    popoverClass: str = ""
    showButtons: tuple[Button, ...] = ("next", "previous", "close")
    disableButtons: tuple[Button, ...] = ()
    showProgress: bool = False
    progressText: str = PROGRESS_TEXT
    nextBtnText: str | Promise = NEXT_LABEL
    prevBtnText: str | Promise = PREVIOUS_LABEL
    doneBtnText: str | Promise = DONE_LABEL
    closeBtnLabel: str | Promise = CLOSE_LABEL

    def __post_init__(self):
        """Refuse a bad tour, freeze its steps and record it under its name."""
        if not isinstance(self.name, str) or not self.name.strip():
            raise ImproperlyConfigured(_("A tour needs a name."))
        if not self.steps:
            raise ImproperlyConfigured(_("A tour needs at least one step."))
        if (
            not isinstance(self.version, int)
            or isinstance(self.version, bool)
            or self.version < 1
        ):
            raise ImproperlyConfigured(
                _("A tour's version must be a whole number of 1 or more.")
            )
        object.__setattr__(self, "steps", tuple(self.steps))
        _declared.setdefault(self.name, []).append(
            weakref.ref(self, partial(_forget, self.name))
        )

    def __html__(self) -> SafeString:
        """Render the tour as the element the package's script plays it from.

        This is what ``{{ tour }}`` outputs in a template: a
        ``<script id="page-tour-steps" type="application/json">`` element holding
        the tour's name and version, whether it plays by itself, its steps in the
        form Driver.js takes, the classes each part of a shown step carries and the
        Driver.js options of the tour that plays, in the names Driver.js uses.

        When the ``PAGE_TOURS_OVERRIDES`` setting names the tour, the replacement
        is rendered in its place, or nothing when the setting turns it off. The
        replacement keeps this tour's name, and plays at this tour's version plus
        its own, less one, so a browser that saw this tour does not see the
        replacement by itself until the replacement's own version is raised. The
        setting is read every time the tour renders.

        Returns:
            The element, marked safe so the template does not escape it, or an
            empty string when the tour is turned off.

        Raises:
            ImproperlyConfigured: If the setting's entry for this tour is not valid.
        """
        played = self
        version = self.version
        overrides = getattr(settings, "PAGE_TOURS_OVERRIDES", {})
        if self.name in overrides:
            replacement = resolve_override(self.name, overrides[self.name])
            if replacement is None:
                return SafeString("")
            played = replacement
            version = self.version + replacement.version - 1
        payload = {
            "id": self.name,
            "version": version,
            "autoplay": played.autoplay,
            "steps": played.as_driver_steps(),
            "parts": TourParts.classes(),
            "options": {
                option.name: getattr(played, option.name)
                for option in fields(played)
                if option.name not in PACKAGE_FIELDS
            },
        }
        return json_script(payload, "page-tour-steps")

    def __str__(self) -> SafeString:
        """Render the tour, as ``__html__`` does.

        A template converts a value with ``str()`` before it escapes it, so this
        has to return the same safe string for ``{{ tour }}`` to arrive unescaped.

        Returns:
            What ``__html__`` returns.
        """
        return self.__html__()

    def as_driver_steps(self) -> list[dict[str, Any]]:
        """Convert the steps to the form Driver.js takes.

        Fields left as ``None`` or empty are left out, so that the tour's value
        applies. Translated text is converted with ``str()`` when this is called,
        so the active language applies.

        Returns:
            One Driver.js step per step, in the declared order.
        """
        driver_steps: list[dict[str, Any]] = []
        for step in self.steps:
            driver_step: dict[str, Any] = {"popover": {}}
            for field in fields(step):
                value = getattr(step, field.name)
                if value in (None, ""):
                    continue
                if isinstance(value, Promise):
                    value = str(value)
                level = (
                    driver_step
                    if field.name in STEP_LEVEL_FIELDS
                    else driver_step["popover"]
                )
                level[field.name] = value
            driver_steps.append(driver_step)
        return driver_steps


def resolve_override(name: str, value: Any) -> Tour | None:
    """Resolve one entry of the ``PAGE_TOURS_OVERRIDES`` setting.

    Args:
        name: The name of the tour the entry changes, for the error message.
        value: A dotted path to a ``Tour``, or ``None`` to turn the tour off.

    Returns:
        The replacement tour, or ``None`` when the tour is turned off.

    Raises:
        ImproperlyConfigured: If ``value`` is neither a string nor ``None``, the
            path does not import, or it names something that is not a ``Tour``.
            A module whose own ``Tour(...)`` is invalid raises its own error.
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
    if not isinstance(replacement, Tour):
        raise ImproperlyConfigured(
            _("PAGE_TOURS_OVERRIDES[%(name)s]: %(path)s is not a Tour.")
            % {"name": name, "path": value}
        )
    return replacement


def tour_overrides() -> dict[str, Tour | None]:
    """Resolve every entry of the ``PAGE_TOURS_OVERRIDES`` setting.

    Returns:
        The replacement tour, or ``None`` for a tour turned off, by tour name.

    Raises:
        ImproperlyConfigured: If any entry is not valid.
    """
    overrides = getattr(settings, "PAGE_TOURS_OVERRIDES", {})
    return {name: resolve_override(name, value) for name, value in overrides.items()}


def declared_tours() -> dict[str, list[Tour]]:
    """Return every tour that exists, by its name.

    A tour is declared when it is made, which for a tour in a module is when the
    module is imported. A tour that nothing refers to any more is left out.

    Returns:
        The tours declared under each name, in the order they were made.
    """
    tours: dict[str, list[Tour]] = {}
    for name, refs in list(_declared.items()):
        alive = [tour for ref in list(refs) if (tour := ref()) is not None]
        if alive:
            tours[name] = alive
    return tours
