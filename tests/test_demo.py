"""The demo project's pages, asserted as rendered."""

import json
import re

import pytest
from django.core.management import call_command
from django.urls import reverse
from playwright.sync_api import expect

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
        return json.loads(match.group(1))

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
