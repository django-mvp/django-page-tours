"""Tests for page_tours.apps."""

import gettext
import re
from pathlib import Path

import pytest
from django.apps import apps
from django.core.exceptions import ImproperlyConfigured
from django.urls import reverse

import page_tours

LOCALE = Path(page_tours.__file__).parent / "locale"
SHIPPED_LANGUAGES = sorted(path.name for path in LOCALE.iterdir() if path.name != "en")


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


class TestPageToursConfigReady:
    """The project's tour overrides are checked when it starts."""

    def ready(self):
        """Run the app's start-up again, as Django does once."""
        apps.get_app_config("page_tours").ready()

    def test_it_is_silent_without_the_setting(self):
        """A project that changes no tour starts."""
        self.ready()

    def test_it_is_silent_with_a_valid_setting(self, settings):
        """A replacement and a tour turned off both start."""
        settings.PAGE_TOURS_OVERRIDES = {
            "app.page": "tests.views.REPLACEMENT_TOUR",
            "app.off": None,
        }

        self.ready()

    @pytest.mark.parametrize(
        "value",
        [42, "tests.views.missing_tour", "tests.views.NOT_A_TOUR"],
    )
    def test_it_refuses_a_bad_entry(self, settings, value):
        """A mistake in the setting stops the project at start-up."""
        settings.PAGE_TOURS_OVERRIDES = {"app.page": value}

        with pytest.raises(ImproperlyConfigured):
            self.ready()

    def test_it_refuses_a_replacement_module_whose_tour_is_invalid(self, settings):
        """The module's own error stops the project at start-up."""
        settings.PAGE_TOURS_OVERRIDES = {"app.page": "tests.invalid_tour.BROKEN_TOUR"}

        with pytest.raises(ImproperlyConfigured):
            self.ready()


class TestShippedTranslations:
    """The catalogues the package ships beside its English one."""

    @staticmethod
    def english_keys():
        """Return the key gettext stores each message of the English catalogue under."""
        text = (LOCALE / "en" / "LC_MESSAGES" / "django.po").read_text()
        entries = re.findall(r'(?:msgctxt "(.*)"\n)?msgid "(.+)"\n', text)
        return [
            f"{context}\x04{message}" if context else message
            for context, message in entries
        ]

    @pytest.mark.parametrize("language", SHIPPED_LANGUAGES)
    def test_every_message_is_translated(self, language):
        """The compiled catalogue translates every message the package marks."""
        with (LOCALE / language / "LC_MESSAGES" / "django.mo").open("rb") as compiled:
            catalogue = gettext.GNUTranslations(compiled)._catalog
        assert [key for key in self.english_keys() if not catalogue.get(key)] == []
