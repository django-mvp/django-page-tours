"""System checks for the project that installs the package."""

from django.conf import settings
from django.core import checks
from django.urls import get_resolver
from django.utils.translation import gettext_lazy as _

from page_tours.driver import declarations
from page_tours.parts import TourParts


@checks.register(checks.Tags.urls)
def check_overrides_name_declarations(app_configs, **kwargs):
    """Warn about each ``PAGE_TOURS_OVERRIDES`` key that names nothing declared.

    A key goes stale when the tour, hints or checklist it named are renamed or
    removed.
    The URLconf is loaded first, so every declaration in a routed view's module
    is known. Only the keys are read; the values are resolved once, at start-up.

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
    get_resolver().url_patterns  # noqa: B018 - importing the views declares their tours
    declared = declarations()
    return [
        checks.Warning(
            _(
                "No tour, hints or checklist are declared with the name %(name)s, so "
                "its entry in PAGE_TOURS_OVERRIDES changes nothing."
            )
            % {"name": name},
            hint=_(
                "A tour, hints or checklist that were renamed have a new name. "
                "Update the key to match."
            ),
            obj=name,
            id="page_tours.W002",
        )
        for name in overrides
        if name not in declared
    ]


@checks.register(checks.Tags.urls)
def check_declaration_names_are_unique(app_configs, **kwargs):
    """Warn about each name that declarations with different content share.

    Two declarations with one name share what a browser remembers about them and
    the entry ``PAGE_TOURS_OVERRIDES`` changes them by. Declarations of one class
    with the same content are one declaration, whatever their version, autoplay
    or the ids a checklist's app reports done, so one tour used on several
    views, or routed at two versions, is not reported. Declarations of different
    kinds under one name are always reported.

    Args:
        app_configs: The app configs being checked, supplied by Django.
        **kwargs: Other arguments Django passes to every check.

    Returns:
        One warning per name shared by declarations with different content, or an
        empty list.
    """
    get_resolver().url_patterns  # noqa: B018 - importing the views declares their tours
    return [
        checks.Warning(
            _(
                "%(count)d tours, sets of hints or checklists with different content "
                "are declared with the name %(name)s, so a browser that saw one "
                "counts them all as seen."
            )
            % {"count": len(contents), "name": name},
            hint=_(
                "Give each its own name. A reusable app names its declarations "
                "'<app_label>.<name>'."
            ),
            obj=name,
            id="page_tours.W005",
        )
        for name, found in declarations().items()
        if len(contents := distinct_contents(found)) > 1
    ]


def distinct_contents(found):
    """Return the different contents among declarations of one name.

    Contents are compared for equality, never hashed, because a declaration may
    hold a list, such as a tour's ``showButtons``.

    Args:
        found: The declarations under one name.

    Returns:
        Each different ``(class, content)`` pair once, in the order first found.
    """
    contents = []
    for item in found:
        content = (type(item), getattr(item, item.content_field))
        if content not in contents:
            contents.append(content)
    return contents


@checks.register()
def check_part_classes(app_configs, **kwargs):
    """Warn about classes configured for a part that does not exist or in a wrong shape.

    Wrong entries are skipped when a tour renders, so each is only a warning.

    Args:
        app_configs: The app configs being checked, supplied by Django.
        **kwargs: Other arguments Django passes to every check.

    Returns:
        A list with a ``page_tours.W003`` warning for each unknown part and a
        ``page_tours.W004`` warning for each value, or whole mapping, that is not
        what it should be.
    """
    issues = []
    for source, mapping in TourParts.sources():
        if not isinstance(mapping, dict):
            issues.append(
                checks.Warning(
                    _("%(source)s must be a dict from part to a string of class names.")
                    % {"source": source},
                    id="page_tours.W004",
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
                        id="page_tours.W003",
                    )
                )
            elif not isinstance(value, str):
                issues.append(
                    checks.Warning(
                        _("%(source)s gives '%(part)s' a value that is not a string.")
                        % {"source": source, "part": part},
                        hint=_("Write the class names as one string."),
                        id="page_tours.W004",
                    )
                )
    return issues
