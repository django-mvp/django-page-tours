"""Django application configuration."""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class PageToursConfig(AppConfig):
    """Django application configuration for django-page-tours."""

    name = "page_tours"
    verbose_name = _("Page tours")

    def ready(self):
        """Register the system checks."""
        from page_tours import checks  # noqa: F401
