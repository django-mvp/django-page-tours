"""Tests for the starter script, page_tours/static/page_tours/page-tours.js."""

from django.urls import reverse
from playwright.sync_api import expect

from tests.views import CLASS_TOUR, MARKUP_TITLE

TITLE = ".driver-popover-title"
NEXT = ".driver-popover-next-btn"
PREVIOUS = ".driver-popover-prev-btn"
CLOSE = ".driver-popover-close-btn"


def assert_no_driver_markup(page):
    """Assert that nothing of Driver.js is left on the page."""
    leftovers = page.evaluate(
        """() => ({
            classed: [...document.querySelectorAll("*")]
                .filter((el) => [...el.classList].some((c) => c.includes("driver-")))
                .map((el) => el.tagName),
            dummy: document.getElementById("driver-dummy-element") !== null,
            controls: document.querySelectorAll(
                '[aria-controls="driver-popover-content"]'
            ).length,
            body: document.body.className,
        })"""
    )
    assert leftovers["classed"] == []
    assert leftovers["dummy"] is False
    assert leftovers["controls"] == 0
    assert "driver-" not in leftovers["body"]


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


class TestTourNavigation:
    """A visitor moves through the tour and closes it."""

    def test_next_and_previous_move_in_declared_order(self, page, live_server):
        """Next shows the following step and previous the one before."""
        page.goto(live_server.url + reverse("navigation-tour"))
        title = page.locator(TITLE)
        expect(title).to_have_text("Step 1")

        page.click(NEXT)
        expect(title).to_have_text("Step 2")
        page.click(NEXT)
        expect(title).to_have_text("Step 3")
        page.click(PREVIOUS)
        expect(title).to_have_text("Step 2")

    def test_closing_at_a_middle_step_leaves_nothing_behind(self, page, live_server):
        """Closing the tour removes everything Driver.js added."""
        page.goto(live_server.url + reverse("navigation-tour"))
        page.click(NEXT)
        expect(page.locator(TITLE)).to_have_text("Step 2")

        page.click(CLOSE)

        expect(page.locator(".driver-popover")).to_have_count(0)
        assert_no_driver_markup(page)

    def test_next_on_the_last_step_leaves_nothing_behind(self, page, live_server):
        """Finishing the tour removes everything Driver.js added."""
        page.goto(live_server.url + reverse("navigation-tour"))
        page.click(NEXT)
        page.click(NEXT)
        expect(page.locator(TITLE)).to_have_text("Step 3")

        page.click(NEXT)

        expect(page.locator(".driver-popover")).to_have_count(0)
        assert_no_driver_markup(page)
