"""Tests for page_tours.parts."""

import pytest

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
