"""Tests for the starter script, page_tours/static/page_tours/page-tours.js."""

import re

import pytest
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


class TestTourControlsLanguage:
    """The tour's own controls are in the language the page is served in."""

    def test_the_buttons_show_the_translated_labels_as_text(self, page, live_server):
        """Next, previous and done carry the page's language, markup shown as text."""
        page.goto(live_server.url + reverse("german-navigation-tour"))
        expect(page.locator(TITLE)).to_have_text("Step 1")

        assert page.locator(NEXT).text_content() == "Weiter <i>»</i>"
        page.click(NEXT)
        assert page.locator(PREVIOUS).text_content() == "Zurück"
        page.click(NEXT)
        expect(page.locator(TITLE)).to_have_text("Step 3")
        assert page.locator(NEXT).text_content() == "Fertig"

    def test_the_close_button_is_named_in_the_pages_language(self, page, live_server):
        """The close button's accessible name is the translated label, as written."""
        page.goto(live_server.url + reverse("german-navigation-tour"))

        expect(page.locator(CLOSE)).to_have_attribute(
            "aria-label", "Schließen & beenden"
        )


class TestTourSkipsSteps:
    """A step whose element cannot be shown is passed over."""

    def test_a_missing_element_is_skipped_forward_and_back(self, page, live_server):
        """Moving past a step with no element lands on its neighbours, silently."""
        problems = []
        page.on("console", lambda m: m.type == "error" and problems.append(m.text))
        page.on("pageerror", lambda error: problems.append(str(error)))
        page.goto(live_server.url + reverse("missing-middle"))
        title = page.locator(TITLE)
        expect(title).to_have_text("Step 1")

        page.click(NEXT)
        expect(title).to_have_text("Step 3")
        page.click(PREVIOUS)
        expect(title).to_have_text("Step 1")

        assert problems == []

    def test_a_hidden_element_is_skipped(self, page, live_server):
        """An element with the hidden attribute is not shown."""
        page.goto(live_server.url + reverse("hidden-middle"))
        expect(page.locator(TITLE)).to_have_text("Step 1")

        page.click(NEXT)

        expect(page.locator(TITLE)).to_have_text("Step 3")

    def test_an_invalid_selector_is_skipped(self, page, live_server):
        """A selector the browser rejects counts as a missing element."""
        page.goto(live_server.url + reverse("invalid"))
        expect(page.locator(TITLE)).to_have_text("Step 1")

        page.click(NEXT)

        expect(page.locator(TITLE)).to_have_text("Step 3")

    def test_the_tour_starts_at_the_first_showable_step(self, page, live_server):
        """With the first element missing, the second step shows first."""
        page.goto(live_server.url + reverse("missing-first"))

        expect(page.locator(TITLE)).to_have_text("Step 2")

    def test_a_tour_with_nothing_showable_does_not_play(self, page, live_server):
        """When every step names a missing element, no popover and no markup."""
        page.goto(live_server.url + reverse("nothing"))
        page.wait_for_load_state("load")

        expect(page.locator(".driver-popover")).to_have_count(0)
        assert_no_driver_markup(page)

    def test_a_tour_with_nothing_showable_never_starts_driver(self, page, live_server):
        """Driver.js is not even asked for a tour when no step could show."""
        stand_in = "window.driver = {js: {driver: () => {window.started = true;}}};"
        page.route(
            "**/driver.js.iife.js",
            lambda route: route.fulfill(body=stand_in, content_type="text/javascript"),
        )
        page.goto(live_server.url + reverse("nothing"))
        page.wait_for_load_state("load")

        assert page.evaluate("window.started") is None

    def test_a_selector_matching_two_elements_highlights_the_first(
        self, page, live_server
    ):
        """The first match carries the highlight and the second does not."""
        page.goto(live_server.url + reverse("twins"))

        expect(page.locator("#twin-first")).to_have_class(
            re.compile(r"driver-active-element")
        )
        expect(page.locator("#twin-second")).not_to_have_class(
            re.compile(r"driver-active-element")
        )


STAND_IN_THAT_FAILS = """
window.driver = {js: {driver: () => ({drive: () => {
  const overlay = document.createElement("div");
  overlay.className = "driver-overlay";
  document.body.appendChild(overlay);
  document.body.classList.add("driver-active");
  throw new Error("cannot start");
}})}};
"""


class TestTourFailure:
    """A tour that fails ends and leaves the page as usable as it was."""

    def assert_page_still_works(self, page):
        """Assert that nothing of Driver.js is left and the page's control works."""
        assert_no_driver_markup(page)
        page.click("#control")
        expect(page.locator("#output")).to_have_text("worked")

    def test_a_script_that_cannot_load_leaves_the_page_alone(self, page, live_server):
        """With the Driver.js file unreachable, the page is as it would be untoured."""
        page.route("**/driver.js.iife.js", lambda route: route.abort())
        page.goto(live_server.url + reverse("navigation-tour"))
        page.wait_for_load_state("load")

        self.assert_page_still_works(page)

    def test_a_failure_while_starting_cleans_up(self, page, live_server):
        """Driver.js adding markup and then throwing leaves none of it behind."""
        page.route(
            "**/driver.js.iife.js",
            lambda route: route.fulfill(
                body=STAND_IN_THAT_FAILS, content_type="text/javascript"
            ),
        )
        page.goto(live_server.url + reverse("navigation-tour"))
        page.wait_for_load_state("load")

        self.assert_page_still_works(page)

    def test_a_failure_while_playing_ends_the_tour(self, page, live_server):
        """A step that throws when Driver.js measures it ends the tour cleanly."""
        page.goto(live_server.url + reverse("fragile"))
        expect(page.locator(TITLE)).to_have_text("Step 1")

        page.click(NEXT)

        expect(page.locator(".driver-popover")).to_have_count(0)
        self.assert_page_still_works(page)


VISIBLE_ELEMENTS = "body *:not(script):not(link):not(style)"


class TestTourWithoutJavaScript:
    """With JavaScript off, a page with a tour looks like the page without one."""

    def layout(self, browser, url):
        """Return the body text and the box of every element in it, in order."""
        context = browser.new_context(java_script_enabled=False)
        try:
            page = context.new_page()
            page.goto(url)
            boxes = [el.bounding_box() for el in page.locator(VISIBLE_ELEMENTS).all()]
            return page.inner_text("body"), boxes
        finally:
            context.close()

    def test_the_page_is_unchanged(self, browser, live_server):
        """Text and the box of every element in the body match the untoured page."""
        with_tour = self.layout(browser, live_server.url + reverse("bare-with-tour"))
        without_tour = self.layout(
            browser, live_server.url + reverse("bare-without-tour")
        )

        assert with_tour == without_tour
        assert len(with_tour[1]) > 0


STORAGE_BLOCKED = """
Object.defineProperty(window, "localStorage", {
  get() { throw new Error("blocked"); },
});
"""

STORAGE_FULL = """
Storage.prototype.setItem = function () { throw new Error("full"); };
"""


class TestSeenTour:
    """A tour plays by itself once per browser and is then seen."""

    def assert_does_not_play(self, page):
        """Assert that the page has loaded and shows no tour."""
        page.wait_for_load_state("load")
        expect(page.locator(".driver-popover")).to_have_count(0)
        assert_no_driver_markup(page)

    def test_it_plays_the_first_time_a_browser_opens_the_page(self, page, live_server):
        """A browser with nothing remembered is shown the first step."""
        page.goto(live_server.url + reverse("navigation-tour"))

        expect(page.locator(TITLE)).to_have_text("Step 1")

    def test_it_does_not_play_again_after_the_last_step(self, page, live_server):
        """Stepping to the end and reopening the page shows nothing."""
        url = live_server.url + reverse("navigation-tour")
        page.goto(url)
        page.click(NEXT)
        page.click(NEXT)
        page.click(NEXT)
        expect(page.locator(".driver-popover")).to_have_count(0)

        page.goto(url)

        self.assert_does_not_play(page)

    def test_it_does_not_play_again_after_closing_it_midway(self, page, live_server):
        """Closing at the second step and reopening the page shows nothing."""
        url = live_server.url + reverse("navigation-tour")
        page.goto(url)
        page.click(NEXT)
        page.click(CLOSE)

        page.goto(url)

        self.assert_does_not_play(page)

    def test_it_does_not_play_again_after_leaving_it_midway(self, page, live_server):
        """Navigating away while a step shows still counts the tour as seen."""
        url = live_server.url + reverse("navigation-tour")
        page.goto(url)
        expect(page.locator(TITLE)).to_have_text("Step 1")
        page.goto(live_server.url + reverse("no-tour"))

        page.goto(url)

        self.assert_does_not_play(page)

    def test_a_page_with_a_different_tour_still_plays(self, page, live_server):
        """Seeing one tour does not hide another."""
        page.goto(live_server.url + reverse("navigation-tour"))
        expect(page.locator(TITLE)).to_have_text("Step 1")

        page.goto(live_server.url + reverse("missing-first"))

        expect(page.locator(TITLE)).to_have_text("Step 2")

    def test_one_view_on_two_addresses_is_seen_once(self, page, live_server):
        """Seeing the tour at one address hides it at the other."""
        page.goto(live_server.url + reverse("class-tour"))
        expect(page.locator(TITLE)).to_have_text(CLASS_TOUR.steps[0].title)

        page.goto(live_server.url + reverse("class-tour-again"))

        self.assert_does_not_play(page)

    def test_a_fresh_browser_plays_it_again(self, page, browser, live_server):
        """What one browser has seen, another has not."""
        url = live_server.url + reverse("navigation-tour")
        page.goto(url)
        expect(page.locator(TITLE)).to_have_text("Step 1")
        other = browser.new_context()
        try:
            other_page = other.new_page()

            other_page.goto(url)

            expect(other_page.locator(TITLE)).to_have_text("Step 1")
        finally:
            other.close()

    def test_blocked_storage_plays_the_tour_on_every_visit(self, page, live_server):
        """With storage unreadable the tour plays each time, with no page error."""
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.add_init_script(STORAGE_BLOCKED)
        url = live_server.url + reverse("navigation-tour")

        page.goto(url)
        expect(page.locator(TITLE)).to_have_text("Step 1")
        page.goto(url)

        expect(page.locator(TITLE)).to_have_text("Step 1")
        assert errors == []

    def test_full_storage_plays_the_tour_with_no_error(self, page, live_server):
        """When seen cannot be written, the tour still plays, with no page error."""
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.add_init_script(STORAGE_FULL)
        url = live_server.url + reverse("navigation-tour")

        page.goto(url)
        expect(page.locator(TITLE)).to_have_text("Step 1")
        page.goto(url)

        expect(page.locator(TITLE)).to_have_text("Step 1")
        assert errors == []

    def test_a_tour_with_nothing_showable_is_not_marked_seen(self, page, live_server):
        """The tour that could not play plays once its elements can show."""
        page.goto(live_server.url + reverse("nothing"))
        page.wait_for_load_state("load")

        keys = page.evaluate("Object.keys(localStorage)")

        assert keys == []

    def test_the_seen_tour_is_remembered_under_the_views_name(self, page, live_server):
        """The browser keeps one entry, named for the view that declares the tour."""
        page.goto(live_server.url + reverse("navigation-tour"))
        expect(page.locator(TITLE)).to_have_text("Step 1")

        keys = page.evaluate("Object.keys(localStorage)")

        assert keys == ["page-tours:seen:tests.views.NavigationTourView"]


REPLAY = "#replay"


class TestReplay:
    """A control the developer places plays the tour again from its first step."""

    def open_and_close(self, page, url):
        """Open the page, let the first play start, and close it."""
        page.goto(url)
        expect(page.locator(TITLE)).to_have_text("Step 1")
        page.click(CLOSE)
        expect(page.locator(".driver-popover")).to_have_count(0)

    def test_the_control_plays_a_seen_tour_from_the_first_step(self, page, live_server):
        """Using the control on a seen tour shows step one."""
        self.open_and_close(page, live_server.url + reverse("replay"))

        page.click(REPLAY)

        expect(page.locator(TITLE)).to_have_text("Step 1")

    def test_the_live_button_carries_only_the_developers_attributes(
        self, page, live_server
    ):
        """The button the script builds has no class, style or attribute of its own."""
        page.goto(live_server.url + reverse("replay"))
        page.wait_for_load_state("load")

        names = page.evaluate(
            '() => [...document.querySelector("#replay").attributes]'
            ".map((attribute) => attribute.name).sort()"
        )
        classes = page.evaluate(
            '() => [...document.querySelector("#replay").classList]'
        )
        assert names == sorted(["aria-label", "class", "data-x", "id", "title", "type"])
        assert classes == ["mine"]

    def test_the_control_starts_the_tour_again_after_it_ends(self, page, live_server):
        """After the last step, nothing is left and the control plays it again."""
        page.goto(live_server.url + reverse("replay"))
        page.click(NEXT)
        page.click(NEXT)
        expect(page.locator(".driver-popover")).to_have_count(0)
        assert_no_driver_markup(page)

        page.click(REPLAY)

        expect(page.locator(TITLE)).to_have_text("Step 1")

    def test_the_control_starts_the_tour_again_after_a_close(self, page, live_server):
        """After a close, nothing is left and the control plays it again."""
        self.open_and_close(page, live_server.url + reverse("replay"))
        assert_no_driver_markup(page)

        page.click(REPLAY)

        expect(page.locator(TITLE)).to_have_text("Step 1")

    def test_a_replay_that_ends_leaves_nothing_behind(self, page, live_server):
        """Closing a replayed tour removes everything Driver.js added."""
        self.open_and_close(page, live_server.url + reverse("replay"))
        page.click(REPLAY)
        expect(page.locator(TITLE)).to_have_text("Step 1")

        page.click(CLOSE)

        expect(page.locator(".driver-popover")).to_have_count(0)
        assert_no_driver_markup(page)

    def test_a_replay_does_not_make_the_tour_play_on_the_next_visit(
        self, page, live_server
    ):
        """Seen stays seen: reopening after a replay shows nothing."""
        url = live_server.url + reverse("replay")
        self.open_and_close(page, url)
        page.click(REPLAY)
        page.click(CLOSE)

        page.goto(url)

        page.wait_for_load_state("load")
        expect(page.locator(REPLAY)).to_be_visible()
        expect(page.locator(".driver-popover")).to_have_count(0)
        assert_no_driver_markup(page)

    def test_the_control_is_a_button_in_the_page_and_the_template_is_gone(
        self, page, live_server
    ):
        """The script swaps the template for its button."""
        page.goto(live_server.url + reverse("replay"))

        expect(page.locator(REPLAY)).to_have_count(1)
        expect(page.locator("template[data-page-tour-replay]")).to_have_count(0)

    def test_with_javascript_off_no_control_is_visible(self, browser, live_server):
        """The control exists only where the script can make it work."""
        context = browser.new_context(java_script_enabled=False)
        try:
            page = context.new_page()
            page.goto(live_server.url + reverse("replay"))

            expect(page.locator(REPLAY)).to_have_count(0)
            expect(page.locator("button:visible")).to_have_count(1)
        finally:
            context.close()

    def test_the_control_is_reached_and_pressed_with_the_keyboard(
        self, page, live_server
    ):
        """Tab reaches the button, Enter starts the tour."""
        self.open_and_close(page, live_server.url + reverse("replay"))
        for _ in range(5):
            page.keyboard.press("Tab")
            if page.evaluate("document.activeElement.id") == "replay":
                break
        expect(page.locator(REPLAY)).to_be_focused()

        page.keyboard.press("Enter")

        expect(page.locator(TITLE)).to_have_text("Step 1")

    def test_using_it_on_a_tour_with_nothing_showable_does_nothing(
        self, page, live_server
    ):
        """No Driver.js markup and no page error."""
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.goto(live_server.url + reverse("replay-nothing"))

        page.click(REPLAY)

        expect(page.locator(".driver-popover")).to_have_count(0)
        assert_no_driver_markup(page)
        assert errors == []

    def test_two_controls_each_start_the_tour(self, page, live_server):
        """Each placement of the control works."""
        self.open_and_close(page, live_server.url + reverse("replay-twice"))
        controls = page.locator(".replay-control")
        expect(controls).to_have_count(2)

        controls.nth(0).click()
        expect(page.locator(TITLE)).to_have_text("Step 1")
        page.click(CLOSE)
        expect(page.locator(".driver-popover")).to_have_count(0)
        controls.nth(1).click()

        expect(page.locator(TITLE)).to_have_text("Step 1")

    def test_a_step_can_point_at_the_control_and_using_it_restarts_the_tour(
        self, page, live_server
    ):
        """On a first open the control exists for a step; using it restarts."""
        page.goto(live_server.url + reverse("replay-pointed-at"))
        expect(page.locator(TITLE)).to_have_text("Step 1")
        page.click(NEXT)
        expect(page.locator(TITLE)).to_have_text("Step 2")
        expect(page.locator(REPLAY)).to_have_class(re.compile("driver-active-element"))

        page.click(REPLAY)

        expect(page.locator(TITLE)).to_have_text("Step 1")
        expect(page.locator(".driver-popover")).to_have_count(1)


class TestTourWithTheKeyboard:
    """Focus goes back to where it was when a tour ends, at any step."""

    def press_next(self, page):
        """Move to the next step from the keyboard, with Enter on the next button."""
        page.focus(NEXT)
        page.keyboard.press("Enter")

    def start_from_the_control(self, page, live_server):
        """Open the replay page, close its first play, and start it from the control."""
        page.goto(live_server.url + reverse("replay"))
        expect(page.locator(TITLE)).to_have_text("Step 1")
        page.keyboard.press("Escape")
        expect(page.locator(".driver-popover")).to_have_count(0)
        page.focus(REPLAY)
        page.keyboard.press("Enter")
        expect(page.locator(TITLE)).to_have_text("Step 1")

    def test_escape_on_a_later_step_returns_focus_to_the_control(
        self, page, live_server
    ):
        """Moving on a step and then pressing Escape puts focus back on the control."""
        self.start_from_the_control(page, live_server)
        self.press_next(page)
        expect(page.locator(TITLE)).to_have_text("Step 2")

        page.keyboard.press("Escape")

        expect(page.locator(".driver-popover")).to_have_count(0)
        expect(page.locator(REPLAY)).to_be_focused()

    def test_finishing_the_tour_returns_focus_to_the_control(self, page, live_server):
        """Going past the last step puts focus back on the control."""
        self.start_from_the_control(page, live_server)
        self.press_next(page)
        expect(page.locator(TITLE)).to_have_text("Step 2")

        self.press_next(page)

        expect(page.locator(".driver-popover")).to_have_count(0)
        expect(page.locator(REPLAY)).to_be_focused()

    def test_a_failure_on_a_later_step_returns_focus_to_the_control(
        self, page, live_server
    ):
        """A tour ended by a page error still puts focus back on the control."""
        self.start_from_the_control(page, live_server)
        self.press_next(page)
        expect(page.locator(TITLE)).to_have_text("Step 2")

        page.evaluate("setTimeout(() => { throw new Error('boom'); })")

        expect(page.locator(".driver-popover")).to_have_count(0)
        expect(page.locator(REPLAY)).to_be_focused()


class TestTourVersion:
    """A tour declared with a new version plays once more for a browser that saw it."""

    SEEN_KEY = "page-tours:seen:tests.views.VersionedTourView"

    def assert_does_not_play(self, page):
        """Assert that the page has loaded and shows no tour."""
        page.wait_for_load_state("load")
        expect(page.locator(".driver-popover")).to_have_count(0)
        assert_no_driver_markup(page)

    def see(self, page, url):
        """Open the page and wait for its tour to show, so the browser has seen it."""
        page.goto(url)
        expect(page.locator(TITLE)).to_have_text("Step 1")

    def test_a_new_version_plays_for_a_browser_that_saw_the_old_one(
        self, page, live_server
    ):
        """Seeing version 1 does not hide version 2."""
        self.see(page, live_server.url + reverse("versioned"))

        page.goto(live_server.url + reverse("versioned-two"))

        expect(page.locator(TITLE)).to_have_text("Step 1")

    def test_the_new_version_plays_only_once(self, page, live_server):
        """Once version 2 has played, it stays quiet."""
        self.see(page, live_server.url + reverse("versioned"))
        self.see(page, live_server.url + reverse("versioned-two"))

        page.goto(live_server.url + reverse("versioned-two"))

        self.assert_does_not_play(page)

    def test_an_edit_that_keeps_the_version_does_not_play_again(
        self, page, live_server
    ):
        """Changing a step's text without a new version brings nobody the tour."""
        self.see(page, live_server.url + reverse("versioned-two"))

        page.goto(live_server.url + reverse("versioned-two-edited"))

        self.assert_does_not_play(page)

    def test_a_lower_version_plays_once_more(self, page, live_server):
        """A browser that saw version 2 plays version 1 again, once."""
        self.see(page, live_server.url + reverse("versioned-two"))

        self.see(page, live_server.url + reverse("versioned"))
        page.goto(live_server.url + reverse("versioned"))

        self.assert_does_not_play(page)

    def test_a_tour_seen_before_versions_counts_as_seen_at_version_one(
        self, page, live_server
    ):
        """The entry a browser kept before tours had versions still hides version 1."""
        page.goto(live_server.url + reverse("no-tour"))
        page.evaluate(f"localStorage.setItem({self.SEEN_KEY!r}, '1')")

        page.goto(live_server.url + reverse("versioned"))

        self.assert_does_not_play(page)

    def test_the_browser_remembers_the_version_it_played(self, page, live_server):
        """The one entry for the tour holds the version that played."""
        self.see(page, live_server.url + reverse("versioned-two"))

        stored = page.evaluate("({...localStorage})")

        assert stored == {self.SEEN_KEY: "2"}

    def test_a_new_version_of_a_tour_on_request_still_waits_for_the_control(
        self, page, live_server
    ):
        """A new version does not make a tour that plays only on request autoplay."""
        page.goto(live_server.url + reverse("on-request"))
        page.click(REPLAY)
        expect(page.locator(TITLE)).to_have_text("Step 1")

        page.goto(live_server.url + reverse("on-request-two"))

        self.assert_does_not_play(page)


class TestOnRequestTour:
    """A tour declared with ``autoplay=False`` plays only when asked."""

    def assert_does_not_play(self, page):
        """Assert that the page has loaded and shows no tour."""
        page.wait_for_load_state("load")
        expect(page.locator(".driver-popover")).to_have_count(0)
        assert_no_driver_markup(page)

    def test_a_fresh_browser_does_not_play_it(self, page, live_server):
        """Opening the page for the first time shows no tour."""
        page.goto(live_server.url + reverse("on-request"))

        self.assert_does_not_play(page)

    def test_the_control_plays_it_from_the_first_step(self, page, live_server):
        """Using the control shows step one."""
        page.goto(live_server.url + reverse("on-request"))

        page.click(REPLAY)

        expect(page.locator(TITLE)).to_have_text("Step 1")

    def test_with_no_control_it_never_plays_and_raises_no_error(
        self, page, live_server
    ):
        """No Driver.js markup appears and the page has no page error."""
        errors = []
        page.on("pageerror", lambda error: errors.append(error))

        page.goto(live_server.url + reverse("on-request-no-control"))

        self.assert_does_not_play(page)
        assert errors == []

    def test_with_no_control_an_ordinary_tour_still_plays_once(self, page, live_server):
        """A tour that autoplays does not need the control."""
        page.goto(live_server.url + reverse("bare-with-tour"))

        expect(page.locator(TITLE)).to_have_text("Step 1")


class TestOverriddenTourSeen:
    """A project's replacement of a tour does not bring back a tour already seen."""

    OVERRIDDEN = "tests.views.OverriddenTourView"

    def replace_with(self, settings, replacement):
        """Replace the app's tour with a module constant of the tests."""
        settings.PAGE_TOURS_OVERRIDES = {self.OVERRIDDEN: f"tests.views.{replacement}"}

    def see_the_app_tour(self, page, live_server):
        """Open the page before the project changes its tour, so the app's is seen."""
        page.goto(live_server.url + reverse("overridden"))
        expect(page.locator(TITLE)).to_have_text("Step 1")

    def test_a_replacement_at_version_one_does_not_play_by_itself(
        self, page, live_server, settings
    ):
        """A browser that saw the app's version 2 is not shown the replacement."""
        self.see_the_app_tour(page, live_server)
        self.replace_with(settings, "REPLACEMENT_TOUR")

        page.goto(live_server.url + reverse("overridden"))

        page.wait_for_load_state("load")
        expect(page.locator(".driver-popover")).to_have_count(0)

    def test_the_replay_control_plays_the_replacement(
        self, page, live_server, settings
    ):
        """What was not shown by itself is there when asked for."""
        self.see_the_app_tour(page, live_server)
        self.replace_with(settings, "REPLACEMENT_TOUR")
        page.goto(live_server.url + reverse("overridden"))

        page.click(REPLAY)

        expect(page.locator(TITLE)).to_have_text("Ours 1")

    def test_a_replacement_at_version_two_plays_by_itself_once(
        self, page, live_server, settings
    ):
        """Raising the replacement's version shows it once more, and only once."""
        self.see_the_app_tour(page, live_server)
        self.replace_with(settings, "REPLACEMENT_TOUR_VERSION_TWO")
        page.goto(live_server.url + reverse("overridden"))
        expect(page.locator(TITLE)).to_have_text("Ours 1")

        page.goto(live_server.url + reverse("overridden"))

        page.wait_for_load_state("load")
        expect(page.locator(".driver-popover")).to_have_count(0)


class TestOwnLook:
    """The tour's stylesheet sits where a site's own rules can override it."""

    def test_the_packages_link_is_first_in_the_head_once_the_tour_shows(
        self, page, live_server
    ):
        """The page's own styles come after the package's link."""
        page.goto(live_server.url + reverse("class-tour"))
        expect(page.locator(TITLE)).to_be_visible()

        first = page.evaluate(
            """() => document.head.querySelector("link, style")
                .hasAttribute("data-page-tour-stylesheet")"""
        )
        assert first is True

    def test_every_rule_reachable_from_the_packages_sheet_is_driverjs(
        self, page, live_server
    ):
        """The package's sheet is one import of driver.css into its own layer."""
        page.goto(live_server.url + reverse("class-tour"))
        expect(page.locator(TITLE)).to_be_visible()

        imports = page.evaluate(
            """() => {
                const link = document.querySelector("link[data-page-tour-stylesheet]");
                return [...link.sheet.cssRules].map((rule) => ({
                    layer: rule.layerName,
                    href: rule.styleSheet && rule.styleSheet.href,
                }));
            }"""
        )
        assert len(imports) == 1
        assert imports[0]["layer"] == "page-tours"
        assert imports[0]["href"].endswith("driver.css")


PART_SELECTORS = {
    "box": ".driver-popover",
    "title": ".driver-popover-title",
    "text": ".driver-popover-description",
    "progress": ".driver-popover-progress-text",
    "previous": ".driver-popover-prev-btn",
    "next": ".driver-popover-next-btn",
    "close": ".driver-popover-close-btn",
    "highlight": "svg.driver-overlay",
}
SITE_CLASSES = {part: f"site-{part}" for part in [*PART_SELECTORS, "done"]}


def classes_of(page, selector):
    """Return the class tokens of the first element matching a selector."""
    return page.evaluate(
        "(selector) => [...document.querySelector(selector).classList]", selector
    )


def press_until_titled(page, key, title):
    """Press a key until the step with the given title shows.

    Driver.js ignores the arrow keys while a step is still moving in, so the
    press is repeated until the step arrives.
    """
    for _ in range(20):
        page.keyboard.press(key)
        try:
            expect(page.locator(TITLE)).to_have_text(title, timeout=250)
        except AssertionError:
            continue
        return
    expect(page.locator(TITLE)).to_have_text(title)


class TestPartNames:
    """Every part of a shown step carries its documented name and its classes."""

    @pytest.fixture
    def site_classes(self, settings):
        """Configure a class of the site's own for every part."""
        settings.PAGE_TOURS_CLASSES = SITE_CLASSES

    def assert_parts_named(self, page):
        """Assert every part on the page carries its name and configured class."""
        for part, selector in PART_SELECTORS.items():
            tokens = classes_of(page, selector)
            assert f"page-tour-{part}" in tokens, part
            assert f"site-{part}" in tokens, part

    @pytest.mark.usefixtures("site_classes")
    def test_each_part_of_an_attached_step_carries_its_name(self, page, live_server):
        """On a step attached to an element, every part is named and classed."""
        page.goto(live_server.url + reverse("parts-tour"))
        expect(page.locator(TITLE)).to_have_text("Step 1")

        self.assert_parts_named(page)

    @pytest.mark.usefixtures("site_classes")
    def test_an_unattached_step_carries_the_same_names(self, page, live_server):
        """A step attached to nothing names and classes its parts the same way."""
        page.goto(live_server.url + reverse("parts-tour"))
        page.click(NEXT)
        expect(page.locator(TITLE)).to_have_text("Step 2")

        self.assert_parts_named(page)

    @pytest.mark.usefixtures("site_classes")
    def test_the_controls_carry_their_names_on_every_step(self, page, live_server):
        """Previous is named while disabled, next in the middle, done at the end."""
        page.goto(live_server.url + reverse("parts-tour"))
        expect(page.locator(PREVIOUS)).to_be_disabled()
        assert "page-tour-previous" in classes_of(page, PREVIOUS)
        assert "site-previous" in classes_of(page, PREVIOUS)

        page.click(NEXT)
        expect(page.locator(TITLE)).to_have_text("Step 2")
        assert "page-tour-next" in classes_of(page, NEXT)
        assert "site-next" in classes_of(page, NEXT)

        page.click(NEXT)
        expect(page.locator(TITLE)).to_have_text("Step 3")
        last = classes_of(page, NEXT)
        assert "page-tour-done" in last
        assert "site-done" in last
        assert "page-tour-next" not in last
        assert "site-next" not in last

    @pytest.mark.usefixtures("site_classes")
    def test_a_configured_class_is_on_exactly_its_part_on_every_step(
        self, page, live_server
    ):
        """One element carries each configured class, on each of the three steps."""
        page.goto(live_server.url + reverse("parts-tour"))
        for number in (1, 2, 3):
            expect(page.locator(TITLE)).to_have_text(f"Step {number}")
            for part in ("box", "title", "text", "close", "highlight"):
                assert page.locator(f".site-{part}").count() == 1, (number, part)
            page.click(NEXT)

    @pytest.mark.usefixtures("site_classes")
    def test_classes_on_the_controls_leave_the_keyboard_alone(self, page, live_server):
        """Names stay, Tab reaches next, Enter and the arrows move, Escape ends."""
        page.goto(live_server.url + reverse("parts-tour"))
        title = page.locator(TITLE)
        expect(title).to_have_text("Step 1")
        label = page.evaluate(
            """() => JSON.parse(
                document.getElementById("page-tour-steps").textContent
            ).controls.close"""
        )
        expect(page.locator(CLOSE)).to_have_attribute("aria-label", label)

        page.focus(CLOSE)
        page.keyboard.press("Tab")
        expect(page.locator(NEXT)).to_be_focused()
        page.keyboard.press("Enter")
        expect(title).to_have_text("Step 2")
        press_until_titled(page, "ArrowRight", "Step 3")
        press_until_titled(page, "ArrowLeft", "Step 2")
        page.keyboard.press("Escape")

        expect(page.locator(".driver-popover")).to_have_count(0)

    @pytest.mark.usefixtures("site_classes")
    def test_a_replayed_tour_carries_the_same_names(self, page, live_server):
        """Closing the tour and starting it from the replay control names its parts."""
        page.goto(live_server.url + reverse("replay"))
        expect(page.locator(TITLE)).to_have_text("Step 1")
        page.click(CLOSE)
        expect(page.locator(".driver-popover")).to_have_count(0)

        page.click("#replay")

        expect(page.locator(TITLE)).to_have_text("Step 1")
        self.assert_parts_named(page)

    def test_with_no_setting_no_class_of_the_sites_appears(self, page, live_server):
        """Without configuration, every class in the tour is the package's or Driver's."""
        page.goto(live_server.url + reverse("parts-tour"))
        for number in (1, 2, 3):
            expect(page.locator(TITLE)).to_have_text(f"Step {number}")
            foreign = page.evaluate(
                """() => [
                    ...document.querySelectorAll(
                        ".driver-popover, .driver-popover *, svg.driver-overlay, "
                        + "svg.driver-overlay *"
                    ),
                ].flatMap((el) => [...el.classList]).filter(
                    (name) => !name.startsWith("driver-")
                        && !name.startsWith("page-tour-")
                )"""
            )
            assert foreign == []
            page.click(NEXT)

    @pytest.mark.usefixtures("site_classes")
    def test_a_failure_while_naming_a_part_ends_the_tour(self, page, live_server):
        """When adding a class throws, the tour ends without a page error."""
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.add_init_script(
            """
            const add = DOMTokenList.prototype.add;
            DOMTokenList.prototype.add = function (...tokens) {
              if (tokens.includes("page-tour-title")) {
                throw new Error("cannot add");
              }
              return add.apply(this, tokens);
            };
            """
        )
        page.goto(live_server.url + reverse("parts-tour"))
        page.wait_for_load_state("load")

        expect(page.locator(".driver-popover")).to_have_count(0)
        assert_no_driver_markup(page)
        assert errors == []
