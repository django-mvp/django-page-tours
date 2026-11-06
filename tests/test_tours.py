"""Tests for page_tours.tours."""

import pytest
from django.core.exceptions import ImproperlyConfigured
from django.utils import translation
from django.utils.html import escape
from django.utils.translation import gettext, gettext_lazy

from page_tours.tours import Tour, TourStep


class TestTourStep:
    """Declaring a step of a tour."""

    @pytest.mark.parametrize("title", ["", "   ", "\n\t"])
    def test_an_empty_or_blank_title_is_an_error(self, title):
        """A step without a title cannot be declared."""
        with pytest.raises(ImproperlyConfigured):
            TourStep(title=title, text="Body")

    @pytest.mark.parametrize("text", ["", "   ", "\n\t"])
    def test_an_empty_or_blank_text_is_an_error(self, text):
        """A step without text cannot be declared."""
        with pytest.raises(ImproperlyConfigured):
            TourStep(title="Title", text=text)

    def test_the_element_is_optional(self):
        """A step may name no element."""
        assert TourStep(title="Title", text="Body").element == ""


class TestTour:
    """Declaring a tour."""

    def test_a_tour_without_steps_is_an_error(self):
        """A tour needs at least one step."""
        with pytest.raises(ImproperlyConfigured):
            Tour(steps=[])

    def test_steps_are_stored_as_a_tuple(self):
        """A declared tour cannot change later."""
        step = TourStep(title="Title", text="Body")

        tour = Tour(steps=[step])

        assert tour.steps == (step,)


class TestTourAsDriverSteps:
    """Converting a tour to the steps Driver.js takes."""

    def test_steps_come_out_in_the_declared_order(self):
        """One dict per step, in the order declared."""
        tour = Tour(
            steps=[
                TourStep(title="First", text="One"),
                TourStep(title="Second", text="Two"),
                TourStep(title="Third", text="Three"),
            ]
        )

        steps = tour.as_driver_steps()

        assert [step["title"] for step in steps] == ["First", "Second", "Third"]

    def test_the_element_key_is_present_only_for_a_step_that_names_one(self):
        """A step with no element has no element key."""
        tour = Tour(
            steps=[
                TourStep(title="Attached", text="One", element="#menu"),
                TourStep(title="Floating", text="Two"),
            ]
        )

        attached, floating = tour.as_driver_steps()

        assert attached["element"] == "#menu"
        assert "element" not in floating

    def test_title_and_text_are_escaped(self):
        """Markup characters come out as text, not as markup."""
        raw = "<b>&\"'"
        tour = Tour(steps=[TourStep(title=raw, text=raw)])

        (step,) = tour.as_driver_steps()

        assert step["title"] == escape(raw)
        assert step["text"] == escape(raw)

    def test_a_lazy_title_is_translated_into_the_active_language(self):
        """The language active when the steps are built decides the text."""
        tour = Tour(steps=[TourStep(title=gettext_lazy("Yes"), text="Body")])

        with translation.override("de"):
            (step,) = tour.as_driver_steps()
            expected = str(gettext("Yes"))

        assert step["title"] == expected
