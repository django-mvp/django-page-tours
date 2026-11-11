"""App configuration of the test design system."""

from django.apps import AppConfig


class DesignSystemConfig(AppConfig):
    """A design system that gives the tour's parts its own classes."""

    name = "tests.design_system"
    label = "design_system"
    page_tour_classes = {
        "box": "ds-box ds-raised",
        "next": "ds-button",
        "done": "ds-button",
        "beacon": "ds-beacon",
    }
