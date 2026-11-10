"""Tests for page_tours.parts."""

import pytest
from django.apps import apps

from page_tours.parts import TourParts

PARTS = [
    "box",
    "title",
    "text",
    "progress",
    "previous",
    "next",
    "done",
    "close",
    "highlight",
]


class TestTourParts:
    """The parts of a shown step and the classes each one carries."""

    def test_the_parts_are_the_nine_of_a_shown_step(self):
        """The list of parts exists once, in this order."""
        assert list(TourParts.parts) == PARTS

    @pytest.mark.parametrize("part", PARTS)
    def test_a_part_is_named_page_tour_followed_by_the_part(self, part):
        """The documented name of a part is built from the part's key."""
        assert TourParts.name(part) == f"page-tour-{part}"

    def test_every_part_carries_only_its_name_with_no_setting(self, settings):
        """A project that configures nothing still gets every part named."""
        settings.PAGE_TOURS_CLASSES = {}

        assert TourParts.classes() == {part: [f"page-tour-{part}"] for part in PARTS}

    def test_every_part_carries_only_its_name_when_the_setting_is_absent(
        self, settings
    ):
        """The setting is optional."""
        del settings.PAGE_TOURS_CLASSES

        assert TourParts.classes() == {part: [f"page-tour-{part}"] for part in PARTS}

    def test_a_configured_part_carries_its_name_then_its_classes(self, settings):
        """The documented name comes first, the configured classes follow."""
        settings.PAGE_TOURS_CLASSES = {"box": "card shadow"}

        assert TourParts.classes()["box"] == ["page-tour-box", "card", "shadow"]

    def test_no_other_part_carries_the_configured_classes(self, settings):
        """Classes configured for one part stay on that part."""
        settings.PAGE_TOURS_CLASSES = {"box": "card shadow"}

        others = TourParts.classes()
        del others["box"]
        assert others == {
            part: [f"page-tour-{part}"] for part in PARTS if part != "box"
        }

    def test_classes_are_split_on_any_whitespace(self, settings):
        """Runs of spaces, tabs and newlines separate class names."""
        settings.PAGE_TOURS_CLASSES = {"title": "  a  b\tc\nd "}

        assert TourParts.classes()["title"] == ["page-tour-title", "a", "b", "c", "d"]

    def test_an_empty_string_leaves_the_name_only(self, settings):
        """An empty string is valid and adds no classes."""
        settings.PAGE_TOURS_CLASSES = {"close": ""}

        assert TourParts.classes()["close"] == ["page-tour-close"]

    def test_an_unknown_part_is_skipped(self, settings):
        """A part the package does not have is ignored, and the rest still apply."""
        settings.PAGE_TOURS_CLASSES = {"footer": "x", "box": "card"}

        classes = TourParts.classes()

        assert set(classes) == set(PARTS)
        assert classes["box"] == ["page-tour-box", "card"]

    @pytest.mark.parametrize("value", [None, 3, ["a", "b"], {"a": "b"}, b"card"])
    def test_a_value_that_is_not_a_string_is_skipped(self, settings, value):
        """Only a string of class names is a valid value."""
        settings.PAGE_TOURS_CLASSES = {"box": value, "title": "heading"}

        classes = TourParts.classes()

        assert classes["box"] == ["page-tour-box"]
        assert classes["title"] == ["page-tour-title", "heading"]

    @pytest.mark.parametrize("value", [None, "box", ["box"], 3])
    def test_a_setting_that_is_not_a_dict_is_skipped(self, settings, value):
        """A wrong setting never raises."""
        settings.PAGE_TOURS_CLASSES = value

        assert TourParts.classes() == {part: [f"page-tour-{part}"] for part in PARTS}

    def test_the_sources_name_the_setting_and_hold_its_mapping(self, settings):
        """The one source for now is the project setting."""
        settings.PAGE_TOURS_CLASSES = {"box": "card"}

        sources = list(TourParts.sources())

        assert len(sources) == 1
        source, mapping = sources[0]
        assert "PAGE_TOURS_CLASSES" in str(source)
        assert mapping == {"box": "card"}


DESIGN_SYSTEM = "tests.design_system"
OTHER_DESIGN_SYSTEM = "tests.other_design_system"


@pytest.fixture
def installed(settings):
    """Return a function that installs test apps after the project's own."""

    def install(*apps):
        settings.INSTALLED_APPS = [*settings.INSTALLED_APPS, *apps]

    return install


class TestTourPartsAppDefaults:
    """The classes an installed design system supplies as defaults."""

    def test_an_installed_apps_classes_apply_with_no_setting(self, settings, installed):
        """A design system styles the tour with nothing configured by the project."""
        settings.PAGE_TOURS_CLASSES = {}
        installed(DESIGN_SYSTEM)

        classes = TourParts.classes()

        assert classes["box"] == ["page-tour-box", "ds-box", "ds-raised"]
        assert classes["next"] == ["page-tour-next", "ds-button"]

    def test_a_part_the_app_leaves_out_carries_only_its_name(self, settings, installed):
        """The app's classes stay on the parts it names."""
        settings.PAGE_TOURS_CLASSES = {}
        installed(DESIGN_SYSTEM)

        assert TourParts.classes()["title"] == ["page-tour-title"]

    def test_the_setting_replaces_the_apps_classes_for_that_part_only(
        self, settings, installed
    ):
        """The project wins for a part it configures, and the app keeps the rest."""
        settings.PAGE_TOURS_CLASSES = {"box": "card"}
        installed(DESIGN_SYSTEM)

        classes = TourParts.classes()

        assert classes["box"] == ["page-tour-box", "card"]
        assert classes["next"] == ["page-tour-next", "ds-button"]

    def test_an_empty_string_in_the_setting_clears_the_apps_classes(
        self, settings, installed
    ):
        """An empty string is a configured value, so the app's classes give way."""
        settings.PAGE_TOURS_CLASSES = {"box": ""}
        installed(DESIGN_SYSTEM)

        assert TourParts.classes()["box"] == ["page-tour-box"]

    def test_the_first_of_two_apps_wins_for_a_part_both_supply(
        self, settings, installed
    ):
        """Installed order decides between design systems."""
        settings.PAGE_TOURS_CLASSES = {}
        installed(DESIGN_SYSTEM, OTHER_DESIGN_SYSTEM)

        assert TourParts.classes()["box"] == ["page-tour-box", "ds-box", "ds-raised"]

    def test_the_second_app_supplies_the_parts_the_first_does_not(
        self, settings, installed
    ):
        """A part the first app leaves out falls through to the second."""
        settings.PAGE_TOURS_CLASSES = {}
        installed(DESIGN_SYSTEM, OTHER_DESIGN_SYSTEM)

        assert TourParts.classes()["title"] == ["page-tour-title", "other-title"]

    def test_swapping_the_apps_swaps_the_winner(self, settings, installed):
        """The order of INSTALLED_APPS is the order of precedence."""
        settings.PAGE_TOURS_CLASSES = {}
        installed(OTHER_DESIGN_SYSTEM, DESIGN_SYSTEM)

        classes = TourParts.classes()

        assert classes["box"] == ["page-tour-box", "other-box"]
        assert classes["next"] == ["page-tour-next", "ds-button"]

    def test_no_app_and_no_setting_gives_names_only(self, settings):
        """Without a design system nothing changes."""
        settings.PAGE_TOURS_CLASSES = {}

        assert TourParts.classes() == {part: [f"page-tour-{part}"] for part in PARTS}

    def test_a_bad_entry_from_an_app_is_skipped(self, settings, installed, monkeypatch):
        """A wrong entry in an app's mapping is ignored, and the rest still apply."""
        settings.PAGE_TOURS_CLASSES = {}
        installed(DESIGN_SYSTEM)
        config = apps.get_app_config("design_system")
        monkeypatch.setattr(
            config, "page_tour_classes", {"footer": "x", "box": 3, "title": "ds-title"}
        )

        classes = TourParts.classes()

        assert set(classes) == set(PARTS)
        assert classes["box"] == ["page-tour-box"]
        assert classes["title"] == ["page-tour-title", "ds-title"]

    def test_the_sources_name_the_app_by_its_label(self, settings, installed):
        """An app is named in the sources so the checks can say where to look."""
        settings.PAGE_TOURS_CLASSES = {}
        installed(DESIGN_SYSTEM)

        sources = [str(source) for source, mapping in TourParts.sources()]

        assert len(sources) == 2
        assert "design_system" in sources[1]
