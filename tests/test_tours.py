"""Tests for page_tours.tours."""

import asyncio
from concurrent.futures import ThreadPoolExecutor

import pytest
from asgiref.sync import iscoroutinefunction
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponse
from django.utils import translation
from django.utils.html import escape
from django.utils.translation import gettext, gettext_lazy

from page_tours.tours import Tour, TourStep, with_tour


def run_in_own_loop(coroutine):
    """Run a coroutine to completion on a fresh event loop in its own thread.

    The browser tests leave an event loop running in the test thread, so the
    coroutine cannot be run there.
    """
    with ThreadPoolExecutor(max_workers=1) as pool:
        return pool.submit(asyncio.run, coroutine).result()


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


@pytest.fixture
def tour():
    """Return a valid one-step tour."""
    return Tour(steps=[TourStep(title="Title", text="Body")])


class TestWithTour:
    """Attaching a tour to a function-based view."""

    def test_the_tour_is_on_the_request_while_the_view_runs(self, rf, tour):
        """The view can reach the tour through the request."""
        seen = []

        @with_tour(tour)
        def view(request):
            seen.append(request.page_tour)
            return HttpResponse()

        view(rf.get("/"))

        assert seen == [tour]

    def test_the_tour_is_removed_if_the_view_raises(self, rf, tour):
        """An error page rendered afterwards does not carry the tour."""

        @with_tour(tour)
        def view(request):
            raise PermissionError

        request = rf.get("/")
        with pytest.raises(PermissionError):
            view(request)

        assert not hasattr(request, "page_tour")

    @pytest.mark.parametrize("login_required_is_outer", [True, False])
    def test_the_tour_reaches_the_request_through_login_required(
        self, rf, tour, login_required_is_outer
    ):
        """The order of with_tour and login_required does not matter."""
        seen = []

        def view(request):
            seen.append(getattr(request, "page_tour", None))
            return HttpResponse()

        if login_required_is_outer:
            decorated = login_required(with_tour(tour)(view))
        else:
            decorated = with_tour(tour)(login_required(view))
        request = rf.get("/")
        request.user = type("User", (), {"is_authenticated": True})()

        decorated(request)

        assert seen == [tour]

    def test_an_async_view_gets_the_tour_on_the_request(self, rf, tour):
        """An async function-based view stays async and sees the tour."""
        seen = []

        @with_tour(tour)
        async def view(request):
            seen.append(request.page_tour)
            return HttpResponse()

        run_in_own_loop(view(rf.get("/")))

        assert seen == [tour]

    def test_an_async_view_stays_async(self, tour):
        """Django still recognises the decorated view as async."""

        @with_tour(tour)
        async def view(request):
            return HttpResponse()

        assert iscoroutinefunction(view)

    def test_an_async_view_that_raises_loses_the_tour(self, rf, tour):
        """An async view's error page does not carry the tour either."""

        @with_tour(tour)
        async def view(request):
            raise PermissionError

        request = rf.get("/")
        with pytest.raises(PermissionError):
            run_in_own_loop(view(request))

        assert not hasattr(request, "page_tour")

    def test_the_wrapper_keeps_the_view_name(self, tour):
        """The wrapper is made with functools.wraps."""

        @with_tour(tour)
        def my_view(request):
            return HttpResponse()

        assert my_view.__name__ == "my_view"
        assert my_view.__wrapped__.__name__ == "my_view"


class TestTourForPage:
    """Finding the tour of the page being rendered."""

    def test_a_class_based_view_supplies_its_tour(self, tour):
        """The tour attribute of the view in the context is found."""
        view = type("View", (), {"tour": tour})()

        assert Tour.for_page({"view": view}) is tour

    def test_a_function_view_supplies_its_tour_through_the_request(self, rf, tour):
        """The tour set by with_tour on the request is found."""
        request = rf.get("/")
        request.page_tour = tour

        assert Tour.for_page({"request": request}) is tour

    def test_an_empty_context_has_no_tour(self):
        """With no view and no request there is nothing to find."""
        assert Tour.for_page({}) is None

    def test_a_view_without_a_tour_has_no_tour(self, rf):
        """A view that declares no tour yields none."""
        context = {"view": object(), "request": rf.get("/")}

        assert Tour.for_page(context) is None

    def test_a_tour_that_is_not_a_tour_is_ignored(self):
        """Only a Tour counts as a tour."""
        view = type("View", (), {"tour": "not a tour"})()

        assert Tour.for_page({"view": view}) is None
