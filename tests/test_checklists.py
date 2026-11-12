"""Tests for page_tours.checklists."""

import json
import re
from dataclasses import replace

import pytest
from django.core.exceptions import ImproperlyConfigured
from django.utils import translation
from django.utils.translation import gettext_lazy, pgettext

import page_tours
from page_tours import Checklist, ChecklistItem, Offset, Tour, TourStep
from page_tours.parts import TourParts
from tests import checklists as checklist_declarations

ITEM = ChecklistItem(id="first", title="First")

SCRIPT = re.compile(
    r'<script id="page-tours-checklist" type="application/json">(.*?)</script>',
    re.DOTALL,
)


def payload_of(html):
    """Return the payload a rendered declaration carries, parsed."""
    match = SCRIPT.fullmatch(str(html))
    assert match is not None
    return json.loads(match.group(1))


class TestChecklistExports:
    """The package exports the classes of a page's checklist."""

    @pytest.mark.parametrize("name", ["Checklist", "ChecklistItem", "Offset"])
    def test_the_name_is_exported(self, name):
        """A developer imports it from the package."""
        assert name in page_tours.__all__
        assert getattr(page_tours, name).__name__ == name


class TestChecklist:
    """Declaring a checklist."""

    def test_a_checklist_keeps_the_name_it_is_declared_with(self):
        """The developer names the checklist."""
        assert Checklist(name="tests.named", items=[ITEM]).name == "tests.named"

    def test_the_items_are_stored_as_a_tuple(self):
        """Declared items cannot change later."""
        assert Checklist(name="tests.tuple", items=[ITEM]).items == (ITEM,)

    def test_the_completed_ids_are_stored_as_a_tuple(self):
        """The ids the app reports cannot change later."""
        checklist = Checklist(
            name="tests.completed-tuple", items=[ITEM], completed=["a"]
        )

        assert checklist.completed == ("a",)

    def test_a_checklist_is_at_version_one_unless_told_otherwise(self):
        """No version means 1."""
        assert Checklist(name="tests.version", items=[ITEM]).version == 1

    def test_a_checklist_without_items_cannot_be_declared_without_the_argument(self):
        """The items are required."""
        with pytest.raises(TypeError):
            Checklist(name="tests.none")  # type: ignore[call-arg]

    def test_a_checklist_with_an_empty_list_renders_with_no_items(self):
        """An empty list is declared and renders, and nothing is listed."""
        checklist = Checklist(name="tests.empty", items=[])

        assert payload_of(checklist)["config"]["items"] == []

    def test_a_checklist_is_keyword_only(self):
        """Every declaration names its arguments."""
        with pytest.raises(TypeError):
            Checklist("tests.positional", [ITEM])  # type: ignore[misc]

    @pytest.mark.parametrize("name", ["", "   ", None, 3])
    def test_a_name_that_is_not_a_non_blank_string_is_an_error(self, name):
        """A name is plain text with something in it."""
        with pytest.raises(ImproperlyConfigured):
            Checklist(name=name, items=[ITEM])

    @pytest.mark.parametrize("version", [0, -1, 1.5, "2", True, None])
    def test_a_version_that_is_not_a_whole_number_of_one_or_more_is_an_error(
        self, version
    ):
        """Only 1, 2, 3 and so on are versions."""
        with pytest.raises(ImproperlyConfigured):
            Checklist(name="tests.bad-version", items=[ITEM], version=version)

    def test_an_item_without_an_id_or_a_title_cannot_be_declared(self):
        """Both are required."""
        with pytest.raises(TypeError):
            ChecklistItem(id="only-an-id")  # type: ignore[call-arg]
        with pytest.raises(TypeError):
            ChecklistItem(title="only a title")  # type: ignore[call-arg]


class TestChecklistRendering:
    """What a rendered checklist carries."""

    def test_it_renders_the_element_the_script_plays_it_from(self):
        """The element is named for the kind."""
        assert SCRIPT.fullmatch(str(checklist_declarations.ONBOARDING)) is not None

    def test_the_payload_carries_exactly_its_kind_id_version_parts_and_config(self):
        """No autoplay: a checklist is not played from the start."""
        payload = payload_of(checklist_declarations.ONBOARDING)

        assert set(payload) == {"kind", "id", "version", "parts", "config"}
        assert payload["kind"] == "checklist"
        assert payload["id"] == checklist_declarations.ONBOARDING.name
        assert payload["version"] == 1
        assert payload["parts"] == TourParts.classes()

    def test_the_items_are_in_the_order_they_are_declared(self):
        """The visitor sees them in that order."""
        items = payload_of(checklist_declarations.ONBOARDING)["config"]["items"]

        assert [item["id"] for item in items] == ["welcome", "hints", "borrow"]

    def test_the_name_and_version_are_not_in_the_config(self):
        """They are the package's, not Driver.js's."""
        config = payload_of(checklist_declarations.ONBOARDING)["config"]

        assert "name" not in config
        assert "version" not in config


class TestChecklistItem:
    """What an item carries to Driver.js."""

    def test_an_item_with_a_link_carries_its_href(self):
        """The link reaches Driver.js as it is."""
        checklist = Checklist(
            name="tests.href",
            items=[ChecklistItem(id="docs", title="Docs", href="https://example.com/")],
        )

        item = payload_of(checklist)["config"]["items"][0]

        assert item["href"] == "https://example.com/"

    def test_an_item_with_nothing_set_carries_only_its_id_and_title(self):
        """An option left as None is left out, so Driver.js's own value applies."""
        item = payload_of(Checklist(name="tests.bare", items=[ITEM]))["config"]["items"]

        assert item == [{"id": "first", "title": "First"}]

    def test_an_item_description_reaches_driverjs(self):
        """The description is passed on as it is."""
        checklist = Checklist(
            name="tests.description",
            items=[ChecklistItem(id="a", title="A", description="<b>Body</b>")],
        )

        item = payload_of(checklist)["config"]["items"][0]

        assert item["description"] == "<b>Body</b>"

    @pytest.mark.parametrize("value", [True, False])
    def test_allow_manual_complete_on_an_item_reaches_driverjs(self, value):
        """A False is kept: it overrides the checklist's own."""
        checklist = Checklist(
            name="tests.item-manual",
            items=[ChecklistItem(id="a", title="A", allowManualComplete=value)],
        )

        item = payload_of(checklist)["config"]["items"][0]

        assert item["allowManualComplete"] is value

    def test_an_item_with_a_tour_carries_the_tours_payload(self):
        """The tour arrives in the shape the page's own tour does."""
        items = payload_of(checklist_declarations.ONBOARDING)["config"]["items"]
        tour = checklist_declarations.WELCOME_TOUR

        assert items[0]["tour"] == {
            "kind": "tour",
            "id": tour.name,
            "version": tour.version,
            "parts": TourParts.classes(),
            "config": tour.as_driver(),
            "autoplay": tour.autoplay,
        }

    def test_the_tour_is_not_a_driverjs_option_of_the_item(self):
        """Only the package's payload of the tour is sent, never the object."""
        item = checklist_declarations.ONBOARDING.items[0]

        assert "tour" not in item.as_driver()

    def test_an_item_without_a_tour_carries_none(self):
        """Only an item that has a tour has the key."""
        items = payload_of(checklist_declarations.ONBOARDING)["config"]["items"]

        assert "tour" not in items[1]


class TestChecklistCompleted:
    """What the app reports done."""

    def test_the_completed_ids_reach_driverjs(self):
        """The ids the app reports are in the config under their own name."""
        checklist = replace(checklist_declarations.ONBOARDING, completed=("borrow",))

        assert payload_of(checklist)["config"]["completed"] == ["borrow"]

    def test_nothing_is_completed_unless_the_app_reports_it(self):
        """The default is an empty list."""
        config = payload_of(checklist_declarations.ONBOARDING)["config"]

        assert config["completed"] == []


class TestChecklistOptions:
    """The options of the checklist itself."""

    def test_the_defaults_are_driverjs_own(self):
        """A checklist that sets nothing renders Driver.js's defaults."""
        with translation.override("en"):
            config = payload_of(checklist_declarations.ONBOARDING)["config"]
        config.pop("items")
        title = config.pop("title")
        progress = config.pop("progressText")

        assert config == {
            "launcherProgressText": "{{done}}/{{total}}",
            "position": "bottom-right",
            "launcher": True,
            "className": "",
            "allowManualComplete": False,
            "completed": [],
        }
        assert title == "Get started"
        assert progress == "{{done}} of {{total}}"

    def test_the_options_left_out_are_not_sent(self):
        """A null would override Driver.js's own value."""
        config = payload_of(checklist_declarations.ONBOARDING)["config"]

        for name in (
            "description",
            "launcherText",
            "completeTitle",
            "completeDescription",
            "completeLauncherText",
            "offset",
        ):
            assert name not in config

    def test_every_option_set_reaches_driverjs_unchanged(self):
        """Each option is in the config under Driver.js's name."""
        options = {
            "title": "Welcome",
            "description": "Start here",
            "launcherText": "Setup",
            "completeTitle": "All done",
            "completeDescription": "Nothing left",
            "completeLauncherText": "Finished",
            "progressText": "{{done}} / {{total}}",
            "launcherProgressText": "{{done}} of {{total}}",
            "position": "top-left",
            "launcher": False,
            "className": "mine",
            "allowManualComplete": True,
        }
        checklist = Checklist(name="tests.all-options", items=[ITEM], **options)

        config = payload_of(checklist)["config"]

        assert {name: config[name] for name in options} == options

    def test_an_offset_reaches_driverjs_as_an_object(self):
        """The offset is an object with the distances."""
        checklist = Checklist(
            name="tests.offset", items=[ITEM], offset=Offset(x=12, y=24)
        )

        assert payload_of(checklist)["config"]["offset"] == {"x": 12, "y": 24}

    def test_an_offset_with_one_distance_leaves_the_other_out(self):
        """The distance not set falls back to Driver.js's own."""
        checklist = Checklist(name="tests.offset-x", items=[ITEM], offset=Offset(x=5))

        assert payload_of(checklist)["config"]["offset"] == {"x": 5}


class TestChecklistTranslation:
    """The default text follows the language of the request."""

    def test_the_heading_and_progress_text_follow_the_active_language(self):
        """The defaults are translated when the checklist renders."""
        with translation.override("de"):
            config = payload_of(checklist_declarations.ONBOARDING)["config"]
            heading = pgettext("page checklist", "Get started")
            progress = pgettext("page checklist", "{{done}} of {{total}}")

        assert config["title"] == heading != "Get started"
        assert config["progressText"] == progress != "{{done}} of {{total}}"

    def test_the_launcher_progress_text_is_not_translated(self):
        """It is plain, as Driver.js has it."""
        with translation.override("de"):
            config = payload_of(checklist_declarations.ONBOARDING)["config"]

        assert config["launcherProgressText"] == "{{done}}/{{total}}"


class TestChecklistOverrides:
    """``PAGE_TOURS_OVERRIDES`` changes a checklist, or the tour of one item."""

    def test_a_replacement_renders_in_its_place(self, settings):
        """The replacement's items are played, under the original's name."""
        original = checklist_declarations.ONBOARDING
        settings.PAGE_TOURS_OVERRIDES = {
            original.name: "tests.checklists.REPLACEMENT_CHECKLIST"
        }

        payload = payload_of(original)

        assert [item["id"] for item in payload["config"]["items"]] == ["other"]
        assert payload["id"] == original.name

    def test_a_replacement_version_adds_to_the_original(self, settings):
        """A browser that saw the original sees the replacement after a bump."""
        original = checklist_declarations.ONBOARDING
        settings.PAGE_TOURS_OVERRIDES = {
            original.name: "tests.checklists.REPLACEMENT_CHECKLIST"
        }

        assert payload_of(original)["version"] == 1 + 3 - 1

    def test_a_replacement_plays_with_its_own_completed(self, settings):
        """What the app reports for the original does not carry over."""
        original = replace(
            checklist_declarations.ONBOARDING, completed=("borrow", "hints")
        )
        settings.PAGE_TOURS_OVERRIDES = {
            original.name: "tests.checklists.REPLACEMENT_CHECKLIST"
        }

        assert payload_of(original)["config"]["completed"] == ["other"]

    def test_none_turns_the_checklist_off(self, settings):
        """Nothing renders."""
        original = checklist_declarations.ONBOARDING
        settings.PAGE_TOURS_OVERRIDES = {original.name: None}

        assert str(original) == ""

    def test_a_tour_as_the_replacement_is_refused(self, settings):
        """A checklist can be replaced only by a checklist."""
        original = checklist_declarations.ONBOARDING
        settings.PAGE_TOURS_OVERRIDES = {original.name: "tests.checklists.WELCOME_TOUR"}

        with pytest.raises(ImproperlyConfigured):
            str(original)

    def test_a_replaced_tour_of_an_item_plays_the_replacement(self, settings):
        """The item's tour is the replacement, under the tour's own name."""
        tour = checklist_declarations.WELCOME_TOUR
        settings.PAGE_TOURS_OVERRIDES = {tour.name: "tests.checklists.REPLACEMENT_TOUR"}

        item = payload_of(checklist_declarations.ONBOARDING)["config"]["items"][0]

        assert item["tour"]["id"] == tour.name
        assert item["tour"]["config"]["steps"] == [
            step.as_driver() for step in checklist_declarations.REPLACEMENT_TOUR.steps
        ]

    def test_a_replaced_tour_of_an_item_plays_at_the_combined_version(self, settings):
        """The tour's version plus the replacement's, less one."""
        tour = checklist_declarations.WELCOME_TOUR
        settings.PAGE_TOURS_OVERRIDES = {tour.name: "tests.checklists.REPLACEMENT_TOUR"}

        item = payload_of(checklist_declarations.ONBOARDING)["config"]["items"][0]

        assert item["tour"]["version"] == tour.version + 4 - 1

    def test_a_tour_turned_off_leaves_its_item_out(self, settings):
        """No tour to play means no item for it."""
        settings.PAGE_TOURS_OVERRIDES = {checklist_declarations.WELCOME_TOUR.name: None}

        items = payload_of(checklist_declarations.ONBOARDING)["config"]["items"]

        assert [item["id"] for item in items] == ["hints", "borrow"]

    def test_the_tour_of_an_item_is_read_from_the_setting_every_time(self, settings):
        """A change to the setting is seen at once."""
        tour = checklist_declarations.WELCOME_TOUR
        settings.PAGE_TOURS_OVERRIDES = {tour.name: None}
        assert (
            len(payload_of(checklist_declarations.ONBOARDING)["config"]["items"]) == 2
        )

        settings.PAGE_TOURS_OVERRIDES = {}

        assert (
            len(payload_of(checklist_declarations.ONBOARDING)["config"]["items"]) == 3
        )

    def test_an_item_tour_of_the_wrong_class_is_refused_when_it_renders(self, settings):
        """A checklist cannot stand in for a tour."""
        tour = Tour(
            name="tests.checklists.wrong-class",
            steps=[TourStep(title="T", description="D")],
        )
        checklist = Checklist(
            name="tests.checklists.wrong-class-list",
            items=[ChecklistItem(id="a", title="A", tour=tour)],
        )
        settings.PAGE_TOURS_OVERRIDES = {
            tour.name: "tests.checklists.REPLACEMENT_CHECKLIST"
        }

        with pytest.raises(ImproperlyConfigured):
            str(checklist)


class TestChecklistSiteText:
    """``PAGE_TOURS_TEXT`` words every checklist that does not word its own."""

    def make(self, name, **options):
        """Return a checklist with one item."""
        return Checklist(
            name=name, items=[ChecklistItem(id="one", title="One")], **options
        )

    def test_the_setting_applies_to_a_checklist_that_sets_nothing(self, settings):
        """A checklist left at the package's text takes the site's."""
        settings.PAGE_TOURS_TEXT = {
            "checklist": {
                "title": "Your first steps",
                "progressText": "{{done}} finished",
                "launcherProgressText": "{{done}} / {{total}}",
            }
        }

        config = self.make("tests.site-list").as_driver()

        assert config["title"] == "Your first steps"
        assert config["progressText"] == "{{done}} finished"
        assert config["launcherProgressText"] == "{{done}} / {{total}}"

    def test_the_checklists_own_text_wins(self, settings):
        """A checklist that words its heading keeps its wording."""
        settings.PAGE_TOURS_TEXT = {"checklist": {"title": "Your first steps"}}

        config = self.make("tests.site-list-own", title="Setup").as_driver()

        assert config["title"] == "Setup"

    def test_a_lazy_value_is_shown_in_the_active_language(self, settings):
        """A translated value is converted when the checklist renders."""
        settings.PAGE_TOURS_TEXT = {"checklist": {"title": gettext_lazy("Site title")}}

        config = self.make("tests.site-list-lazy").as_driver()

        assert config["title"] == "Site title"
        assert type(config["title"]) is str

    def test_a_tour_in_an_item_takes_the_tour_text(self, settings):
        """The tour of an item is a tour, so the tour's text applies."""
        settings.PAGE_TOURS_TEXT = {"tour": {"doneBtnText": "Finish"}}
        tour = Tour(name="tests.site-list-tour", steps=[TourStep(title="One")])
        checklist = Checklist(
            name="tests.site-list-item-tour",
            items=[ChecklistItem(id="tour", title="Tour", tour=tour)],
        )

        config = checklist.as_driver()

        assert config["items"][0]["tour"]["config"]["doneBtnText"] == "Finish"
