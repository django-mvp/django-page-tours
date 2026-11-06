"""The demo project's pages, asserted as rendered."""

import pytest
from django.core.management import call_command
from django.urls import reverse

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
