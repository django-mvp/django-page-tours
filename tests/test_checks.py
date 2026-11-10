"""Tests for page_tours.checks."""

import copy

import pytest
from django.core.checks import run_checks

REQUEST_PROCESSOR = "django.template.context_processors.request"


def check_ids():
    """Return the ids of the issues the system checks raise."""
    return {issue.id for issue in run_checks()}


class TestRequestContextProcessorCheck:
    """The warning for a project whose templates cannot see the request."""

    def test_it_warns_when_the_request_processor_is_missing(self, settings):
        """Without the processor a function-based view's tour cannot be found."""
        templates = copy.deepcopy(settings.TEMPLATES)
        templates[0]["OPTIONS"]["context_processors"].remove(REQUEST_PROCESSOR)
        settings.TEMPLATES = templates

        assert "page_tours.W001" in check_ids()

    def test_it_is_silent_when_the_request_processor_is_listed(self, settings):
        """A project with the processor gets no warning."""
        assert (
            REQUEST_PROCESSOR in settings.TEMPLATES[0]["OPTIONS"]["context_processors"]
        )

        assert "page_tours.W001" not in check_ids()

    def test_it_warns_when_no_django_templates_backend_is_configured(self, settings):
        """Another template engine alone cannot supply the processor."""
        settings.TEMPLATES = [
            {"BACKEND": "django.template.backends.dummy.TemplateStrings", "DIRS": []}
        ]

        assert "page_tours.W001" in check_ids()


def overrides_warnings():
    """Return the issues of the overrides check, by the key each is about."""
    return {issue.obj: issue for issue in run_checks() if issue.id == "page_tours.W002"}


class TestOverridesCheck:
    """The warning for a setting key that no routed view declares."""

    @pytest.fixture(autouse=True)
    def urls(self, settings):
        """Route the views that declare tours in the app-like test module."""
        settings.ROOT_URLCONF = "tests.urls_checks"

    def test_it_warns_for_a_key_no_routed_view_declares(self, settings):
        """A view that was renamed or moved leaves its key behind."""
        settings.PAGE_TOURS_OVERRIDES = {"tests.views.GoneView": None}

        assert set(overrides_warnings()) == {"tests.views.GoneView"}

    @pytest.mark.parametrize(
        "key",
        [
            "tests.views.UntouchedTourView",
            "tests.views.OverriddenTourView",
            "tests.views.overridden_function_view",
            "tests.views.OffTourView",
        ],
        ids=["class", "inherited by a routed subclass", "function view", "include"],
    )
    def test_it_is_silent_for_a_key_a_routed_view_declares(self, settings, key):
        """The name a routed view gives its tour is a name that exists."""
        settings.PAGE_TOURS_OVERRIDES = {key: None}

        assert overrides_warnings() == {}

    def test_it_is_silent_for_the_name_of_a_tour_given_through_as_view(self, settings):
        """A subclass that sets no tour is named by the class that declares one."""
        settings.ROOT_URLCONF = "tests.urls_checks_as_view"
        settings.PAGE_TOURS_OVERRIDES = {"tests.views.OverriddenTourView": None}

        assert overrides_warnings() == {}

    def test_it_warns_for_the_name_of_the_subclass_given_a_tour_through_as_view(
        self, settings
    ):
        """The subclass's own name is not the name its tour is remembered by."""
        settings.ROOT_URLCONF = "tests.urls_checks_as_view"
        settings.PAGE_TOURS_OVERRIDES = {"tests.views.OverriddenTourSubclassView": None}

        assert set(overrides_warnings()) == {"tests.views.OverriddenTourSubclassView"}

    def test_it_warns_once_for_each_key_that_is_not_declared(self, settings):
        """Each stale key is one warning, and the others stay quiet."""
        settings.PAGE_TOURS_OVERRIDES = {
            "tests.views.GoneView": None,
            "tests.views.AlsoGoneView": "tests.views.REPLACEMENT_TOUR",
            "tests.views.UntouchedTourView": None,
        }

        assert set(overrides_warnings()) == {
            "tests.views.GoneView",
            "tests.views.AlsoGoneView",
        }

    def test_it_is_silent_without_the_setting(self):
        """A project that changes no tour has nothing to go stale."""
        assert overrides_warnings() == {}

    def test_it_does_not_resolve_the_values(self, settings):
        """A bad value is reported once, when the project starts, not here."""
        settings.PAGE_TOURS_OVERRIDES = {"tests.views.UntouchedTourView": 42}

        assert overrides_warnings() == {}
