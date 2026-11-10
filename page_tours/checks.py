"""System checks for the project that installs the package."""

from django.conf import settings
from django.core import checks
from django.urls import URLPattern, URLResolver, get_resolver
from django.utils.translation import gettext_lazy as _

from page_tours.parts import TourParts
from page_tours.tours import Tour, declaring_view_name

REQUEST_PROCESSOR = "django.template.context_processors.request"
DJANGO_TEMPLATES = "django.template.backends.django.DjangoTemplates"


@checks.register()
def check_request_context_processor(app_configs, **kwargs):
    """Warn when no Django template engine puts the request in the context.

    Without the request, a function-based view's tour cannot be found.

    Args:
        app_configs: The app configs being checked, supplied by Django.
        **kwargs: Other arguments Django passes to every check.

    Returns:
        A list with one warning, or an empty list when the processor is listed.
    """
    for engine in settings.TEMPLATES:
        processors = engine.get("OPTIONS", {}).get("context_processors", [])
        if engine["BACKEND"] == DJANGO_TEMPLATES and REQUEST_PROCESSOR in processors:
            return []
    return [
        checks.Warning(
            _(
                "Tours on function-based views are not shown because "
                "'django.template.context_processors.request' is not in the "
                "context_processors of any DjangoTemplates backend."
            ),
            hint=_("Add it to the 'context_processors' option of TEMPLATES."),
            id="page_tours.W001",
        )
    ]


def declared_tour_names(patterns) -> set[str]:
    """Name every tour the routed views declare, as ``tour_id`` names them.

    A function-based view is named by ``with_tour``. A class-based view that
    carries a tour, declared on the class or given through ``as_view``, is named
    by the class that declares it.

    Args:
        patterns: URL patterns and resolvers, such as ``get_resolver().url_patterns``.

    Returns:
        The names of the tours of every view the patterns route to, including
        views under ``include()``.
    """
    names: set[str] = set()
    for pattern in patterns:
        if isinstance(pattern, URLResolver):
            names |= declared_tour_names(pattern.url_patterns)
        elif isinstance(pattern, URLPattern):
            callback = pattern.callback
            view_class = getattr(callback, "view_class", None)
            if hasattr(callback, "page_tour_view"):
                names.add(callback.page_tour_view)
            elif view_class is not None and any(
                isinstance(tour, Tour)
                for tour in (
                    getattr(callback, "view_initkwargs", {}).get("tour"),
                    getattr(view_class, "tour", None),
                )
            ):
                names.add(declaring_view_name(view_class))
    return names


@checks.register(checks.Tags.urls)
def check_overrides_name_declared_tours(app_configs, **kwargs):
    """Warn about each ``PAGE_TOURS_OVERRIDES`` key that no routed view declares.

    A key goes stale when the view it named is renamed, moved or removed. Only
    the keys are read; the values are resolved once, at start-up.

    Args:
        app_configs: The app configs being checked, supplied by Django.
        **kwargs: Other arguments Django passes to every check.

    Returns:
        One warning per stale key, or an empty list when none is stale or the
        setting is absent.
    """
    overrides = getattr(settings, "PAGE_TOURS_OVERRIDES", {})
    if not overrides:
        return []
    declared = declared_tour_names(get_resolver().url_patterns)
    return [
        checks.Warning(
            _(
                "No routed view declares the tour %(name)s, so its entry in "
                "PAGE_TOURS_OVERRIDES changes nothing."
            )
            % {"name": name},
            hint=_(
                "A view that was renamed or moved gives its tour a new name. "
                "Update the key to match."
            ),
            obj=name,
            id="page_tours.W002",
        )
        for name in overrides
        if name not in declared
    ]


@checks.register()
def check_part_classes(app_configs, **kwargs):
    """Warn about classes configured for a part that does not exist or in a wrong shape.

    Wrong entries are skipped when a tour renders, so each is only a warning.

    Args:
        app_configs: The app configs being checked, supplied by Django.
        **kwargs: Other arguments Django passes to every check.

    Returns:
        A list with a ``page_tours.W002`` warning for each unknown part and a
        ``page_tours.W003`` warning for each value, or whole mapping, that is not
        what it should be.
    """
    issues = []
    for source, mapping in TourParts.sources():
        if not isinstance(mapping, dict):
            issues.append(
                checks.Warning(
                    _("%(source)s must be a dict from part to a string of class names.")
                    % {"source": source},
                    id="page_tours.W003",
                )
            )
            continue
        for part, value in mapping.items():
            if part not in TourParts.parts:
                issues.append(
                    checks.Warning(
                        _("%(source)s names '%(part)s', which is not a part of a tour.")
                        % {"source": source, "part": part},
                        hint=_("The parts are: %(parts)s.")
                        % {"parts": ", ".join(TourParts.parts)},
                        id="page_tours.W002",
                    )
                )
            elif not isinstance(value, str):
                issues.append(
                    checks.Warning(
                        _("%(source)s gives '%(part)s' a value that is not a string.")
                        % {"source": source, "part": part},
                        hint=_("Write the class names as one string."),
                        id="page_tours.W003",
                    )
                )
    return issues
