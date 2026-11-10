"""Tests for page_tours.tours."""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from functools import partial

import pytest
from asgiref.sync import iscoroutinefunction
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponse
from django.utils import translation
from django.utils.html import escape
from django.utils.translation import gettext, gettext_lazy
from django.views import View

from page_tours.tours import (
    Tour,
    TourStep,
    resolve_override,
    tour_id,
    tour_overrides,
    with_tour,
)
from tests import views


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

    def test_a_tour_plays_by_itself_unless_told_otherwise(self):
        """Autoplay is on by default."""
        assert Tour(steps=[TourStep(title="Title", text="Body")]).autoplay is True

    def test_a_tour_is_at_version_one_unless_told_otherwise(self):
        """A tour declared without a version has version 1."""
        assert Tour(steps=[TourStep(title="Title", text="Body")]).version == 1

    def test_a_tour_keeps_the_version_it_is_declared_with(self):
        """The developer sets the version."""
        tour = Tour(steps=[TourStep(title="Title", text="Body")], version=3)

        assert tour.version == 3

    @pytest.mark.parametrize("version", [0, -1, 1.5, "2", True, None])
    def test_a_version_that_is_not_a_whole_number_of_one_or_more_is_an_error(
        self, version
    ):
        """Only 1, 2, 3 and so on are versions."""
        with pytest.raises(ImproperlyConfigured):
            Tour(steps=[TourStep(title="Title", text="Body")], version=version)


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

    def test_the_view_is_recorded_on_the_request(self, rf, tour):
        """The request names the decorated view by its dotted path."""
        seen = []

        @with_tour(tour)
        def view(request):
            seen.append(request.page_tour_view)
            return HttpResponse()

        view(rf.get("/"))

        assert seen == [f"{view.__module__}.{view.__wrapped__.__qualname__}"]

    def test_an_async_view_is_recorded_on_the_request(self, rf, tour):
        """An async view is named on the request too."""
        seen = []

        @with_tour(tour)
        async def view(request):
            seen.append(request.page_tour_view)
            return HttpResponse()

        run_in_own_loop(view(rf.get("/")))

        assert seen == [f"{view.__module__}.{view.__wrapped__.__qualname__}"]

    def test_class_based_views_wrapped_with_with_tour_keep_their_own_names(
        self, rf, tour
    ):
        """Two ``as_view()`` views are named by their own classes, not as one."""
        seen = []

        class FirstView(View):
            def get(self, request):
                seen.append(request.page_tour_view)
                return HttpResponse()

        class SecondView(FirstView):
            pass

        with_tour(tour)(FirstView.as_view())(rf.get("/"))
        with_tour(tour)(SecondView.as_view())(rf.get("/"))

        assert seen == [dotted_path(FirstView), dotted_path(SecondView)]

    def test_a_view_without_a_qualified_name_can_carry_a_tour(self, rf, tour):
        """A ``functools.partial`` view is decorated and named without error."""
        seen = []

        def view(request, answer):
            seen.append(request.page_tour_view)
            return HttpResponse()

        with_tour(tour)(partial(view, answer=42))(rf.get("/"))

        assert len(seen) == 1
        assert isinstance(seen[0], str)

    def test_the_view_is_forgotten_if_the_view_raises(self, rf, tour):
        """The error page that follows does not name a view."""

        @with_tour(tour)
        def view(request):
            raise PermissionError

        request = rf.get("/")
        with pytest.raises(PermissionError):
            view(request)

        assert not hasattr(request, "page_tour_view")

    def test_an_async_view_that_raises_forgets_the_view(self, rf, tour):
        """An async view's error page does not name a view either."""

        @with_tour(tour)
        async def view(request):
            raise PermissionError

        request = rf.get("/")
        with pytest.raises(PermissionError):
            run_in_own_loop(view(request))

        assert not hasattr(request, "page_tour_view")

    def test_the_wrapper_keeps_the_view_name(self, tour):
        """The wrapper is made with functools.wraps."""

        @with_tour(tour)
        def my_view(request):
            return HttpResponse()

        assert my_view.__name__ == "my_view"
        assert my_view.__wrapped__.__name__ == "my_view"


class ParentView:
    """A class-based view that declares a tour."""

    tour = Tour(steps=[TourStep(title="Title", text="Body")])


class InheritingView(ParentView):
    """A view that takes its parent's tour."""


class OwnTourView(ParentView):
    """A view that declares a tour of its own."""

    tour = Tour(steps=[TourStep(title="Other", text="Body")])


class TourlessView:
    """A view whose tour is set after the class is made."""


def dotted_path(cls):
    """Return the dotted path of a class as the tests expect to see it."""
    return f"{cls.__module__}.{cls.__qualname__}"


class TestTourId:
    """Naming the tour of the page being rendered."""

    def test_a_class_based_view_is_named_by_its_class(self):
        """The class that holds the tour gives the id."""
        assert tour_id({"view": ParentView()}) == dotted_path(ParentView)

    def test_a_subclass_inheriting_the_tour_shares_its_parents_id(self):
        """Inheriting a tour is showing the same tour."""
        assert tour_id({"view": InheritingView()}) == dotted_path(ParentView)

    def test_a_subclass_declaring_its_own_tour_has_its_own_id(self):
        """Declaring a tour makes it a different tour."""
        assert tour_id({"view": OwnTourView()}) == dotted_path(OwnTourView)

    def test_a_tour_set_on_the_instance_is_named_by_the_views_class(self):
        """With no class holding the tour, the view's own class gives the id."""
        view = TourlessView()
        view.tour = Tour(steps=[TourStep(title="Title", text="Body")])

        assert tour_id({"view": view}) == dotted_path(TourlessView)

    def test_a_tour_put_on_the_request_by_hand_still_gets_an_id(self, rf, tour):
        """A request carrying a tour but no recorded view does not raise."""
        request = rf.get("/")
        request.page_tour = tour

        assert isinstance(tour_id({"request": request}), str)

    def test_a_function_based_view_is_named_by_the_request(self, rf, tour):
        """The view that ``with_tour`` recorded gives the id."""

        @with_tour(tour)
        def view(request):
            return request

        request = view(rf.get("/"))

        assert tour_id({"request": request}) == (
            f"{view.__module__}.{view.__wrapped__.__qualname__}"
        )


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


OVERRIDDEN = "tests.views.OverriddenTourView"
REPLACEMENT = "tests.views.REPLACEMENT_TOUR"


class TestTourOverrides:
    """A project changes or turns off a tour declared by an installed app."""

    def page_tour(self, view_class, **initkwargs):
        """Return the tour of a class-based page, as the page renders it."""
        view = view_class(**initkwargs)
        return Tour.for_page({"view": view})

    def test_a_replacement_is_the_tour_of_the_page(self, settings):
        """The page plays the replacement's steps."""
        settings.PAGE_TOURS_OVERRIDES = {OVERRIDDEN: REPLACEMENT}

        tour = self.page_tour(views.OverriddenTourView)

        assert tour.steps == views.REPLACEMENT_TOUR.steps

    def test_a_replacement_keeps_the_name_of_the_tour_it_replaces(self, settings):
        """Replacing a tour does not rename it, so what was seen stays seen."""
        settings.PAGE_TOURS_OVERRIDES = {OVERRIDDEN: REPLACEMENT}

        assert tour_id({"view": views.OverriddenTourView()}) == OVERRIDDEN

    def test_none_turns_the_tour_off(self, settings):
        """A page whose tour is set to None has no tour."""
        settings.PAGE_TOURS_OVERRIDES = {OVERRIDDEN: None}

        assert self.page_tour(views.OverriddenTourView) is None

    def test_a_subclass_that_sets_no_tour_gets_the_change(self, settings):
        """A page that shares the tour shares its replacement."""
        settings.PAGE_TOURS_OVERRIDES = {OVERRIDDEN: REPLACEMENT}

        tour = self.page_tour(views.OverriddenTourSubclassView)

        assert tour.steps == views.REPLACEMENT_TOUR.steps

    def test_a_subclass_that_sets_its_own_tour_does_not(self, settings):
        """A page with a tour of its own is another tour."""
        settings.PAGE_TOURS_OVERRIDES = {OVERRIDDEN: REPLACEMENT}

        tour = self.page_tour(views.OverriddenTourOwnView)

        assert tour is views.OWN_TOUR

    def test_a_function_based_view_gets_the_change(self, rf, settings):
        """A tour set with ``with_tour`` is replaced by its name."""
        settings.PAGE_TOURS_OVERRIDES = {
            "tests.views.overridden_function_view": REPLACEMENT
        }
        request = rf.get("/")
        views.overridden_function_view(request)

        tour = Tour.for_page({"request": request})

        assert tour.steps == views.REPLACEMENT_TOUR.steps

    def test_a_tour_given_through_as_view_gets_the_change(self, settings):
        """The name is that of the class that declares the tour."""
        settings.PAGE_TOURS_OVERRIDES = {OVERRIDDEN: REPLACEMENT}

        tour = self.page_tour(views.OverriddenTourView, tour=views.OWN_TOUR)

        assert tour.steps == views.REPLACEMENT_TOUR.steps

    def test_another_tour_is_untouched(self, settings):
        """A tour the setting does not name is returned as declared."""
        settings.PAGE_TOURS_OVERRIDES = {OVERRIDDEN: REPLACEMENT}

        assert self.page_tour(views.UntouchedTourView) is views.APP_TOUR

    def test_without_the_setting_the_declared_tour_is_returned(self):
        """A project that sets nothing sees every tour as declared."""
        assert self.page_tour(views.OverriddenTourView) is views.APP_TOUR

    @pytest.mark.parametrize(
        ("declared", "path", "played"),
        [
            (2, REPLACEMENT, 2),
            (2, "tests.views.REPLACEMENT_TOUR_VERSION_TWO", 3),
            (1, REPLACEMENT, 1),
        ],
    )
    def test_a_replacement_counts_on_from_the_version_it_replaces(
        self, settings, declared, path, played
    ):
        """The version played is the declared one plus the replacement's, less one."""
        settings.PAGE_TOURS_OVERRIDES = {OVERRIDDEN: path}
        view = views.OverriddenTourView(tour=replace(views.APP_TOUR, version=declared))

        assert Tour.for_page({"view": view}).version == played

    def test_the_declared_replacement_is_not_changed(self, settings):
        """Counting a version on builds a new tour and leaves the declared one."""
        settings.PAGE_TOURS_OVERRIDES = {OVERRIDDEN: REPLACEMENT}

        self.page_tour(views.OverriddenTourView)

        assert views.REPLACEMENT_TOUR.version == 1

    def test_a_change_to_the_setting_is_seen_at_once(self, settings):
        """The setting is read on every call, not cached."""
        settings.PAGE_TOURS_OVERRIDES = {OVERRIDDEN: None}
        assert self.page_tour(views.OverriddenTourView) is None

        settings.PAGE_TOURS_OVERRIDES = {}

        assert self.page_tour(views.OverriddenTourView) is views.APP_TOUR


class TestTourOverridesRefused:
    """A setting that cannot be used is refused, not ignored."""

    @pytest.mark.parametrize("value", [42, ["tests.views.REPLACEMENT_TOUR"], True])
    def test_a_value_that_is_neither_a_path_nor_none_is_refused(self, value):
        """Only a dotted path or None is a replacement."""
        with pytest.raises(ImproperlyConfigured):
            resolve_override(OVERRIDDEN, value)

    def test_a_tour_object_is_refused(self):
        """The setting holds paths, so a project's settings do not import its tours."""
        with pytest.raises(ImproperlyConfigured):
            resolve_override(OVERRIDDEN, views.REPLACEMENT_TOUR)

    @pytest.mark.parametrize(
        "path", ["tests.views.missing_tour", "tests.no_such_module.tour", "nodots"]
    )
    def test_a_path_that_does_not_import_is_refused(self, path):
        """A replacement that is not there is an error."""
        with pytest.raises(ImproperlyConfigured):
            resolve_override(OVERRIDDEN, path)

    def test_a_path_that_does_not_import_keeps_its_cause(self):
        """The import error that explains the refusal is chained."""
        with pytest.raises(ImproperlyConfigured) as raised:
            resolve_override(OVERRIDDEN, "tests.views.missing_tour")

        assert isinstance(raised.value.__cause__, ImportError)

    def test_a_path_to_something_that_is_not_a_tour_is_refused(self):
        """What the path names has to be a Tour."""
        with pytest.raises(ImproperlyConfigured):
            resolve_override(OVERRIDDEN, "tests.views.NOT_A_TOUR")

    def test_a_module_whose_own_tour_is_invalid_raises_its_own_error(self):
        """The module's error is not reported as a path that cannot be imported."""
        with pytest.raises(ImproperlyConfigured) as raised:
            resolve_override(OVERRIDDEN, "tests.invalid_tour.BROKEN_TOUR")

        assert raised.value.__cause__ is None

    def test_none_resolves_to_none(self):
        """A tour turned off has no replacement."""
        assert resolve_override(OVERRIDDEN, None) is None

    def test_every_entry_of_the_setting_is_resolved(self, settings):
        """The replacements and the tours turned off are returned by name."""
        settings.PAGE_TOURS_OVERRIDES = {OVERRIDDEN: REPLACEMENT, "other": None}

        assert tour_overrides() == {OVERRIDDEN: views.REPLACEMENT_TOUR, "other": None}

    def test_no_setting_resolves_to_nothing(self):
        """A project that sets nothing changes no tour."""
        assert tour_overrides() == {}

    def test_one_bad_entry_refuses_the_whole_setting(self, settings):
        """A good entry does not hide a bad one."""
        settings.PAGE_TOURS_OVERRIDES = {OVERRIDDEN: REPLACEMENT, "other": 42}

        with pytest.raises(ImproperlyConfigured):
            tour_overrides()
