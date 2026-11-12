"""Tests for page_tours.hints."""

import json
import re

import pytest
from django.core.exceptions import ImproperlyConfigured
from django.utils import translation
from django.utils.translation import gettext_lazy, pgettext

import page_tours
from page_tours import Beacon, Hint, Hints
from page_tours.hints import GOT_IT_LABEL
from tests import hints as hint_declarations

HINT = Hint(element="#menu", title="Title", description="Body")

SCRIPT = re.compile(
    r'<script id="page-tours-hints" type="application/json">(.*?)</script>',
    re.DOTALL,
)


def payload_of(html):
    """Return the payload a rendered declaration carries, parsed."""
    match = SCRIPT.fullmatch(str(html))
    assert match is not None
    return json.loads(match.group(1))


class TestHintsExports:
    """The package exports the three classes of a page's hints."""

    @pytest.mark.parametrize("name", ["Beacon", "Hint", "Hints"])
    def test_the_name_is_exported(self, name):
        """A developer imports it from the package."""
        assert name in page_tours.__all__
        assert getattr(page_tours, name).__name__ == name


class TestHints:
    """Declaring hints."""

    def test_hints_keep_the_name_they_are_declared_with(self):
        """The developer names the hints."""
        assert Hints(name="tests.named", hints=[HINT]).name == "tests.named"

    def test_hints_are_stored_as_a_tuple(self):
        """Declared hints cannot change later."""
        assert Hints(name="tests.tuple", hints=[HINT]).hints == (HINT,)

    def test_hints_are_at_version_one_unless_told_otherwise(self):
        """No version means 1."""
        assert Hints(name="tests.version", hints=[HINT]).version == 1

    def test_hints_without_hints_cannot_be_declared_without_the_argument(self):
        """The hints are required."""
        with pytest.raises(TypeError):
            Hints(name="tests.none")  # type: ignore[call-arg]

    def test_hints_with_an_empty_list_render_with_no_hints(self):
        """An empty list is declared and renders, and nothing is shown."""
        hints = Hints(name="tests.empty", hints=[])

        assert payload_of(str(hints))["config"]["hints"] == []

    @pytest.mark.parametrize("name", ["", "   ", None, 3])
    def test_a_name_that_is_not_a_non_blank_string_is_an_error(self, name):
        """A name is plain text with something in it."""
        with pytest.raises(ImproperlyConfigured):
            Hints(name=name, hints=[HINT])

    @pytest.mark.parametrize("version", [0, -1, 1.5, "2", True, None])
    def test_a_version_that_is_not_a_whole_number_of_one_or_more_is_an_error(
        self, version
    ):
        """Only 1, 2, 3 and so on are versions."""
        with pytest.raises(ImproperlyConfigured):
            Hints(name="tests.bad-version", hints=[HINT], version=version)

    def test_it_is_a_declaration_of_the_hints_kind(self):
        """The kind names the script element and the check's content field."""
        assert Hints.kind == "hints"
        assert Hints.content_field == "hints"


class TestHintsPayload:
    """Hints render as the element the package's script plays them from."""

    def test_the_payload_carries_its_kind_id_version_parts_and_config(self):
        """Nothing else reaches the browser."""
        payload = payload_of(hint_declarations.REPORT_HINTS)

        assert set(payload) == {"kind", "id", "version", "parts", "config"}
        assert payload["kind"] == "hints"
        assert payload["id"] == hint_declarations.REPORT_HINTS.name
        assert payload["version"] == 1

    def test_each_hint_carries_its_element_and_a_popover_with_title_and_text(self):
        """A hint is Driver.js's element and popover."""
        first, second = payload_of(hint_declarations.REPORT_HINTS)["config"]["hints"]

        assert first["element"] == "#first"
        assert first["popover"]["title"] == "First"
        assert first["popover"]["description"] == "Body one."
        assert second["element"] == "#second"

    def test_popover_fields_sit_flat_on_a_hint_and_arrive_in_the_popover(self):
        """Side is given on the hint and read from its popover."""
        (hint,) = payload_of(
            Hints(
                name="tests.flat",
                hints=[Hint(element="#a", title="T", description="D", side="left")],
            )
        )["config"]["hints"]

        assert hint["popover"]["side"] == "left"
        assert "side" not in hint

    def test_the_defaults_are_driverjs_own(self):
        """A declaration that sets nothing renders Driver.js's defaults."""
        config = payload_of(hint_declarations.REPORT_HINTS)["config"]
        config.pop("hints")
        button = config.pop("buttonText")

        assert config == {
            "popoverClass": "",
            "popoverOffset": 10,
            "overlay": False,
            "overlayColor": "#000",
            "overlayOpacity": 0.7,
        }
        assert button == str(GOT_IT_LABEL)

    def test_the_button_text_follows_the_active_language(self):
        """The default text is translated when the hints render."""
        with translation.override("de"):
            config = payload_of(hint_declarations.REPORT_HINTS)["config"]
            expected = pgettext("page hint control", "Got it")

        assert config["buttonText"] == expected != "Got it"

    def test_an_option_set_on_the_hints_reaches_the_config(self):
        """The hints' own options are in the config."""
        hints = Hints(name="tests.option", hints=[HINT], overlay=True, popoverOffset=3)

        config = payload_of(hints)["config"]

        assert config["overlay"] is True
        assert config["popoverOffset"] == 3

    def test_a_beacon_on_the_hints_arrives_in_the_config(self):
        """The beacon is a nested object, converted."""
        hints = Hints(
            name="tests.beacon", hints=[HINT], beacon=hint_declarations.BEACON
        )

        assert payload_of(hints)["config"]["beacon"] == {"side": "left", "offsetX": 4}

    def test_a_hints_without_a_beacon_leaves_it_out(self):
        """Driver.js's default beacon applies."""
        assert "beacon" not in payload_of(hint_declarations.REPORT_HINTS)["config"]

    def test_a_hints_own_options_reach_that_hint_only(self):
        """A beacon, button text and popover class on one hint stay on it."""
        hints = Hints(
            name="tests.own",
            hints=[
                Hint(
                    element="#a",
                    title="A",
                    description="D",
                    beacon=Beacon(animate=False),
                    buttonText="OK",
                    popoverClass="wide",
                ),
                Hint(element="#b", title="B", description="D"),
            ],
        )

        own, other = payload_of(hints)["config"]["hints"]

        assert own["beacon"] == {"animate": False}
        assert own["popover"]["buttonText"] == "OK"
        assert own["popover"]["popoverClass"] == "wide"
        assert "beacon" not in other
        assert set(other["popover"]) == {"title", "description"}

    def test_an_unset_hint_option_is_absent(self):
        """A null would override the hints' value in Driver.js."""
        (hint,) = payload_of(Hints(name="tests.unset", hints=[HINT]))["config"]["hints"]

        assert set(hint) == {"element", "popover"}
        assert set(hint["popover"]) == {"title", "description"}

    def test_html_in_a_title_passes_through_unescaped(self):
        """Driver.js writes the title as HTML."""
        hints = Hints(
            name="tests.markup",
            hints=[Hint(element="#a", title="<b>A</b>", description="<i>B</i>")],
        )

        (hint,) = payload_of(hints)["config"]["hints"]

        assert hint["popover"]["title"] == "<b>A</b>"
        assert hint["popover"]["description"] == "<i>B</i>"

    def test_the_id_is_present_when_set_and_absent_when_not(self):
        """An id names the hint in the browser's memory."""
        first, second = payload_of(hint_declarations.REPORT_HINTS)["config"]["hints"]

        assert first["id"] == "first"
        assert "id" not in second

    def test_the_version_is_the_declared_one(self):
        """The browser remembers the hints at their version."""
        hints = Hints(name="tests.v3", hints=[HINT], version=3)

        assert payload_of(hints)["version"] == 3

    def test_a_value_holding_markup_stays_inside_the_script_element(self):
        """A value cannot close the element it is carried in."""
        value = "</script><script>alert(1)</script>"
        hints = Hints(name="tests.escape", hints=[HINT], popoverClass=value)

        assert payload_of(hints)["config"]["popoverClass"] == value


class TestHintsOverrides:
    """``PAGE_TOURS_OVERRIDES`` changes hints by their name."""

    def test_a_replacement_renders_in_its_place(self, settings):
        """The replacement's hints are played."""
        settings.PAGE_TOURS_OVERRIDES = {
            hint_declarations.REPORT_HINTS.name: "tests.hints.REPLACEMENT_HINTS"
        }

        payload = payload_of(hint_declarations.REPORT_HINTS)

        elements = [hint["element"] for hint in payload["config"]["hints"]]
        assert elements == ["#other"]
        assert payload["id"] == hint_declarations.REPORT_HINTS.name

    def test_a_replacement_version_adds_to_the_original(self, settings):
        """A browser that saw the original sees the replacement after a version bump."""
        settings.PAGE_TOURS_OVERRIDES = {
            hint_declarations.REPORT_HINTS.name: (
                "tests.hints.REPLACEMENT_HINTS_VERSION_TWO"
            )
        }

        assert payload_of(hint_declarations.REPORT_HINTS)["version"] == 2

    def test_none_turns_the_hints_off(self, settings):
        """Nothing renders."""
        settings.PAGE_TOURS_OVERRIDES = {hint_declarations.REPORT_HINTS.name: None}

        assert str(hint_declarations.REPORT_HINTS) == ""

    def test_a_tour_as_the_replacement_is_refused(self, settings):
        """Hints can be replaced only by hints."""
        settings.PAGE_TOURS_OVERRIDES = {
            hint_declarations.REPORT_HINTS.name: "tests.hints.TOUR_AS_REPLACEMENT"
        }

        with pytest.raises(ImproperlyConfigured):
            str(hint_declarations.REPORT_HINTS)


class TestHintsSiteText:
    """``PAGE_TOURS_TEXT`` words every set of hints that does not word its own."""

    def test_the_setting_applies_to_hints_that_set_nothing(self, settings):
        """Hints left at the package's text take the site's."""
        settings.PAGE_TOURS_TEXT = {"hint": {"buttonText": "Understood"}}
        hints = Hints(name="tests.site-hints", hints=[Hint(element="#a", title="A")])

        assert hints.as_driver()["buttonText"] == "Understood"

    def test_the_hints_own_text_wins(self, settings):
        """Hints that word their button keep their wording."""
        settings.PAGE_TOURS_TEXT = {"hint": {"buttonText": "Understood"}}
        hints = Hints(
            name="tests.site-hints-own",
            hints=[Hint(element="#a", title="A")],
            buttonText="Okay",
        )

        assert hints.as_driver()["buttonText"] == "Okay"

    def test_a_hints_own_text_wins(self, settings):
        """A hint that words its button keeps its wording."""
        settings.PAGE_TOURS_TEXT = {"hint": {"buttonText": "Understood"}}
        hints = Hints(
            name="tests.site-hints-hint",
            hints=[Hint(element="#a", title="A", buttonText="Hint's own")],
        )

        config = hints.as_driver()

        assert config["hints"][0]["popover"]["buttonText"] == "Hint's own"
        assert config["buttonText"] == "Understood"

    def test_a_lazy_value_is_shown_in_the_active_language(self, settings):
        """A translated value is converted when the hints render."""
        settings.PAGE_TOURS_TEXT = {"hint": {"buttonText": gettext_lazy("Site ok")}}
        hints = Hints(name="tests.site-hints-lazy", hints=[Hint(element="#a")])

        assert hints.as_driver()["buttonText"] == "Site ok"
