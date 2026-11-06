"""Tests for page_tours.templatetags.page_tours."""

import json
import re
from html.parser import HTMLParser
from types import SimpleNamespace

import pytest
from django.template import Context, Template, TemplateSyntaxError
from django.urls import reverse
from django.utils import translation
from django.utils.html import escape
from django.utils.translation import gettext_lazy

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
        """A page rendered by a ``with_tour`` view carries the tour."""
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


class TestPageTourPayload:
    """The object the tag hands to the starter script."""

    def test_the_payload_names_the_view_that_declares_the_tour(self, client):
        """The id is the dotted path of the view class."""
        payload = tour_payload(client.get(reverse("class-tour")))

        assert payload["id"] == "tests.views.ClassTourView"

    def test_the_payload_names_a_function_based_view(self, client):
        """The id of a ``with_tour`` view is its dotted path."""
        payload = tour_payload(client.get(reverse("function-tour")))

        assert payload["id"] == "tests.views.function_tour_view"

    def test_a_tour_plays_by_itself_unless_told_otherwise(self, client):
        """``autoplay`` is true for a tour that does not say."""
        payload = tour_payload(client.get(reverse("class-tour")))

        assert payload["autoplay"] is True

    def test_a_tour_declared_to_play_only_on_request_says_so(self, client):
        """``autoplay`` is false for a tour declared with ``autoplay=False``."""
        payload = tour_payload(client.get(reverse("on-request")))

        assert payload["autoplay"] is False

    def test_the_payload_carries_exactly_an_id_autoplay_and_steps(self, client):
        """Nothing else reaches the browser."""
        payload = tour_payload(client.get(reverse("class-tour")))

        assert set(payload) == {"id", "autoplay", "steps"}

    def test_both_urls_of_a_view_carry_the_same_id(self, client):
        """A view routed twice is one tour."""
        first = tour_payload(client.get(reverse("class-tour")))
        second = tour_payload(client.get(reverse("class-tour-again")))

        assert first["id"] == second["id"]

    def test_a_page_with_no_tour_carries_no_payload(self, client):
        """No script element at all."""
        response = client.get(reverse("no-tour"))

        assert STEPS_SCRIPT.search(response.content.decode()) is None


class ReplayMarkup(HTMLParser):
    """Collect the elements of a page, remembering which sit inside a template."""

    def __init__(self):
        super().__init__()
        self.templates = []
        self.buttons = []
        self.classes = []
        self.text = ""
        self.depth = 0
        self.in_button = False

    def handle_starttag(self, tag, attrs):
        """Record templates, the buttons inside them and every class seen."""
        attributes = dict(attrs)
        if tag == "template":
            self.templates.append(attributes)
            self.depth += 1
        elif tag == "button" and self.depth:
            self.buttons.append(attributes)
            self.in_button = True
            self.text = ""
        if self.depth and "class" in attributes:
            self.classes.append(attributes["class"])

    def handle_endtag(self, tag):
        """Leave the template or the button."""
        if tag == "template":
            self.depth -= 1
        elif tag == "button":
            self.in_button = False

    def handle_data(self, data):
        """Gather the text of the button inside the template."""
        if self.in_button:
            self.text += data


def replay_markup(html):
    """Parse a page and return what its replay templates hold."""
    markup = ReplayMarkup()
    markup.feed(html)
    return markup


def render_replay(source, tour=CLASS_TOUR):
    """Render a template string on a page whose view declares ``tour``."""
    template = Template("{% load page_tours %}" + source)
    return template.render(Context({"view": SimpleNamespace(tour=tour)}))


class TestPageTourReplayTag:
    """The tag that places a control replaying the page's tour."""

    def test_a_page_with_no_tour_gets_nothing(self, client):
        """No template, no button."""
        response = client.get(reverse("replay-no-tour"))

        markup = replay_markup(response.content.decode())
        assert markup.templates == []
        assert markup.buttons == []

    def test_a_page_with_a_tour_gets_one_template_holding_one_button(self, client):
        """The control waits in a template for the starter script."""
        response = client.get(reverse("replay"))

        markup = replay_markup(response.content.decode())
        assert markup.templates == [{"data-page-tour-replay": None}]
        assert len(markup.buttons) == 1
        assert markup.buttons[0]["type"] == "button"

    def test_a_control_placed_once_in_a_base_template_shows_only_with_a_tour(
        self, client
    ):
        """Pages extending the base get the control only if they have a tour."""
        with_tour = client.get(reverse("control-in-base")).content.decode()
        without_tour = client.get(reverse("control-in-base-no-tour")).content.decode()

        assert len(replay_markup(with_tour).templates) == 1
        assert replay_markup(without_tour).templates == []

    def test_the_button_holds_the_content_of_the_block(self):
        """What sits between the tags is what the button holds."""
        html = render_replay("{% page_tour_replay %}<i>Go</i>{% endpage_tour_replay %}")

        assert replay_markup(html).text == "Go"

    def test_a_page_placing_the_control_twice_gets_two_buttons(self, client):
        """Each placement renders its own template."""
        response = client.get(reverse("replay-twice"))

        markup = replay_markup(response.content.decode())
        assert len(markup.templates) == 2
        assert len(markup.buttons) == 2

    def test_the_developers_attributes_are_on_the_button(self, client):
        """Class, id and data attributes arrive unchanged."""
        response = client.get(reverse("replay"))

        button = replay_markup(response.content.decode()).buttons[0]
        assert button["class"] == "mine"
        assert button["id"] == "replay"
        assert button["data-x"] == "1"

    def test_no_class_but_the_developers_is_added(self, client):
        """Every class inside the template is the one the developer gave."""
        response = client.get(reverse("replay"))

        assert replay_markup(response.content.decode()).classes == ["mine"]

    def test_attribute_values_are_escaped(self, client):
        """A value with markup characters reaches the button as text."""
        response = client.get(reverse("replay"))

        button = replay_markup(response.content.decode()).buttons[0]
        assert button["title"] == 'a "quoted" <b>&'
        assert "<b>&" not in response.content.decode()

    def test_aria_label_renders_as_aria_label(self, client):
        """An underscore in an argument name becomes a hyphen."""
        response = client.get(reverse("replay"))

        button = replay_markup(response.content.decode()).buttons[0]
        assert button["aria-label"] == "Again"
        assert "aria_label" not in button

    def test_an_empty_block_gets_the_translatable_fallback(self):
        """The fallback is the text ``gettext`` supplies, and is not empty."""
        html = render_replay("{% page_tour_replay %} {% endpage_tour_replay %}")

        markup = replay_markup(html)
        assert markup.text == str(gettext_lazy("Show the tour"))
        assert markup.text.strip() != ""

    def test_a_type_argument_does_not_change_the_button_type(self):
        """The button never submits a form."""
        html = render_replay(
            '{% page_tour_replay type="submit" %}Go{% endpage_tour_replay %}'
        )

        buttons = replay_markup(html).buttons
        assert [button["type"] for button in buttons] == ["button"]

    def test_a_positional_argument_is_a_template_syntax_error(self):
        """Only ``name=value`` arguments are taken."""
        with pytest.raises(TemplateSyntaxError):
            render_replay('{% page_tour_replay "first" %}Go{% endpage_tour_replay %}')
