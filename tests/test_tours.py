"""Tests for page_tours.tours."""

import pytest
from django.core.exceptions import ImproperlyConfigured

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
