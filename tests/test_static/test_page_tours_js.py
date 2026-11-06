"""Tests for the starter script, page_tours/static/page_tours/page-tours.js."""

from django.urls import reverse
from playwright.sync_api import expect

from tests.views import CLASS_TOUR, MARKUP_TITLE

TITLE = ".driver-popover-title"


class TestTourPlays:
    """The tour a page carries plays when the page opens in a browser."""

    def test_the_first_step_shows_in_a_popover(self, page, live_server):
        """Opening the page shows a popover titled with the first step's title."""
        page.goto(live_server.url + reverse("class-tour"))

        title = page.locator(TITLE)
        expect(title).to_have_text(CLASS_TOUR.steps[0].title)

    def test_markup_characters_in_a_step_show_as_text(self, page, live_server):
        """A title with markup characters shows exactly as written."""
        page.goto(live_server.url + reverse("markup-tour"))

        title = page.locator(TITLE)
        expect(title).to_be_visible()
        assert title.text_content() == MARKUP_TITLE
