"""System checks for the project that installs the package."""

from django.conf import settings
from django.core import checks
from django.utils.translation import gettext_lazy as _

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
