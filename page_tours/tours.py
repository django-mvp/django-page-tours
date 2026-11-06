"""Declarations of a tour and its steps."""

from collections.abc import Sequence
from dataclasses import dataclass

from django.core.exceptions import ImproperlyConfigured
from django.utils.functional import Promise
from django.utils.html import escape
from django.utils.translation import gettext_lazy as _

StrOrPromise = str | Promise


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

    title: StrOrPromise
    text: StrOrPromise
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

    Args:
        steps: The steps in the order they are shown. At least one.

    Raises:
        ImproperlyConfigured: If ``steps`` is empty.
    """

    steps: Sequence[TourStep]

    def __post_init__(self):
        """Refuse a tour with no steps and freeze the steps as a tuple."""
        if not self.steps:
            raise ImproperlyConfigured(_("A tour needs at least one step."))
        object.__setattr__(self, "steps", tuple(self.steps))

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
