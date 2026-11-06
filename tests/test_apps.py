"""Tests for page_tours.apps."""

from django.apps import apps
from django.urls import reverse


class TestPageToursConfig:
    """The app's configuration."""

    def test_the_app_is_installed_under_its_label(self):
        """The app registers under the label ``page_tours``."""
        config = apps.get_app_config("page_tours")
        assert config.name == "page_tours"

    def test_the_app_has_no_models(self):
        """Nothing is stored on the server."""
        assert list(apps.get_app_config("page_tours").get_models()) == []

    def test_a_page_with_a_tour_sets_no_cookie(self, client):
        """Whether a tour was seen is not kept in a cookie."""
        response = client.get(reverse("class-tour"))

        assert not response.cookies
