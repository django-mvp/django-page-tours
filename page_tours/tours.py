"""Declarations of a tour and its steps."""

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from functools import wraps
from inspect import iscoroutinefunction
from typing import Any, TypeVar

from django.core.exceptions import ImproperlyConfigured
from django.utils.functional import Promise
from django.utils.html import escape
from django.utils.translation import gettext_lazy as _

F = TypeVar("F", bound=Callable[..., Any])


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

    Args:
        steps: The steps in the order they are shown. At least one.
        autoplay: Whether the tour plays by itself the first time a browser opens
            the page.

    Raises:
        ImproperlyConfigured: If ``steps`` is empty.
    """

    steps: Sequence[TourStep]
    autoplay: bool = True

    def __post_init__(self):
        """Refuse a tour with no steps and freeze the steps as a tuple."""
        if not self.steps:
            raise ImproperlyConfigured(_("A tour needs at least one step."))
        object.__setattr__(self, "steps", tuple(self.steps))

    @classmethod
    def for_page(cls, context: Any) -> "Tour | None":
        """Find the tour of the page whose own view is being rendered.

        A class-based view supplies its ``tour`` attribute through ``context["view"]``.
        A function-based view supplies the tour that ``with_tour`` put on the request.
        An error page has neither, so it has no tour.

        Args:
            context: The template context, or any mapping with ``get``.

        Returns:
            The tour, or ``None`` when the page has none.
        """
        tour = getattr(context.get("view"), "tour", None)
        if not isinstance(tour, cls):
            tour = getattr(context.get("request"), "page_tour", None)
        return tour if isinstance(tour, cls) else None

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


def tour_id(context: Any) -> str:
    """Name the tour of the page being rendered, for remembering that it was seen.

    A class-based view is named by the class that declares ``tour`` itself, so a
    subclass that inherits the tour shares its parent's id. When no class declares
    it, because it was set on the instance or through ``as_view``, the view's own
    class gives the name. A function-based view is named by ``with_tour``.

    Call it only for a page whose ``Tour.for_page(context)`` is not ``None``.

    Args:
        context: The template context, or any mapping with ``get``.

    Returns:
        The dotted path of the view that declares the tour.
    """
    view = context.get("view")
    if isinstance(getattr(view, "tour", None), Tour):
        for cls in type(view).__mro__:
            if "tour" in cls.__dict__:
                return f"{cls.__module__}.{cls.__qualname__}"
        return f"{type(view).__module__}.{type(view).__qualname__}"
    return str(context["request"].page_tour_view)


def with_tour(tour: Tour) -> Callable[[F], F]:
    """Attach a tour to a function-based view, sync or async.

    The tour is on ``request.page_tour`` while the view runs, and the view's dotted
    path on ``request.page_tour_view``. Both are removed again if the view raises, so
    the error page that follows does not play the tour.

    Args:
        tour: The tour to show on the page the view renders.

    Returns:
        A decorator for the view.
    """

    def decorator(view: F) -> F:
        view_path = f"{view.__module__}.{view.__qualname__}"

        if iscoroutinefunction(view):

            @wraps(view)
            async def async_wrapper(request, *args, **kwargs):
                request.page_tour = tour
                request.page_tour_view = view_path
                try:
                    return await view(request, *args, **kwargs)
                except BaseException:
                    del request.page_tour, request.page_tour_view
                    raise

            return async_wrapper  # type: ignore[return-value]

        @wraps(view)
        def wrapper(request, *args, **kwargs):
            request.page_tour = tour
            request.page_tour_view = view_path
            try:
                return view(request, *args, **kwargs)
            except BaseException:
                del request.page_tour, request.page_tour_view
                raise

        return wrapper  # type: ignore[return-value]

    return decorator
