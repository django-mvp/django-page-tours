"""Tests for page_tours.templatetags.page_tours."""

import json
import re

import pytest
from django.template import Context, Template
from django.urls import reverse
from django.utils import translation
from django.utils.html import escape

from page_tours.parts import TourParts
from tests import views
from tests.views import CLASS_TOUR, FUNCTION_TOUR, MARKUP_TITLE

STEPS_SCRIPT = re.compile(
    r'<script id="page-tour-steps" type="application/json">(.*?)</script>', re.DOTALL
)
URL_ATTRIBUTE = re.compile(r'\b(?:src|href)="([^"]*)"')


def tour_payload(response):
    """Return the payload the page carries, parsed from its script element."""
    match = STEPS_SCRIPT.search(response.content.decode())
    assert match is not None
    return json.loads(match.group(1))


def tour_steps(response):
    """Return the steps the page carries."""
    return tour_payload(response)["steps"]


class TestPageTourTag:
    """The tag that puts a page's tour on the page."""

    def test_the_page_carries_its_steps_in_order(self, client):
        """A class-based page's steps arrive in the order declared."""
        response = client.get(reverse("class-tour"))

        titles = [step["title"] for step in tour_steps(response)]
        assert titles == [step.title for step in CLASS_TOUR.steps]

    def test_a_step_with_an_element_carries_its_selector(self, client):
        """The selector of a step is in its entry."""
        response = client.get(reverse("class-tour"))

        assert tour_steps(response)[1]["element"] == "h1"

    def test_a_step_with_no_element_has_no_element_key(self, client):
        """A step attached to nothing carries no ``element`` key."""
        response = client.get(reverse("class-tour"))

        assert "element" not in tour_steps(response)[0]

    def test_a_page_with_no_tour_carries_nothing_of_the_package(self, client):
        """No steps and no reference to the package's files."""
        response = client.get(reverse("no-tour"))

        content = response.content.decode()
        assert "page-tour-steps" not in content
        assert "page_tours/" not in content

    def test_every_file_comes_from_the_sites_static_url(self, client, settings):
        """Each ``src`` and ``href`` starts with ``STATIC_URL`` and names no host."""
        response = client.get(reverse("class-tour"))

        urls = URL_ATTRIBUTE.findall(response.content.decode())
        assert urls
        assert all(url.startswith(settings.STATIC_URL) for url in urls)
        assert not any("//" in url for url in urls)

    def test_markup_characters_in_a_step_arrive_escaped(self, client):
        """The step is plain text: its markup characters reach the page escaped."""
        response = client.get(reverse("markup-tour"))

        assert tour_steps(response)[0]["title"] == escape(MARKUP_TITLE)
        assert MARKUP_TITLE not in response.content.decode()

    @pytest.mark.django_db
    def test_a_signed_in_and_an_anonymous_visitor_get_the_same_steps(
        self, client, django_user_model
    ):
        """The tour does not depend on who is looking."""
        anonymous = tour_steps(client.get(reverse("class-tour")))
        client.force_login(django_user_model.objects.create_user("visitor"))

        signed_in = tour_steps(client.get(reverse("class-tour")))

        assert signed_in == anonymous

    def test_both_urls_of_a_view_carry_its_tour(self, client):
        """A view routed twice shows its tour on both."""
        first = tour_steps(client.get(reverse("class-tour")))
        second = tour_steps(client.get(reverse("class-tour-again")))

        assert first == second

    def test_a_function_based_page_carries_its_tour(self, client):
        """A function-based view that passes its tour in the context shows it."""
        response = client.get(reverse("function-tour"))

        assert tour_steps(response) == FUNCTION_TOUR.as_driver_steps()

    def test_a_template_with_no_request_renders_nothing(self):
        """Rendered outside a request, the tag has nothing to emit."""
        template = Template("{% load page_tours %}{% page_tour %}")

        assert template.render(Context({})).strip() == ""

    @pytest.mark.parametrize("name", ["missing-class-tour", "missing-function-tour"])
    def test_a_not_found_page_does_not_carry_the_tour(self, client, settings, name):
        """The error page shown instead of the page has no tour."""
        settings.DEBUG = False

        response = client.get(reverse(name))

        assert response.status_code == 404
        assert "page-tour-steps" not in response.content.decode()

    def test_a_translated_step_is_in_the_active_language(self, client):
        """A lazy title is converted when the page is rendered."""
        with translation.override("de"):
            response = client.get(reverse("translated-tour"))

            expected = str(translation.gettext("Yes"))
        assert tour_steps(response)[0]["title"] == expected
        assert expected != "Yes"


class TestPageTourStylesheet:
    """The stylesheet the tag links."""

    def test_the_page_links_the_packages_stylesheet_and_not_driverjs_directly(
        self, client
    ):
        """The one link is to page-tours.css, marked for the starter script."""
        response = client.get(reverse("class-tour"))

        content = response.content.decode()
        links = re.findall(r"<link\b[^>]*>", content)
        assert len(links) == 1
        assert "data-page-tour-stylesheet" in links[0]
        assert "page_tours/page-tours.css" in links[0]


class TestPageTourPayload:
    """The object the tag hands to the starter script."""

    def test_the_controls_are_in_the_active_language(self, client):
        """The labels for the tour's own controls follow the language of the page."""
        with translation.override("de"):
            payload = tour_payload(client.get(reverse("navigation-tour")))

        assert payload["controls"]["previous"] == "Zurück"
        assert payload["controls"]["done"] == "Fertig"

    @pytest.mark.parametrize(
        ("url", "tour"),
        [("class-tour", CLASS_TOUR), ("function-tour", FUNCTION_TOUR)],
        ids=["class-based view", "function-based view"],
    )
    def test_the_payload_carries_the_tours_name(self, client, url, tour):
        """The browser remembers the tour by the name it is declared with."""
        payload = tour_payload(client.get(reverse(url)))

        assert payload["id"] == tour.name

    def test_the_page_does_not_carry_the_views_path(self, client):
        """Where the view lives in the code stays out of the page source."""
        content = client.get(reverse("class-tour")).content.decode()

        assert "tests.views" not in content

    def test_a_tour_plays_by_itself_unless_told_otherwise(self, client):
        """``autoplay`` is true for a tour that does not say."""
        payload = tour_payload(client.get(reverse("class-tour")))

        assert payload["autoplay"] is True

    def test_a_tour_declared_without_a_version_is_at_version_one(self, client):
        """``version`` is 1 for a tour that does not say."""
        payload = tour_payload(client.get(reverse("versioned")))

        assert payload["version"] == 1

    def test_the_payload_carries_the_declared_version(self, client):
        """``version`` is the one the tour is declared with."""
        payload = tour_payload(client.get(reverse("versioned-two")))

        assert payload["version"] == 2

    def test_a_tour_declared_to_play_only_on_request_says_so(self, client):
        """``autoplay`` is false for a tour declared with ``autoplay=False``."""
        payload = tour_payload(client.get(reverse("on-request")))

        assert payload["autoplay"] is False

    def test_the_payload_carries_exactly_its_id_version_autoplay_steps_and_controls(
        self, client
    ):
        """Nothing else reaches the browser."""
        payload = tour_payload(client.get(reverse("class-tour")))

        assert set(payload) == {
            "id",
            "version",
            "autoplay",
            "steps",
            "controls",
            "parts",
        }

    def test_both_urls_of_a_view_carry_the_same_id(self, client):
        """A view routed twice is one tour."""
        first = tour_payload(client.get(reverse("class-tour")))
        second = tour_payload(client.get(reverse("class-tour-again")))

        assert first["id"] == second["id"]

    def test_a_page_with_no_tour_carries_no_payload(self, client):
        """No script element at all."""
        response = client.get(reverse("no-tour"))

        assert STEPS_SCRIPT.search(response.content.decode()) is None

    def test_the_payload_carries_every_part_with_its_name(self, client):
        """Each part is a key, and its documented name is the first class."""
        payload = tour_payload(client.get(reverse("class-tour")))

        assert payload["parts"] == {
            part: [f"page-tour-{part}"] for part in TourParts.parts
        }

    def test_a_configured_value_is_carried_after_the_name(self, client, settings):
        """The classes a site sets for a part reach the browser."""
        settings.PAGE_TOURS_CLASSES = {"box": "card shadow"}

        payload = tour_payload(client.get(reverse("class-tour")))

        assert payload["parts"]["box"] == ["page-tour-box", "card", "shadow"]

    def test_a_value_holding_markup_stays_inside_the_script_element(
        self, client, settings
    ):
        """A value cannot close the element or add one to the page."""
        value = '"><script>alert(1)</script>'
        settings.PAGE_TOURS_CLASSES = {"box": value}

        response = client.get(reverse("class-tour"))

        content = response.content.decode()
        assert len(STEPS_SCRIPT.findall(content)) == 1
        assert "<script>alert(1)</script>" not in content
        assert tour_payload(response)["parts"]["box"] == [
            "page-tour-box",
            *value.split(),
        ]

    @pytest.mark.parametrize("value", [None, "box", 3, {"box": 3, "footer": "x"}])
    def test_a_page_renders_with_a_wrong_setting(self, client, settings, value):
        """A styling mistake never stops a tour from rendering."""
        settings.PAGE_TOURS_CLASSES = value

        response = client.get(reverse("class-tour"))

        assert response.status_code == 200
        assert tour_payload(response)["parts"]["box"] == ["page-tour-box"]


OVERRIDDEN = views.APP_TOUR.name


class TestOverriddenTourPayload:
    """The page of an app's tour carries what the project changed it to."""

    def get(self, client, settings, replacement, name="overridden"):
        """Open the page with the app's tour replaced by a module constant."""
        settings.PAGE_TOURS_OVERRIDES = {OVERRIDDEN: f"tests.views.{replacement}"}
        return client.get(reverse(name))

    def test_the_steps_are_the_replacements_and_the_id_is_the_apps(
        self, client, settings
    ):
        """The page plays the project's steps under the app's name for the tour."""
        response = self.get(client, settings, "REPLACEMENT_TOUR")

        payload = tour_payload(response)
        assert payload["steps"] == views.REPLACEMENT_TOUR.as_driver_steps()
        assert payload["id"] == OVERRIDDEN

    def test_one_reworded_step_arrives_among_the_apps_in_order(self, client, settings):
        """A replacement that rewords one step carries all three, in order."""
        response = self.get(client, settings, "REWORDED_TOUR")

        assert tour_steps(response) == views.REWORDED_TOUR.as_driver_steps()

    def test_a_replacement_that_does_not_autoplay_carries_it(self, client, settings):
        """The replacement's own autoplay reaches the page."""
        response = self.get(client, settings, "QUIET_REPLACEMENT_TOUR")

        assert tour_payload(response)["autoplay"] is False

    @pytest.mark.parametrize(
        ("replacement", "version"),
        [("REPLACEMENT_TOUR", 2), ("REPLACEMENT_TOUR_VERSION_TWO", 3)],
    )
    def test_the_version_counts_on_from_the_apps(
        self, client, settings, replacement, version
    ):
        """The app's tour is at version 2, so the replacement plays at 2 or 3."""
        response = self.get(client, settings, replacement)

        assert tour_payload(response)["version"] == version

    def test_a_tour_turned_off_has_no_payload_and_no_starter_script(
        self, client, settings
    ):
        """Nothing about the tour reaches the page, so a replay control stays hidden."""
        settings.PAGE_TOURS_OVERRIDES = {views.OFF_TOUR.name: None}

        response = client.get(reverse("overridden-off"))

        content = response.content.decode()
        assert "page-tour-steps" not in content
        assert "page-tours.js" not in content

    def test_every_url_of_the_view_carries_the_change(self, client, settings):
        """Two routes to the one view play the same replacement."""
        settings.PAGE_TOURS_OVERRIDES = {OVERRIDDEN: "tests.views.REPLACEMENT_TOUR"}

        payloads = [
            tour_payload(client.get(reverse(name)))
            for name in ("overridden", "overridden-again")
        ]

        assert payloads[0] == payloads[1]
        assert payloads[0]["steps"] == views.REPLACEMENT_TOUR.as_driver_steps()
