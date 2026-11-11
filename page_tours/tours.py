"""Declarations of a tour and its steps."""

import weakref
from collections.abc import Sequence
from dataclasses import dataclass, fields
from functools import partial
from typing import Any, Literal

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.functional import Promise
from django.utils.html import escape, json_script
from django.utils.module_loading import import_string
from django.utils.safestring import SafeString
from django.utils.translation import gettext_lazy as _
from django.utils.translation import pgettext_lazy

from page_tours.parts import TourParts

# Every tour that exists, by name. The references are weak, and each removes
# itself when its tour is collected, so a tour built per request leaves nothing.
_declared: dict[str, list[weakref.ref["Tour"]]] = {}

# The fields of Tour that are the package's own. Every other field is a
# Driver.js option, passed to the browser under its Driver.js name.
PACKAGE_FIELDS = {"name", "steps", "autoplay", "version"}

Button = Literal["next", "previous", "close"]

# Driver.js's own default progress text.
PROGRESS_TEXT = "{{current}} of {{total}}"

# The default labels of the controls: lazy, so the active language applies when
# the tour renders.
NEXT_LABEL = pgettext_lazy("page tour control", "Next")
PREVIOUS_LABEL = pgettext_lazy("page tour control", "Previous")
DONE_LABEL = pgettext_lazy("page tour control", "Done")
CLOSE_LABEL = pgettext_lazy("page tour control", "Close")


def camel_case(name: str) -> str:
    """Convert a snake_case field name to the camelCase name Driver.js uses.

    Args:
        name: The field name, such as ``overlay_opacity``.

    Returns:
        The Driver.js name, such as ``overlayOpacity``.
    """
    first, *rest = name.split("_")
    return first + "".join(word.capitalize() for word in rest)


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
    """One step of a tour.

    Args:
        title: The heading of the step. Plain text, never empty.
        text: The body of the step. Plain text, never empty.
        element: A CSS selector for the element the step points at. Empty means
            the step is attached to nothing.

    Raises:
        ImproperlyConfigured: If ``title`` or ``text`` is empty or only whitespace.
    """

    title: str | Promise
    text: str | Promise
    element: str = ""

    def __post_init__(self):
        """Refuse a step with no title or no text."""
        for name in ("title", "text"):
            if not str(getattr(self, name)).strip():
                raise ImproperlyConfigured(
                    _("A tour step needs a %(name)s.") % {"name": name}
                )


@dataclass(frozen=True)
class Tour:
    """A guided tour of one page.

    A view puts the tour in its template context, and ``{{ tour }}`` in the
    page's template renders it. Every tour is recorded under its name when it is
    made, so the system checks can report a name declared twice or a
    ``PAGE_TOURS_OVERRIDES`` key that names no tour.

    The fields after ``version`` are Driver.js's configuration options, named in
    snake_case and defaulting to the value Driver.js 1.10.2 itself uses. See
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
        allow_close: Whether a visitor can close the tour before its last step.
        allow_scroll: Whether the page can be scrolled while the tour shows.
        overlay_click_behavior: What clicking the overlay does: ``"close"`` the tour
            or go to the ``"nextStep"``.
        overlay_color: The colour of the overlay.
        overlay_opacity: The opacity of the overlay, from 0 to 1.
        smooth_scroll: Whether to scroll smoothly to each step's element.
        disable_active_interaction: Whether the highlighted element ignores clicks.
        allow_keyboard_control: Whether the arrow and escape keys move through and
            close the tour.
        advance_on_click: Whether clicking a step's element moves to the next step.
        wait_for_element: How long to wait for a step's element to appear, in
            milliseconds.
        stage_padding: The space around the highlighted element, in pixels.
        stage_radius: The corner radius of the highlight, in pixels.
        popover_offset: The distance between the popover and the element, in pixels.
        popover_class: A class added to every popover.
        show_buttons: The buttons the popover shows, from ``"next"``,
            ``"previous"`` and ``"close"``.
        disable_buttons: The buttons that show but cannot be pressed.
        show_progress: Whether the popover shows how far through the tour it is.
        progress_text: The progress text, with ``{{current}}`` and ``{{total}}``
            standing for the step's number and the number of steps.
        next_btn_text: The text of the next button, in the active language by
            default.
        prev_btn_text: The text of the previous button, in the active language by
            default.
        done_btn_text: The text of the button on the last step, in the active
            language by default.
        close_btn_label: The accessible name of the close button, in the active
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
    allow_close: bool = True
    allow_scroll: bool = True
    overlay_click_behavior: Literal["close", "nextStep"] = "close"
    overlay_color: str = "#000"
    overlay_opacity: float = 0.7
    smooth_scroll: bool = False
    disable_active_interaction: bool = False
    allow_keyboard_control: bool = True
    advance_on_click: bool = False
    wait_for_element: int = 0
    stage_padding: int = 10
    stage_radius: int = 5
    popover_offset: int = 10
    popover_class: str = ""
    show_buttons: tuple[Button, ...] = ("next", "previous", "close")
    disable_buttons: tuple[Button, ...] = ()
    show_progress: bool = False
    progress_text: str = PROGRESS_TEXT
    next_btn_text: str | Promise = NEXT_LABEL
    prev_btn_text: str | Promise = PREVIOUS_LABEL
    done_btn_text: str | Promise = DONE_LABEL
    close_btn_label: str | Promise = CLOSE_LABEL

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
                camel_case(option.name): getattr(played, option.name)
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

    def as_driver_steps(self) -> list[dict[str, str]]:
        """Convert the steps to the form Driver.js takes.

        Title and text are converted with ``str()`` when this is called, so the
        active language applies, and escaped because Driver.js writes them as HTML.

        Returns:
            One dict per step, in the declared order. A step that names an element
            carries an ``element`` key; the others do not.
        """
        driver_steps: list[dict[str, str]] = []
        for step in self.steps:
            driver_step: dict[str, str] = {
                "title": escape(str(step.title)),
                "text": escape(str(step.text)),
            }
            if step.element:
                driver_step["element"] = step.element
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
