"""Declarations of a tour and its steps."""

from collections.abc import Callable, Sequence
from dataclasses import dataclass, replace
from functools import wraps
from inspect import iscoroutinefunction
from typing import Any, TypeVar

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.functional import Promise
from django.utils.html import escape
from django.utils.module_loading import import_string
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
        version: A whole number of 1 or more. Raise it when the tour has changed
            enough that people who saw it should see it again: a browser that saw
            another version plays it by itself once more.

    Raises:
        ImproperlyConfigured: If ``steps`` is empty or ``version`` is not a whole
            number of 1 or more.
    """

    steps: Sequence[TourStep]
    autoplay: bool = True
    version: int = 1

    def __post_init__(self):
        """Refuse a tour with no steps or a bad version, and freeze the steps."""
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

    @classmethod
    def for_page(cls, context: Any) -> "Tour | None":
        """Find the tour of the page whose own view is being rendered.

        A class-based view supplies its ``tour`` attribute through ``context["view"]``.
        A function-based view supplies the tour that ``with_tour`` put on the request.
        An error page has neither, so it has no tour.

        When the ``PAGE_TOURS_OVERRIDES`` setting names the tour, the replacement
        is returned in its place, or ``None`` when the setting turns it off. The
        replacement plays at the declared tour's version plus its own, less one,
        so a browser that saw the declared tour does not see the replacement by
        itself until the replacement's own version is raised. The setting is read
        on every call.

        Args:
            context: The template context, or any mapping with ``get``.

        Returns:
            The tour, or ``None`` when the page has none.

        Raises:
            ImproperlyConfigured: If the setting's entry for this tour is not valid.
        """
        tour = getattr(context.get("view"), "tour", None)
        if not isinstance(tour, cls):
            tour = getattr(context.get("request"), "page_tour", None)
        if not isinstance(tour, cls):
            return None
        overrides = getattr(settings, "PAGE_TOURS_OVERRIDES", {})
        name = tour_id(context)
        if name not in overrides:
            return tour
        replacement = resolve_override(name, overrides[name])
        if replacement is None:
            return None
        return replace(replacement, version=tour.version + replacement.version - 1)

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


def declaring_view_name(view_class: type) -> str:
    """Name a class-based view for the tour it declares or inherits.

    The name is the dotted path of the first class along the view's method
    resolution order whose own body declares ``tour``, so a subclass that
    inherits the tour shares its parent's name. When no class declares it,
    because it was set on the instance or through ``as_view``, it is the view
    class's own path.

    Args:
        view_class: The class of a class-based view.

    Returns:
        The dotted path of the class that names the view's tour.
    """
    for cls in view_class.__mro__:
        if "tour" in cls.__dict__:
            return f"{cls.__module__}.{cls.__qualname__}"
    return f"{view_class.__module__}.{view_class.__qualname__}"


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
        return declaring_view_name(type(view))
    return str(getattr(context.get("request"), "page_tour_view", ""))


def with_tour(tour: Tour) -> Callable[[F], F]:
    """Attach a tour to a function-based view, sync or async.

    The tour is on ``request.page_tour`` while the view runs, and the view's dotted
    path on ``request.page_tour_view``. Both are removed again if the view raises, so
    the error page that follows does not play the tour. The returned view carries
    the same path as ``page_tour_view``, so the system checks can name its tour
    without calling it.

    Args:
        tour: The tour to show on the page the view renders.

    Returns:
        A decorator for the view.
    """

    def decorator(view: F) -> F:
        # A view from as_view() is named by its class, and a callable with no name
        # of its own, such as a functools.partial, by its type.
        named = getattr(view, "view_class", view)
        module = getattr(named, "__module__", None) or type(named).__module__
        qualname = getattr(named, "__qualname__", None) or type(named).__qualname__
        path = f"{module}.{qualname}"

        if iscoroutinefunction(view):

            @wraps(view)
            async def async_wrapper(request, *args, **kwargs):
                request.page_tour = tour
                request.page_tour_view = path
                try:
                    return await view(request, *args, **kwargs)
                except BaseException:
                    del request.page_tour, request.page_tour_view
                    raise

            async_wrapper.page_tour_view = path  # type: ignore[attr-defined]
            return async_wrapper  # type: ignore[return-value]

        @wraps(view)
        def wrapper(request, *args, **kwargs):
            request.page_tour = tour
            request.page_tour_view = path
            try:
                return view(request, *args, **kwargs)
            except BaseException:
                del request.page_tour, request.page_tour_view
                raise

        wrapper.page_tour_view = path  # type: ignore[attr-defined]
        return wrapper  # type: ignore[return-value]

    return decorator
