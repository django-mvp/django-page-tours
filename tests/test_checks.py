"""Tests for page_tours.checks."""

import copy

import pytest
from django.apps import apps
from django.core import checks
from django.core.checks import run_checks
from django.core.management import call_command

from page_tours.parts import TourParts

REQUEST_PROCESSOR = "django.template.context_processors.request"


def check_ids():
    """Return the ids of the issues the system checks raise."""
    return {issue.id for issue in run_checks()}


class TestRequestContextProcessorCheck:
    """The warning for a project whose templates cannot see the request."""

    def test_it_warns_when_the_request_processor_is_missing(self, settings):
        """Without the processor a function-based view's tour cannot be found."""
        templates = copy.deepcopy(settings.TEMPLATES)
        templates[0]["OPTIONS"]["context_processors"].remove(REQUEST_PROCESSOR)
        settings.TEMPLATES = templates

        assert "page_tours.W001" in check_ids()

    def test_it_is_silent_when_the_request_processor_is_listed(self, settings):
        """A project with the processor gets no warning."""
        assert (
            REQUEST_PROCESSOR in settings.TEMPLATES[0]["OPTIONS"]["context_processors"]
        )

        assert "page_tours.W001" not in check_ids()

    def test_it_warns_when_no_django_templates_backend_is_configured(self, settings):
        """Another template engine alone cannot supply the processor."""
        settings.TEMPLATES = [
            {"BACKEND": "django.template.backends.dummy.TemplateStrings", "DIRS": []}
        ]

        assert "page_tours.W001" in check_ids()


def overrides_warnings():
    """Return the issues of the overrides check, by the key each is about."""
    return {issue.obj: issue for issue in run_checks() if issue.id == "page_tours.W002"}


class TestOverridesCheck:
    """The warning for a setting key that no routed view declares."""

    @pytest.fixture(autouse=True)
    def urls(self, settings):
        """Route the views that declare tours in the app-like test module."""
        settings.ROOT_URLCONF = "tests.urls_checks"

    def test_it_warns_for_a_key_no_routed_view_declares(self, settings):
        """A view that was renamed or moved leaves its key behind."""
        settings.PAGE_TOURS_OVERRIDES = {"tests.views.GoneView": None}

        assert set(overrides_warnings()) == {"tests.views.GoneView"}

    @pytest.mark.parametrize(
        "key",
        [
            "tests.views.UntouchedTourView",
            "tests.views.OverriddenTourView",
            "tests.views.overridden_function_view",
            "tests.views.OffTourView",
        ],
        ids=["class", "inherited by a routed subclass", "function view", "include"],
    )
    def test_it_is_silent_for_a_key_a_routed_view_declares(self, settings, key):
        """The name a routed view gives its tour is a name that exists."""
        settings.PAGE_TOURS_OVERRIDES = {key: None}

        assert overrides_warnings() == {}

    def test_it_is_silent_for_the_name_of_a_tour_given_through_as_view(self, settings):
        """A subclass that sets no tour is named by the class that declares one."""
        settings.ROOT_URLCONF = "tests.urls_checks_as_view"
        settings.PAGE_TOURS_OVERRIDES = {"tests.views.OverriddenTourView": None}

        assert overrides_warnings() == {}

    def test_it_warns_for_the_name_of_the_subclass_given_a_tour_through_as_view(
        self, settings
    ):
        """The subclass's own name is not the name its tour is remembered by."""
        settings.ROOT_URLCONF = "tests.urls_checks_as_view"
        settings.PAGE_TOURS_OVERRIDES = {"tests.views.OverriddenTourSubclassView": None}

        assert set(overrides_warnings()) == {"tests.views.OverriddenTourSubclassView"}

    def test_it_warns_once_for_each_key_that_is_not_declared(self, settings):
        """Each stale key is one warning, and the others stay quiet."""
        settings.PAGE_TOURS_OVERRIDES = {
            "tests.views.GoneView": None,
            "tests.views.AlsoGoneView": "tests.views.REPLACEMENT_TOUR",
            "tests.views.UntouchedTourView": None,
        }

        assert set(overrides_warnings()) == {
            "tests.views.GoneView",
            "tests.views.AlsoGoneView",
        }

    def test_it_is_silent_without_the_setting(self):
        """A project that changes no tour has nothing to go stale."""
        assert overrides_warnings() == {}

    def test_it_does_not_resolve_the_values(self, settings):
        """A bad value is reported once, when the project starts, not here."""
        settings.PAGE_TOURS_OVERRIDES = {"tests.views.UntouchedTourView": 42}

        assert overrides_warnings() == {}


class TestClassesCheck:
    """The warnings for classes configured for the wrong parts or in the wrong shape."""

    @staticmethod
    def issues(settings, value):
        """Return the issues raised for a PAGE_TOURS_CLASSES of this value."""
        settings.PAGE_TOURS_CLASSES = value
        return [
            issue for issue in run_checks() if issue.id.startswith("page_tours.W00")
        ]

    def test_an_unknown_part_gives_w002_naming_the_part_and_the_setting(self, settings):
        """The warning says which entry is wrong and where it was found."""
        found = self.issues(settings, {"footer": "x"})

        assert [issue.id for issue in found] == ["page_tours.W003"]
        assert "footer" in found[0].msg
        assert "PAGE_TOURS_CLASSES" in found[0].msg

    def test_the_hint_of_w002_lists_every_part(self, settings):
        """The developer is shown the parts they can use."""
        found = self.issues(settings, {"footer": "x"})

        assert all(part in found[0].hint for part in TourParts.parts)

    def test_a_value_that_is_not_a_string_gives_w003_naming_the_part(self, settings):
        """A list of class names is not a string of them."""
        found = self.issues(settings, {"box": ["card"]})

        assert [issue.id for issue in found] == ["page_tours.W004"]
        assert "box" in found[0].msg
        assert "PAGE_TOURS_CLASSES" in found[0].msg

    @pytest.mark.parametrize("value", ["box", ["box"], 3, None])
    def test_a_setting_that_is_not_a_dict_gives_w003(self, settings, value):
        """The setting itself must be a dict."""
        found = self.issues(settings, value)

        assert [issue.id for issue in found] == ["page_tours.W004"]
        assert "PAGE_TOURS_CLASSES" in found[0].msg

    def test_each_wrong_entry_gets_its_own_warning(self, settings):
        """Two mistakes are two warnings."""
        found = self.issues(settings, {"footer": "x", "box": 3})

        assert sorted(issue.id for issue in found) == [
            "page_tours.W003",
            "page_tours.W004",
        ]

    @pytest.mark.parametrize("value", [{}, {"box": "card", "close": ""}])
    def test_a_valid_setting_gives_nothing(self, settings, value):
        """Known parts with string values, an empty string included, are fine."""
        assert self.issues(settings, value) == []

    def test_no_setting_gives_nothing(self, settings):
        """The setting is optional."""
        del settings.PAGE_TOURS_CLASSES

        assert [i for i in run_checks() if i.id.startswith("page_tours.W00")] == []

    def test_both_are_warnings_so_the_checks_still_pass(self, settings):
        """A styling mistake never stops the project from running."""
        found = self.issues(settings, {"footer": "x", "box": 3})

        assert {issue.level for issue in found} == {checks.WARNING}
        settings.PAGE_TOURS_CLASSES = {"footer": "x", "box": 3}
        call_command("check")

    def test_an_apps_unknown_part_gives_w002_naming_the_part_and_the_app(
        self, settings, monkeypatch
    ):
        """An entry from a design system is reported with the app it came from."""
        settings.INSTALLED_APPS = [*settings.INSTALLED_APPS, "tests.design_system"]
        config = apps.get_app_config("design_system")
        monkeypatch.setattr(config, "page_tour_classes", {"footer": "x"})

        found = self.issues(settings, {})

        assert [issue.id for issue in found] == ["page_tours.W003"]
        assert "footer" in found[0].msg
        assert "design_system" in found[0].msg

    def test_an_apps_bad_value_gives_w003_naming_the_part_and_the_app(
        self, settings, monkeypatch
    ):
        """A value that is not a string is reported with the app it came from."""
        settings.INSTALLED_APPS = [*settings.INSTALLED_APPS, "tests.design_system"]
        config = apps.get_app_config("design_system")
        monkeypatch.setattr(config, "page_tour_classes", {"box": ["card"]})

        found = self.issues(settings, {})

        assert [issue.id for issue in found] == ["page_tours.W004"]
        assert "box" in found[0].msg
        assert "design_system" in found[0].msg

    @pytest.mark.parametrize("value", ["box", ["box"], 3, None])
    def test_an_apps_attribute_that_is_not_a_dict_gives_w003_naming_the_app(
        self, settings, monkeypatch, value
    ):
        """The attribute itself must be a dict."""
        settings.INSTALLED_APPS = [*settings.INSTALLED_APPS, "tests.design_system"]
        config = apps.get_app_config("design_system")
        monkeypatch.setattr(config, "page_tour_classes", value)

        found = self.issues(settings, {})

        assert [issue.id for issue in found] == ["page_tours.W004"]
        assert "design_system" in found[0].msg

    def test_a_valid_design_system_gives_nothing(self, settings):
        """An app with known parts and string values is fine."""
        settings.INSTALLED_APPS = [
            *settings.INSTALLED_APPS,
            "tests.design_system",
            "tests.other_design_system",
        ]

        assert self.issues(settings, {}) == []
