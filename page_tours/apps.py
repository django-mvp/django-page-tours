"""Django application configuration."""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class PageToursConfig(AppConfig):
    """Django application configuration for django-page-tours."""

    name = "page_tours"
    verbose_name = _("Page tours")

    def ready(self):
        """Register the system checks and refuse a bad PAGE_TOURS_OVERRIDES.

        Raises:
            ImproperlyConfigured: If an entry of the setting cannot be resolved.
        """
        from page_tours import checks  # noqa: F401
        from page_tours.tours import tour_overrides

        tour_overrides()
