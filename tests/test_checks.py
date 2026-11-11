"""Tests for page_tours.checks."""

import pytest
from django.apps import apps
from django.core import checks
from django.core.checks import run_checks
from django.core.management import call_command

from page_tours.parts import TourParts
from page_tours.tours import Tour, TourStep
from tests import views

STEP = TourStep(title="Title", description="Body")


def warnings_of(check_id):
    """Return the issues one check raises, by the name each is about."""
    return {issue.obj: issue for issue in run_checks() if issue.id == check_id}


class TestOverridesCheck:
    """The warning for a setting key that names no declared tour."""

    def test_it_warns_for_a_key_that_names_no_tour(self, settings):
        """A tour that was renamed or removed leaves its key behind."""
        settings.PAGE_TOURS_OVERRIDES = {"app.gone": None}

        assert set(warnings_of("page_tours.W002")) == {"app.gone"}

    @pytest.mark.parametrize(
        "tour",
        [views.UNTOUCHED_TOUR, views.APP_TOUR, views.OWN_TOUR],
        ids=["class attribute", "function view context", "given through as_view"],
    )
    def test_it_is_silent_for_the_name_of_a_declared_tour(self, settings, tour):
        """However a view supplies its tour, the tour's name exists."""
        settings.PAGE_TOURS_OVERRIDES = {tour.name: None}

        assert warnings_of("page_tours.W002") == {}

    def test_it_is_silent_for_a_tour_no_view_routes_to(self, settings):
        """A tour is declared when it is made, routed or not."""
        tour = Tour(name="tests.unrouted", steps=[STEP])
        settings.PAGE_TOURS_OVERRIDES = {tour.name: None}

        assert warnings_of("page_tours.W002") == {}

    def test_it_warns_for_the_path_of_a_view(self, settings):
        """A view's dotted path is not a tour's name."""
        settings.PAGE_TOURS_OVERRIDES = {"tests.views.OverriddenTourView": None}

        assert set(warnings_of("page_tours.W002")) == {"tests.views.OverriddenTourView"}

    def test_it_warns_once_for_each_key_that_is_not_declared(self, settings):
        """Each stale key is one warning, and the others stay quiet."""
        settings.PAGE_TOURS_OVERRIDES = {
            "app.gone": None,
            "app.also-gone": "tests.views.REPLACEMENT_TOUR",
            views.UNTOUCHED_TOUR.name: None,
        }

        assert set(warnings_of("page_tours.W002")) == {
            "app.gone",
            "app.also-gone",
        }

    def test_it_is_silent_without_the_setting(self):
        """A project that changes no tour has nothing to go stale."""
        assert warnings_of("page_tours.W002") == {}

    def test_it_does_not_resolve_the_values(self, settings):
        """A bad value is reported once, when the project starts, not here."""
        settings.PAGE_TOURS_OVERRIDES = {views.UNTOUCHED_TOUR.name: 42}

        assert warnings_of("page_tours.W002") == {}


class TestUniqueNamesCheck:
    """The warning for tours with different steps declared with one name."""

    def test_it_warns_for_two_tours_with_one_name_and_different_steps(self):
        """They would share what a browser remembers and one override."""
        first = Tour(name="tests.clash", steps=[STEP])
        second = Tour(
            name="tests.clash", steps=[TourStep(title="Other", description="X")]
        )

        found = warnings_of("page_tours.W005")

        assert "tests.clash" in found
        assert found["tests.clash"].level == checks.WARNING
        assert first != second

    @pytest.mark.parametrize(
        "change", [{"version": 2}, {"autoplay": False}], ids=["version", "autoplay"]
    )
    def test_the_same_steps_at_another_version_or_autoplay_are_one_tour(self, change):
        """One tour routed at two versions is how a new version is tried out."""
        first = Tour(name="tests.versions", steps=[STEP])
        second = Tour(name="tests.versions", steps=[STEP], **change)

        assert "tests.versions" not in warnings_of("page_tours.W005")
        assert first != second

    def test_it_is_silent_for_one_tour_used_on_several_views(self):
        """A subclass, a second route or a second view sharing a tour is one tour."""
        assert views.APP_TOUR.name not in warnings_of("page_tours.W005")

    def test_it_is_silent_for_two_equal_declarations(self):
        """A tour made twice with the same values is still one tour."""
        first = Tour(name="tests.twins", steps=[STEP])
        second = Tour(name="tests.twins", steps=[STEP])

        assert "tests.twins" not in warnings_of("page_tours.W005")
        assert first == second

    def test_it_is_silent_for_tours_with_their_own_names(self):
        """Different names never clash."""
        first = Tour(name="tests.one", steps=[STEP])
        second = Tour(name="tests.two", steps=[STEP])

        found = warnings_of("page_tours.W005")

        assert {first.name, second.name}.isdisjoint(found)


class TestClassesCheck:
    """The warnings for classes configured for the wrong parts or in the wrong shape."""

    @staticmethod
    def issues(settings, value):
        """Return the issues raised for a PAGE_TOURS_CLASSES of this value."""
        settings.PAGE_TOURS_CLASSES = value
        return [
            issue
            for issue in run_checks()
            if issue.id in {"page_tours.W003", "page_tours.W004"}
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

        assert [
            i for i in run_checks() if i.id in {"page_tours.W003", "page_tours.W004"}
        ] == []

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
