"""Tests for page_tours.checks."""

import copy

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
