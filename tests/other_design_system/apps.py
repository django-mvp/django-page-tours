"""App configuration of the second test design system."""

from django.apps import AppConfig


class OtherDesignSystemConfig(AppConfig):
    """A design system that styles the box and the title."""

    name = "tests.other_design_system"
    label = "other_design_system"
    page_tour_classes = {"box": "other-box", "title": "other-title"}
