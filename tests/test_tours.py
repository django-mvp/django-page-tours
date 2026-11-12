"""Tests for page_tours.tours."""

import gc
import json
import re
from dataclasses import replace

import pytest
from django.core.exceptions import ImproperlyConfigured
from django.template import Context, Template
from django.urls import reverse
from django.utils import translation
from django.utils.safestring import SafeString
from django.utils.translation import gettext, gettext_lazy

from page_tours import driver as driver_module
from page_tours.driver import declaration_overrides, declarations, resolve_override
from page_tours.parts import TourParts
from page_tours.tours import Tour, TourStep
from tests import views
from tests.settings_site_text import PAGE_TOURS_TEXT as SITE_TEXT
from tests.site_text import run_with_site_text

STEP = TourStep(title="Title", description="Body")


class TestTourStep:
    """Declaring a step of a tour."""

    def test_the_element_is_optional(self):
        """A step may name no element."""
        assert TourStep(title="Title", description="Body").element == ""


class TestTour:
    """Declaring a tour."""

    def test_a_tour_keeps_the_name_it_is_declared_with(self):
        """The developer names the tour."""
        assert Tour(name="app.book", steps=[STEP]).name == "app.book"

    def test_a_tour_without_a_name_is_an_error(self):
        """The name is required."""
        with pytest.raises(TypeError):
            Tour(steps=[STEP])  # type: ignore[call-arg]

    @pytest.mark.parametrize("name", ["", "   ", "\n\t", None, 3, gettext_lazy("x")])
    def test_a_name_that_is_not_a_non_blank_string_is_an_error(self, name):
        """A name is plain text with something in it."""
        with pytest.raises(ImproperlyConfigured):
            Tour(name=name, steps=[STEP])

    def test_a_tour_without_steps_is_an_error(self):
        """A tour needs at least one step."""
        with pytest.raises(ImproperlyConfigured):
            Tour(name="test", steps=[])

    def test_steps_are_stored_as_a_tuple(self):
        """A declared tour cannot change later."""
        step = TourStep(title="Title", description="Body")

        tour = Tour(name="test", steps=[step])

        assert tour.steps == (step,)

    def test_a_tour_plays_by_itself_unless_told_otherwise(self):
        """Autoplay is on by default."""
        assert (
            Tour(
                name="test", steps=[TourStep(title="Title", description="Body")]
            ).autoplay
            is True
        )

    def test_a_tour_is_at_version_one_unless_told_otherwise(self):
        """A tour declared without a version has version 1."""
        assert (
            Tour(
                name="test", steps=[TourStep(title="Title", description="Body")]
            ).version
            == 1
        )

    def test_a_tour_keeps_the_version_it_is_declared_with(self):
        """The developer sets the version."""
        tour = Tour(
            name="test", steps=[TourStep(title="Title", description="Body")], version=3
        )

        assert tour.version == 3

    @pytest.mark.parametrize("version", [0, -1, 1.5, "2", True, None])
    def test_a_version_that_is_not_a_whole_number_of_one_or_more_is_an_error(
        self, version
    ):
        """Only 1, 2, 3 and so on are versions."""
        with pytest.raises(ImproperlyConfigured):
            Tour(
                name="test",
                steps=[TourStep(title="Title", description="Body")],
                version=version,
            )


class TestTourDriverOptions:
    """A tour's Driver.js options reach the page under Driver.js's own names."""

    def test_a_field_arrives_in_the_rendered_options(self):
        """``overlayOpacity`` set on a tour is in the rendered options."""
        tour = Tour(name="tests.options-field", steps=[STEP], overlayOpacity=0.4)

        assert payload_of(tour)["config"]["overlayOpacity"] == 0.4

    def test_a_tour_that_sets_nothing_renders_driverjs_defaults(self):
        """The defaults of the fields are the defaults of Driver.js 1.11.0."""
        options = payload_of(views.CLASS_TOUR)["config"]
        options.pop("steps")

        assert options == {
            "animate": True,
            "duration": 400,
            "allowClose": True,
            "allowScroll": True,
            "overlayClickBehavior": "close",
            "overlayColor": "#000",
            "overlayOpacity": 0.7,
            "smoothScroll": False,
            "disableActiveInteraction": False,
            "allowKeyboardControl": True,
            "advanceOn": False,
            "waitForElement": 0,
            "stagePadding": 10,
            "stageRadius": 5,
            "popoverOffset": 10,
            "popoverClass": "",
            "showButtons": ["next", "previous", "close"],
            "disableButtons": [],
            "showProgress": False,
            "progressText": "{{current}} of {{total}}",
            "nextBtnText": "Next",
            "prevBtnText": "Previous",
            "doneBtnText": "Done",
            "closeBtnLabel": "Close",
        }

    def test_the_options_leave_out_what_is_not_a_driverjs_option(self):
        """Name, steps, autoplay and version are the package's, not Driver.js's."""
        options = payload_of(views.CLASS_TOUR)["config"]

        assert not {"name", "autoplay", "version"} & set(options)

    def test_allowed_elements_arrive_as_a_list(self):
        """The selectors of the elements left usable are carried as a JSON list."""
        tour = Tour(
            name="tests.options-allowed", steps=[STEP], allowedElements=("#search",)
        )

        assert payload_of(tour)["config"]["allowedElements"] == ["#search"]

    def test_a_tuple_of_buttons_arrives_as_a_list(self):
        """The buttons shown are carried as a JSON list."""
        tour = Tour(name="tests.options-buttons", steps=[STEP], showButtons=("next",))

        assert payload_of(tour)["config"]["showButtons"] == ["next"]

    def test_the_labels_follow_the_active_language(self):
        """The four labels are translated when the tour renders."""
        with translation.override("de"):
            options = payload_of(views.CLASS_TOUR)["config"]

        assert options["nextBtnText"] == "Weiter <i>»</i>"
        assert options["prevBtnText"] == "Zurück"
        assert options["doneBtnText"] == "Fertig"
        assert options["closeBtnLabel"] == "Schließen & beenden"

    def test_a_label_set_on_the_tour_replaces_the_translated_one(self):
        """A tour names its own label, and it is passed as written."""
        tour = Tour(name="tests.options-label", steps=[STEP], nextBtnText="Go <b>")

        with translation.override("de"):
            assert payload_of(tour)["config"]["nextBtnText"] == "Go <b>"

    def test_a_value_holding_markup_stays_inside_the_script_element(self):
        """A value cannot close the element it is carried in."""
        value = "</script><script>alert(1)</script>"
        tour = Tour(name="tests.options-markup", steps=[STEP], popoverClass=value)

        assert payload_of(tour)["config"]["popoverClass"] == value


class TestTourAsDriverSteps:
    """Converting a tour to the steps Driver.js takes."""

    def test_steps_come_out_in_the_declared_order(self):
        """One dict per step, in the order declared."""
        tour = Tour(
            name="test",
            steps=[
                TourStep(title="First", description="One"),
                TourStep(title="Second", description="Two"),
                TourStep(title="Third", description="Three"),
            ],
        )

        steps = tour.as_driver()["steps"]

        assert [step["popover"]["title"] for step in steps] == [
            "First",
            "Second",
            "Third",
        ]

    def test_the_element_key_is_present_only_for_a_step_that_names_one(self):
        """A step with no element has no element key."""
        tour = Tour(
            name="test",
            steps=[
                TourStep(title="Attached", description="One", element="#menu"),
                TourStep(title="Floating", description="Two"),
            ],
        )

        attached, floating = tour.as_driver()["steps"]

        assert attached["element"] == "#menu"
        assert floating["element"] == ""

    def test_a_step_option_arrives_under_driverjs_name_where_driverjs_reads_it(self):
        """Step-level options sit on the step, popover options inside ``popover``."""
        tour = Tour(
            name="test",
            steps=[
                TourStep(
                    element="#menu",
                    title="Title",
                    description="Body",
                    advanceOn=("click", "keydown"),
                    waitForElement=500,
                    side="left",
                    popoverClass="wide",
                    showButtons=("next",),
                )
            ],
        )

        (step,) = tour.as_driver()["steps"]

        assert step == {
            "element": "#menu",
            "advanceOn": ["click", "keydown"],
            "waitForElement": 500,
            "popover": {
                "title": "Title",
                "description": "Body",
                "side": "left",
                "popoverClass": "wide",
                "showButtons": ["next"],
            },
        }

    def test_the_remaining_step_options_arrive_where_driverjs_reads_them(self):
        """Allowed elements and skipping sit on the step, the close label in ``popover``."""
        tour = Tour(
            name="test",
            steps=[
                TourStep(
                    element="#menu",
                    description="Body",
                    allowedElements=("#search", ".help"),
                    skipMissingElement=False,
                    closeBtnLabel="Stop the tour",
                )
            ],
        )

        (step,) = tour.as_driver()["steps"]

        assert step == {
            "element": "#menu",
            "allowedElements": ["#search", ".help"],
            "skipMissingElement": False,
            "popover": {"description": "Body", "closeBtnLabel": "Stop the tour"},
        }

    def test_an_option_left_as_none_is_absent_so_the_tours_value_applies(self):
        """A null in the step would override the tour's value in Driver.js."""
        tour = Tour(name="test", steps=[TourStep(title="Title", description="Body")])

        (step,) = tour.as_driver()["steps"]

        assert step == {
            "element": "",
            "popover": {"title": "Title", "description": "Body"},
        }

    def test_title_and_description_are_passed_as_they_are(self):
        """HTML in a title or description reaches Driver.js unescaped."""
        tour = Tour(
            name="test", steps=[TourStep(title="<b>A</b>", description="<i>B</i>")]
        )

        (step,) = tour.as_driver()["steps"]

        assert step["popover"]["title"] == "<b>A</b>"
        assert step["popover"]["description"] == "<i>B</i>"

    def test_a_lazy_title_is_translated_into_the_active_language(self):
        """The language active when the steps are built decides the text."""
        tour = Tour(
            name="test", steps=[TourStep(title=gettext_lazy("Yes"), description="Body")]
        )

        with translation.override("de"):
            (step,) = tour.as_driver()["steps"]
            expected = str(gettext("Yes"))

        assert step["popover"]["title"] == expected


STEPS_SCRIPT = re.compile(
    r'<script id="page-tours-tour" type="application/json">(.*?)</script>', re.DOTALL
)


def payload_of(html):
    """Return the payload a rendered tour carries, parsed from its script element."""
    match = STEPS_SCRIPT.fullmatch(str(html))
    assert match is not None
    return json.loads(match.group(1))


def page_payload(response):
    """Return the payload a page carries, parsed from its script element."""
    match = STEPS_SCRIPT.search(response.content.decode())
    assert match is not None
    return json.loads(match.group(1))


def page_steps(response):
    """Return the steps a page carries."""
    return page_payload(response)["config"]["steps"]


class TestTourRendering:
    """A tour renders itself as the element the package's script plays it from."""

    def test_in_a_template_it_renders_its_script_element_unescaped(self):
        """``{{ tour }}`` outputs the element itself, not escaped text."""
        rendered = Template("{{ tour }}").render(Context({"tour": views.CLASS_TOUR}))

        assert payload_of(rendered)["id"] == views.CLASS_TOUR.name

    @pytest.mark.parametrize("autoescape", [True, False])
    def test_it_renders_the_same_with_and_without_autoescaping(self, autoescape):
        """Turning autoescaping off changes nothing."""
        context = Context({"tour": views.CLASS_TOUR}, autoescape=autoescape)

        rendered = Template("{{ tour }}").render(context)

        assert rendered == views.CLASS_TOUR.__html__()

    def test_str_is_the_same_safe_html(self):
        """``str()`` returns what ``__html__`` returns, marked safe."""
        rendered = str(views.CLASS_TOUR)

        assert rendered == views.CLASS_TOUR.__html__()
        assert isinstance(rendered, SafeString)

    def test_the_payload_carries_exactly_its_kind_id_version_autoplay_parts_and_config(
        self,
    ):
        """Nothing else reaches the browser."""
        payload = payload_of(views.CLASS_TOUR)

        assert set(payload) == {
            "kind",
            "id",
            "version",
            "autoplay",
            "parts",
            "config",
        }

    def test_the_payload_carries_the_tours_name_version_and_autoplay(self):
        """The browser remembers the tour by its name, at its version."""
        payload = payload_of(views.ON_REQUEST_VERSION_TWO)

        assert payload["id"] == views.ON_REQUEST_VERSION_TWO.name
        assert payload["version"] == 2
        assert payload["autoplay"] is False

    def test_a_tour_declared_with_neither_plays_by_itself_at_version_one(self):
        """``autoplay`` is true and ``version`` is 1 for a tour that does not say."""
        payload = payload_of(views.CLASS_TOUR)

        assert payload["autoplay"] is True
        assert payload["version"] == 1

    def test_the_steps_are_its_steps_as_driverjs_takes_them(self):
        """The steps arrive in the declared order, in Driver.js's form."""
        assert (
            payload_of(views.CLASS_TOUR)["config"]["steps"]
            == (views.CLASS_TOUR.as_driver()["steps"])
        )

    def test_a_translated_step_is_in_the_active_language(self):
        """The tour is converted when it renders, in the language active then."""
        with translation.override("de"):
            payload = payload_of(views.TRANSLATED_TOUR)
            expected = str(gettext("Yes"))

        assert payload["config"]["steps"][0]["popover"]["title"] == expected != "Yes"

    def test_the_payload_carries_every_part_with_its_name(self):
        """Each part is a key, and its documented name is the first class."""
        assert payload_of(views.CLASS_TOUR)["parts"] == {
            part: [f"page-tour-{part}"] for part in TourParts.parts
        }

    def test_a_configured_value_is_carried_after_the_name(self, settings):
        """The classes a site sets for a part reach the browser."""
        settings.PAGE_TOURS_CLASSES = {"box": "card shadow"}

        payload = payload_of(views.CLASS_TOUR)

        assert payload["parts"]["box"] == ["page-tour-box", "card", "shadow"]

    def test_a_value_holding_markup_stays_inside_the_script_element(self, settings):
        """A value cannot close the element or add one to the page."""
        value = '"><script>alert(1)</script>'
        settings.PAGE_TOURS_CLASSES = {"box": value}

        rendered = str(views.CLASS_TOUR)

        assert len(STEPS_SCRIPT.findall(rendered)) == 1
        assert "<script>alert(1)</script>" not in rendered
        assert payload_of(rendered)["parts"]["box"] == ["page-tour-box", *value.split()]

    @pytest.mark.parametrize("value", [None, "box", 3, {"box": 3, "footer": "x"}])
    def test_a_tour_renders_with_a_wrong_setting(self, settings, value):
        """A styling mistake never stops a tour from rendering."""
        settings.PAGE_TOURS_CLASSES = value

        assert payload_of(views.CLASS_TOUR)["parts"]["box"] == ["page-tour-box"]

    def test_the_payload_does_not_carry_where_the_tour_is_declared(self):
        """Where the tour lives in the code stays out of the page source."""
        assert "tests.views" not in str(views.CLASS_TOUR)


class TestTourOnAPage:
    """A view puts its tour in the context, and the page renders it."""

    @pytest.mark.parametrize(
        ("url", "tour"),
        [("class-tour", views.CLASS_TOUR), ("function-tour", views.FUNCTION_TOUR)],
        ids=["class-based view", "function-based view"],
    )
    def test_the_page_carries_its_views_tour(self, client, url, tour):
        """A class-based view's ``extra_context`` and a function's context both work."""
        response = client.get(reverse(url))

        assert page_payload(response) == payload_of(tour)

    def test_a_page_with_no_tour_carries_no_steps(self, client):
        """``{{ tour }}`` with nothing in the context renders nothing."""
        response = client.get(reverse("no-tour"))

        assert "page-tours-tour" not in response.content.decode()

    def test_a_tour_given_through_as_view_is_on_that_url(self, client):
        """``as_view(extra_context=...)`` puts a tour on one URL."""
        response = client.get(reverse("versioned-two"))

        assert page_payload(response)["version"] == 2

    def test_both_urls_of_a_view_carry_its_tour(self, client):
        """A view routed twice shows its tour on both."""
        first = page_payload(client.get(reverse("class-tour")))
        second = page_payload(client.get(reverse("class-tour-again")))

        assert first == second

    @pytest.mark.django_db
    def test_a_signed_in_and_an_anonymous_visitor_get_the_same_steps(
        self, client, django_user_model
    ):
        """The tour does not depend on who is looking."""
        anonymous = page_steps(client.get(reverse("class-tour")))
        client.force_login(django_user_model.objects.create_user("visitor"))

        signed_in = page_steps(client.get(reverse("class-tour")))

        assert signed_in == anonymous

    @pytest.mark.parametrize("name", ["missing-class-tour", "missing-function-tour"])
    def test_a_not_found_page_does_not_carry_the_tour(self, client, settings, name):
        """The error page renders ``{{ tour }}`` with a context that has no tour."""
        settings.DEBUG = False

        response = client.get(reverse(name))

        assert response.status_code == 404
        assert "page-tours-tour" not in response.content.decode()

    def test_a_tour_rendered_twice_is_on_the_page_twice(self, client):
        """The template decides; the browser plays the first one."""
        response = client.get(reverse("tour-twice"))

        assert len(STEPS_SCRIPT.findall(response.content.decode())) == 2


OVERRIDDEN = views.APP_TOUR.name
REPLACEMENT = "tests.views.REPLACEMENT_TOUR"


class TestTourOverrides:
    """A project changes or turns off a tour declared by an installed app."""

    def test_a_replacement_is_rendered_in_its_place(self, settings):
        """The tour renders the replacement's steps and autoplay."""
        settings.PAGE_TOURS_OVERRIDES = {
            OVERRIDDEN: "tests.views.QUIET_REPLACEMENT_TOUR"
        }

        payload = payload_of(views.APP_TOUR)

        assert (
            payload["config"]["steps"]
            == views.QUIET_REPLACEMENT_TOUR.as_driver()["steps"]
        )
        assert payload["autoplay"] is False

    def test_one_reworded_step_arrives_among_the_apps_in_order(self, settings):
        """A replacement that rewords one step carries all three, in order."""
        settings.PAGE_TOURS_OVERRIDES = {OVERRIDDEN: "tests.views.REWORDED_TOUR"}

        steps = payload_of(views.APP_TOUR)["config"]["steps"]

        assert steps == views.REWORDED_TOUR.as_driver()["steps"]

    def test_a_replacement_renders_its_own_options(self, settings):
        """The options are the replacement's, not the replaced tour's."""
        settings.PAGE_TOURS_OVERRIDES = {OVERRIDDEN: "tests.views.OPTIONS_TOUR"}

        options = payload_of(views.APP_TOUR)["config"]

        assert options["showProgress"] is True
        assert options["progressText"] == "{{current}} / {{total}}"

    def test_a_replacement_keeps_the_name_of_the_tour_it_replaces(self, settings):
        """Replacing a tour does not rename it, so what was seen stays seen."""
        settings.PAGE_TOURS_OVERRIDES = {OVERRIDDEN: REPLACEMENT}

        assert payload_of(views.APP_TOUR)["id"] == OVERRIDDEN

    def test_rendering_a_replacement_declares_no_tour(self, settings):
        """Playing a replacement under the app tour's name is not a second tour."""
        settings.PAGE_TOURS_OVERRIDES = {OVERRIDDEN: REPLACEMENT}
        before = {name: len(tours) for name, tours in declarations().items()}

        str(views.APP_TOUR)

        after = {name: len(tours) for name, tours in declarations().items()}
        assert after == before

    def test_none_turns_the_tour_off(self, settings):
        """A tour set to None renders nothing at all."""
        settings.PAGE_TOURS_OVERRIDES = {OVERRIDDEN: None}

        assert Template("{{ tour }}").render(Context({"tour": views.APP_TOUR})) == ""

    def test_a_tour_turned_off_leaves_its_page_without_steps(self, client, settings):
        """Nothing about the tour reaches the page, so a replay control stays hidden."""
        settings.PAGE_TOURS_OVERRIDES = {views.OFF_TOUR.name: None}

        response = client.get(reverse("overridden-off"))

        assert "page-tours-tour" not in response.content.decode()

    @pytest.mark.parametrize(
        "url", ["overridden", "overridden-again", "overridden-function"]
    )
    def test_every_page_of_the_tour_renders_the_change(self, client, settings, url):
        """Every URL, class-based or function-based, plays the replacement."""
        settings.PAGE_TOURS_OVERRIDES = {OVERRIDDEN: REPLACEMENT}

        response = client.get(reverse(url))

        assert page_steps(response) == views.REPLACEMENT_TOUR.as_driver()["steps"]

    def test_another_tour_is_untouched(self, settings):
        """A tour the setting does not name renders as declared."""
        settings.PAGE_TOURS_OVERRIDES = {OVERRIDDEN: REPLACEMENT}

        payload = payload_of(views.UNTOUCHED_TOUR)

        assert payload["config"]["steps"] == views.UNTOUCHED_TOUR.as_driver()["steps"]

    @pytest.mark.parametrize(
        ("declared", "path", "played"),
        [
            (2, REPLACEMENT, 2),
            (2, "tests.views.REPLACEMENT_TOUR_VERSION_TWO", 3),
            (1, REPLACEMENT, 1),
        ],
    )
    def test_a_replacement_counts_on_from_the_version_it_replaces(
        self, settings, declared, path, played
    ):
        """The version played is the declared one plus the replacement's, less one."""
        settings.PAGE_TOURS_OVERRIDES = {OVERRIDDEN: path}
        declared_tour = replace(views.APP_TOUR, version=declared)

        assert payload_of(declared_tour)["version"] == played

    def test_the_declared_replacement_is_not_changed(self, settings):
        """Counting a version on leaves the declared replacement as it was."""
        settings.PAGE_TOURS_OVERRIDES = {OVERRIDDEN: REPLACEMENT}

        str(views.APP_TOUR)

        assert views.REPLACEMENT_TOUR.version == 1
        assert views.REPLACEMENT_TOUR.name == "tests.replacement"

    def test_a_change_to_the_setting_is_seen_at_once(self, settings):
        """The setting is read every time the tour renders, not cached."""
        settings.PAGE_TOURS_OVERRIDES = {OVERRIDDEN: None}
        assert str(views.APP_TOUR) == ""

        settings.PAGE_TOURS_OVERRIDES = {}

        assert (
            payload_of(views.APP_TOUR)["config"]["steps"]
            == views.APP_TOUR.as_driver()["steps"]
        )

    def test_a_bad_entry_is_refused_when_the_tour_renders(self, settings):
        """An entry set after start-up that cannot be resolved raises."""
        settings.PAGE_TOURS_OVERRIDES = {OVERRIDDEN: 42}

        with pytest.raises(ImproperlyConfigured):
            str(views.APP_TOUR)


class TestTourOverridesRefused:
    """A setting that cannot be used is refused, not ignored."""

    @pytest.mark.parametrize("value", [42, ["tests.views.REPLACEMENT_TOUR"], True])
    def test_a_value_that_is_neither_a_path_nor_none_is_refused(self, value):
        """Only a dotted path or None is a replacement."""
        with pytest.raises(ImproperlyConfigured):
            resolve_override(OVERRIDDEN, value)

    def test_a_tour_object_is_refused(self):
        """The setting holds paths, so a project's settings do not import its tours."""
        with pytest.raises(ImproperlyConfigured):
            resolve_override(OVERRIDDEN, views.REPLACEMENT_TOUR)

    @pytest.mark.parametrize(
        "path", ["tests.views.missing_tour", "tests.no_such_module.tour", "nodots"]
    )
    def test_a_path_that_does_not_import_is_refused(self, path):
        """A replacement that is not there is an error."""
        with pytest.raises(ImproperlyConfigured):
            resolve_override(OVERRIDDEN, path)

    def test_a_path_that_does_not_import_keeps_its_cause(self):
        """The import error that explains the refusal is chained."""
        with pytest.raises(ImproperlyConfigured) as raised:
            resolve_override(OVERRIDDEN, "tests.views.missing_tour")

        assert isinstance(raised.value.__cause__, ImportError)

    def test_a_path_to_something_that_is_not_a_tour_is_refused(self):
        """What the path names has to be a Tour."""
        with pytest.raises(ImproperlyConfigured):
            resolve_override(OVERRIDDEN, "tests.views.NOT_A_TOUR")

    def test_a_module_whose_own_tour_is_invalid_raises_its_own_error(self):
        """The module's error is not reported as a path that cannot be imported."""
        with pytest.raises(ImproperlyConfigured) as raised:
            resolve_override(OVERRIDDEN, "tests.invalid_tour.BROKEN_TOUR")

        assert raised.value.__cause__ is None

    def test_none_resolves_to_none(self):
        """A tour turned off has no replacement."""
        assert resolve_override(OVERRIDDEN, None) is None

    def test_every_entry_of_the_setting_is_resolved(self, settings):
        """The replacements and the tours turned off are returned by name."""
        settings.PAGE_TOURS_OVERRIDES = {OVERRIDDEN: REPLACEMENT, "other": None}

        assert declaration_overrides() == {
            OVERRIDDEN: views.REPLACEMENT_TOUR,
            "other": None,
        }

    def test_no_setting_resolves_to_nothing(self):
        """A project that sets nothing changes no tour."""
        assert declaration_overrides() == {}

    def test_one_bad_entry_refuses_the_whole_setting(self, settings):
        """A good entry does not hide a bad one."""
        settings.PAGE_TOURS_OVERRIDES = {OVERRIDDEN: REPLACEMENT, "other": 42}

        with pytest.raises(ImproperlyConfigured):
            declaration_overrides()


class TestDeclaredTours:
    """The package records every tour by its name as it is declared."""

    def test_a_declared_tour_is_recorded_under_its_name(self):
        """A tour can be found by its name once it exists."""
        tour = Tour(name="tests.recorded", steps=[STEP])

        assert declarations()["tests.recorded"] == [tour]

    def test_two_tours_with_one_name_are_both_recorded(self):
        """Both are kept, so the check can report the clash."""
        first = Tour(name="tests.twice", steps=[STEP])
        second = Tour(name="tests.twice", steps=[STEP], version=2)

        recorded = declarations()["tests.twice"]

        assert len(recorded) == 2
        assert any(tour is first for tour in recorded)
        assert any(tour is second for tour in recorded)

    def test_a_tour_that_no_longer_exists_is_forgotten(self):
        """A tour nothing refers to any more is no longer declared."""
        Tour(name="tests.forgotten", steps=[STEP])
        gc.collect()

        assert "tests.forgotten" not in declarations()

    def test_tours_made_and_dropped_leave_nothing_behind(self):
        """A view that builds its tour on every request does not grow the record."""
        for _ in range(3):
            Tour(name="tests.per-request", steps=[STEP])
        gc.collect()

        assert "tests.per-request" not in driver_module.declared

    def test_the_tours_of_the_routed_views_are_declared(self):
        """A tour declared in a view module is recorded when the module is imported."""
        assert any(
            tour is views.APP_TOUR for tour in declarations()[views.APP_TOUR.name]
        )


class TestTourSiteText:
    """``PAGE_TOURS_TEXT`` gives the default text of every tour."""

    def test_a_tour_that_sets_nothing_takes_the_setting(self):
        """A tour's texts come from the setting, and the rest from the package."""
        config = run_with_site_text(
            """
            import json
            from page_tours import Tour, TourStep
            from page_tours.tours import DONE_LABEL
            tour = Tour(name="tests.site-text", steps=[TourStep(title="One")])
            driver = tour.as_driver()
            print(json.dumps({
                "next": driver["nextBtnText"],
                "progress": driver["progressText"],
                "done_is_default": driver["doneBtnText"] == str(DONE_LABEL),
            }))
            """
        )

        assert config == {
            "next": SITE_TEXT["tour"]["nextBtnText"],
            "progress": SITE_TEXT["tour"]["progressText"],
            "done_is_default": True,
        }

    def test_a_tour_step_or_subclass_that_sets_its_own_text_keeps_it(self):
        """Text set on a tour, a subclass or a step wins over the setting."""
        config = run_with_site_text(
            """
            import json
            from dataclasses import dataclass
            from page_tours import Tour, TourStep

            @dataclass(frozen=True, kw_only=True)
            class WordedTour(Tour):
                nextBtnText: str = "Subclass next"

            steps = [TourStep(title="One", nextBtnText="Step next")]
            print(json.dumps({
                "argument": Tour(
                    name="tests.own", steps=steps, nextBtnText="Own next"
                ).as_driver()["nextBtnText"],
                "subclass": WordedTour(name="tests.sub", steps=steps).as_driver()[
                    "nextBtnText"
                ],
                "step": Tour(name="tests.step", steps=steps).as_driver()["steps"][0][
                    "popover"
                ]["nextBtnText"],
            }))
            """
        )

        assert config == {
            "argument": "Own next",
            "subclass": "Subclass next",
            "step": "Step next",
        }
