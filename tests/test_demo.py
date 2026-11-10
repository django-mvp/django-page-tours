"""The demo project's pages, asserted as rendered."""

import json
import re

import pytest
from django.core.checks import run_checks
from django.core.management import call_command
from django.urls import reverse
from playwright.sync_api import expect

from demo import settings as demo_settings
from demo.library.views import BookDetailView, BookListView
from demo.tours import book_tour
from page_tours.parts import TourParts

pytestmark = pytest.mark.urls("demo.urls")


class TestOverviewPage:
    """The demo project's landing page."""

    def test_it_responds(self, client):
        """The page renders for an anonymous visitor."""
        assert client.get(reverse("overview")).status_code == 200

    def test_it_links_itself_from_the_page_bar(self, client):
        """The bar every demo page shares links the overview."""
        page = client.get(reverse("overview")).content.decode()
        bar = page.split('aria-label="Demo pages"', 1)[1].split("</nav>", 1)[0]
        assert f'href="{reverse("overview")}"' in bar


class TestTourPage:
    """The demo page that carries a tour."""

    def steps(self, page):
        """Return the steps the page hands to the browser."""
        match = re.search(
            r'<script id="page-tour-steps" type="application/json">(.*?)</script>',
            page,
            re.DOTALL,
        )
        return json.loads(match.group(1))["steps"]

    def test_it_responds(self, client):
        """The page renders for an anonymous visitor."""
        assert client.get(reverse("tour")).status_code == 200

    def test_it_is_linked_from_the_page_bar(self, client):
        """The bar every demo page shares links the tour page."""
        page = client.get(reverse("overview")).content.decode()
        bar = page.split('aria-label="Demo pages"', 1)[1].split("</nav>", 1)[0]
        assert f'href="{reverse("tour")}"' in bar

    def test_its_tour_has_a_step_attached_to_an_element_on_the_page(self, client):
        """A step names an element that is in the page's HTML."""
        page = client.get(reverse("tour")).content.decode()
        selectors = [s["element"] for s in self.steps(page) if "element" in s]
        assert any(f'id="{s.removeprefix("#")}"' in page for s in selectors)

    def test_its_tour_has_a_step_attached_to_nothing(self, client):
        """A step carries no element key."""
        page = client.get(reverse("tour")).content.decode()
        assert any("element" not in s for s in self.steps(page))

    def test_its_tour_has_a_step_whose_element_is_not_on_the_page(self, client):
        """A step names an element the page does not contain."""
        page = client.get(reverse("tour")).content.decode()
        selectors = [s["element"] for s in self.steps(page) if "element" in s]
        assert any(f'id="{s.removeprefix("#")}"' not in page for s in selectors)


class TestDemoTourPages:
    """The demo pages that show how a tour is started and when it plays again."""

    PAGES = ["plays-once", "on-request", "changed-tour", "function-view"]

    def payload(self, page):
        """Return the payload the page hands to the browser."""
        match = re.search(
            r'<script id="page-tour-steps" type="application/json">(.*?)</script>',
            page,
            re.DOTALL,
        )
        return json.loads(match.group(1))

    def bar(self, page):
        """Return the markup of the page bar."""
        return page.split('aria-label="Demo pages"', 1)[1].split("</nav>", 1)[0]

    @pytest.mark.parametrize("name", PAGES)
    def test_the_page_responds_and_carries_a_tour(self, client, name):
        """Each page renders for an anonymous visitor with a tour on it."""
        response = client.get(reverse(name))

        assert response.status_code == 200
        assert 'id="page-tour-steps"' in response.content.decode()

    def test_the_plays_once_page_plays_by_itself(self, client):
        """Its payload says the tour autoplays."""
        page = client.get(reverse("plays-once")).content.decode()

        assert self.payload(page)["autoplay"] is True

    def test_the_on_request_page_does_not_play_by_itself(self, client):
        """Its payload says the tour does not autoplay."""
        page = client.get(reverse("on-request")).content.decode()

        assert self.payload(page)["autoplay"] is False

    def test_the_changed_tour_is_routed_at_two_versions_of_one_tour(self, client):
        """Both addresses carry the same tour name, at versions 1 and 2."""
        first = self.payload(client.get(reverse("changed-tour")).content.decode())
        new = self.payload(
            client.get(reverse("changed-tour-new-version")).content.decode()
        )

        assert first["id"] == new["id"]
        assert (first["version"], new["version"]) == (1, 2)

    @pytest.mark.parametrize("name", PAGES)
    def test_the_page_bar_links_the_page(self, client, name):
        """The bar every demo page shares links each of them."""
        page = client.get(reverse("overview")).content.decode()

        assert f'href="{reverse(name)}"' in self.bar(page)

    @pytest.mark.parametrize("name", PAGES)
    def test_the_overview_links_the_page(self, client, name):
        """The overview names each of them outside the page bar."""
        page = client.get(reverse("overview")).content.decode()

        assert f'href="{reverse(name)}"' in page.split("</nav>", 1)[1]

    @pytest.mark.parametrize("name", [*PAGES, "overview"])
    def test_the_page_bar_carries_a_hidden_replay_control(self, client, name):
        """The control placed once in the base template waits, hidden, for the script."""
        page = client.get(reverse(name)).content.decode()

        assert "data-page-tour-replay hidden" in self.bar(page)

    @pytest.mark.parametrize("name", PAGES)
    def test_a_tour_page_carries_the_script_that_shows_the_control(self, client, name):
        """A page with a tour loads the script that takes ``hidden`` off the control."""
        page = client.get(reverse(name)).content.decode()

        assert "page-tours.js" in page

    def test_the_overview_does_not_carry_the_script(self, client):
        """A page with no tour never loads the script, so its control stays hidden."""
        page = client.get(reverse("overview")).content.decode()

        assert "page-tours.js" not in page

    def test_the_on_request_page_places_a_second_control_in_its_body(self, client):
        """The page carries two controls: the bar's and its own."""
        page = client.get(reverse("on-request")).content.decode()

        assert page.count("data-page-tour-replay") == 2


class TestLibraryPages:
    """The demo pages of an installed app whose tours the project changed."""

    PAGES = ["library-books", "library-book", "library-loans"]

    @pytest.fixture(autouse=True)
    def project_overrides(self, settings):
        """Set the demo's own overrides, which the test settings do not carry."""
        settings.PAGE_TOURS_OVERRIDES = demo_settings.PAGE_TOURS_OVERRIDES

    def payload(self, page):
        """Return the payload the page hands to the browser."""
        match = re.search(
            r'<script id="page-tour-steps" type="application/json">(.*?)</script>',
            page,
            re.DOTALL,
        )
        return json.loads(match.group(1))

    def bar(self, page):
        """Return the markup of the page bar."""
        return page.split('aria-label="Demo pages"', 1)[1].split("</nav>", 1)[0]

    @pytest.mark.parametrize("name", PAGES)
    def test_the_page_responds(self, client, name):
        """Each page renders for an anonymous visitor."""
        assert client.get(reverse(name)).status_code == 200

    def test_the_book_list_plays_the_steps_the_app_declared(self, client):
        """Its payload is the app's own tour."""
        page = client.get(reverse("library-books")).content.decode()

        assert self.payload(page)["steps"] == BookListView.tour.as_driver_steps()

    def test_the_book_page_plays_the_projects_replacement(self, client):
        """Its payload carries the replacement's steps under the app tour's name."""
        payload = self.payload(client.get(reverse("library-book")).content.decode())

        assert payload["steps"] == book_tour.as_driver_steps()
        assert payload["id"] == BookDetailView.tour.name

    def test_the_replacement_differs_from_the_apps_tour(self):
        """The project reworded a step, so the two tours are not the same."""
        assert book_tour.as_driver_steps() != BookDetailView.tour.as_driver_steps()

    def test_the_loans_page_has_no_tour_payload(self, client):
        """The project turned its tour off."""
        page = client.get(reverse("library-loans")).content.decode()

        assert 'id="page-tour-steps"' not in page

    def test_the_loans_page_does_not_show_the_replay_control(self, client):
        """With no tour the script is not loaded, so the bar's control stays hidden."""
        page = client.get(reverse("library-loans")).content.decode()

        assert "data-page-tour-replay hidden" in self.bar(page)
        assert "page-tours.js" not in page

    @pytest.mark.parametrize("name", ["library-books", "library-book"])
    def test_every_step_with_an_element_points_at_the_page(self, client, name):
        """The markup each step points at is in the page."""
        page = client.get(reverse(name)).content.decode()
        selectors = [
            s["element"] for s in self.payload(page)["steps"] if "element" in s
        ]

        assert selectors
        assert all(f'id="{s.removeprefix("#")}"' in page for s in selectors)

    @pytest.mark.parametrize("name", PAGES)
    def test_the_overview_links_the_page(self, client, name):
        """The overview names each of them outside the page bar."""
        page = client.get(reverse("overview")).content.decode()

        assert f'href="{reverse(name)}"' in page.split("</nav>", 1)[1]

    def test_the_page_bar_links_the_book_list(self, client):
        """The bar every demo page shares links the library."""
        page = client.get(reverse("overview")).content.decode()

        assert f'href="{reverse("library-books")}"' in self.bar(page)

    def test_the_demo_raises_no_page_tours_warning(self):
        """Both override keys name declared tours, and no two tours share a name.

        The test suite's own tours declare a name twice on purpose, so only the
        warnings about the demo's tours are read.
        """
        found = [
            m
            for m in run_checks()
            if m.id.startswith("page_tours.")
            and str(m.obj).partition(".")[0] in {"demo", "library"}
        ]

        assert found == []


class TestTourPageInBrowser:
    """A visitor walks the demo tour and then uses the page."""

    def test_the_tour_walks_and_the_page_keeps_working(self, page, live_server):
        """Three steps show, the missing one is skipped, and the page stays usable."""
        title = page.locator(".driver-popover-title")
        page.goto(live_server.url + reverse("tour"))
        shown = [title.text_content()]
        for _ in range(2):
            page.click(".driver-popover-next-btn")
            expect(title).not_to_have_text(shown[-1])
            shown.append(title.text_content())
        assert len(set(shown)) == 3
        assert shown[2] != "An element that is not here"

        page.click(".driver-popover-prev-btn")
        page.click(".driver-popover-prev-btn")
        expect(title).to_have_text(shown[0])

        page.click(".driver-popover-next-btn")
        expect(title).to_have_text(shown[1])
        page.click("#demo-disclosure summary")
        expect(page.locator("#demo-disclosure")).to_have_attribute("open", "")

        page.click(".driver-popover-next-btn")
        expect(title).to_have_text(shown[2])
        page.locator(".driver-overlay").click(position={"x": 5, "y": 5})
        expect(page.locator(".driver-popover")).to_have_count(0)

        page.fill("#demo-field", "Ada")
        page.press("#demo-field", "Enter")
        page.wait_for_url(re.compile(r"\?name=Ada$"))


@pytest.mark.django_db
class TestSeedDemo:
    """The command that creates the demo's sign-in accounts."""

    def test_it_creates_the_three_accounts(self, django_user_model, settings):
        """One regular, one staff and one superuser account exist afterwards."""
        settings.DEBUG = True
        call_command("seed_demo", stdout=None)
        users = django_user_model.objects.order_by("username")
        assert [(u.username, u.is_staff, u.is_superuser) for u in users] == [
            ("regular.user@example.com", False, False),
            ("staff.user@example.com", True, False),
            ("super.user@example.com", True, True),
        ]

    def test_it_refuses_without_debug(self, settings):
        """Accounts with a known password are never created on a deployed site."""
        settings.DEBUG = False
        with pytest.raises(Exception, match="only runs with DEBUG on"):
            call_command("seed_demo")


class TestOwnLookPage:
    """The demo page that shows a tour with a look of its own."""

    def payload(self, page):
        """Return the payload the page hands to the browser."""
        match = re.search(
            r'<script id="page-tour-steps" type="application/json">(.*?)</script>',
            page,
            re.DOTALL,
        )
        return json.loads(match.group(1))

    def test_it_responds_and_carries_a_tour(self, client):
        """The page renders for an anonymous visitor with a tour on it."""
        response = client.get(reverse("own-look"))

        assert response.status_code == 200
        assert 'id="page-tour-steps"' in response.content.decode()

    def test_its_tour_has_a_step_attached_to_nothing(self, client):
        """A step carries no element key."""
        page = client.get(reverse("own-look")).content.decode()

        assert any("element" not in s for s in self.payload(page)["steps"])

    def test_its_tour_has_a_step_attached_to_an_element_on_the_page(self, client):
        """A step names an element that is in the page's HTML."""
        page = client.get(reverse("own-look")).content.decode()
        selectors = [
            s["element"] for s in self.payload(page)["steps"] if "element" in s
        ]

        assert any(f'id="{s.removeprefix("#")}"' in page for s in selectors)

    def test_its_payload_carries_the_classes_for_the_parts(self, client):
        """The payload has a list of class tokens for every part."""
        page = client.get(reverse("own-look")).content.decode()

        assert set(self.payload(page)["parts"]) == set(TourParts.parts)

    def test_the_demos_configured_classes_reach_the_payload(self, client, settings):
        """The classes the demo settings configure are on their parts in the payload."""
        settings.PAGE_TOURS_CLASSES = demo_settings.PAGE_TOURS_CLASSES

        page = client.get(reverse("own-look")).content.decode()

        parts = self.payload(page)["parts"]
        assert "demo-next" in parts["next"]
        assert "demo-box" in parts["box"]

    def test_the_page_bar_links_the_page(self, client):
        """The bar every demo page shares links it."""
        page = client.get(reverse("overview")).content.decode()
        bar = page.split('aria-label="Demo pages"', 1)[1].split("</nav>", 1)[0]

        assert f'href="{reverse("own-look")}"' in bar

    def test_the_overview_links_the_page(self, client):
        """The overview names it outside the page bar."""
        page = client.get(reverse("overview")).content.decode()

        assert f'href="{reverse("own-look")}"' in page.split("</nav>", 1)[1]
