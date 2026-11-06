"""Tests for page_tours.apps."""

from django.apps import apps


class TestPageToursConfig:
    """The app's configuration."""

    def test_the_app_is_installed_under_its_label(self):
        """The app registers under the label ``page_tours``."""
        config = apps.get_app_config("page_tours")
        assert config.name == "page_tours"
