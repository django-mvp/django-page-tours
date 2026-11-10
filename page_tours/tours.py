"""Declarations of a tour and its steps."""

import copy
import weakref
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.functional import Promise
from django.utils.html import escape
from django.utils.module_loading import import_string
from django.utils.translation import gettext_lazy as _

# Every tour declared so far, by name. The references are weak, so a tour that
# nothing refers to any more is no longer declared.
_declared: dict[str, list[weakref.ref["Tour"]]] = {}


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

    Every tour is recorded under its name when it is made, so the system checks
    can report a name declared twice or a ``PAGE_TOURS_OVERRIDES`` key that names
    no tour.

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

    Raises:
        ImproperlyConfigured: If ``name`` is not a string with something in it,
            ``steps`` is empty or ``version`` is not a whole number of 1 or more.
    """

    name: str
    steps: Sequence[TourStep]
    autoplay: bool = True
    version: int = 1

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
        _declared.setdefault(self.name, []).append(weakref.ref(self))

    @classmethod
    def for_page(cls, context: Any) -> "Tour | None":
        """Find the tour of the page whose own view is being rendered.

        A class-based view supplies its ``tour`` attribute through ``context["view"]``.
        A function-based view passes the tour in its context under ``tour``. An
        error page has neither, so it has no tour.

        When the ``PAGE_TOURS_OVERRIDES`` setting names the tour, the replacement
        is returned in its place, or ``None`` when the setting turns it off. The
        replacement keeps the declared tour's name, and plays at the declared
        tour's version plus its own, less one, so a browser that saw the declared
        tour does not see the replacement by itself until the replacement's own
        version is raised. The setting is read on every call.

        Args:
            context: The template context, or any mapping with ``get``.

        Returns:
            The tour, or ``None`` when the page has none.

        Raises:
            ImproperlyConfigured: If the setting's entry for this tour is not valid.
        """
        tour = getattr(context.get("view"), "tour", None)
        if not isinstance(tour, cls):
            tour = context.get("tour")
        if not isinstance(tour, cls):
            return None
        overrides = getattr(settings, "PAGE_TOURS_OVERRIDES", {})
        if tour.name not in overrides:
            return tour
        replacement = resolve_override(tour.name, overrides[tour.name])
        if replacement is None:
            return None
        # A copy is not made through __init__, so the tour a page plays is not
        # recorded as a second tour declared under the declared tour's name.
        played = copy.copy(replacement)
        object.__setattr__(played, "name", tour.name)
        object.__setattr__(played, "version", tour.version + replacement.version - 1)
        return played

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
        alive = [tour for ref in refs if (tour := ref()) is not None]
        if alive:
            _declared[name] = [weakref.ref(tour) for tour in alive]
            tours[name] = alive
        else:
            del _declared[name]
    return tours
