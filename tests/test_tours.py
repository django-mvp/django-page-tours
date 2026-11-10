"""Tests for page_tours.tours."""

import gc
from dataclasses import replace

import pytest
from django.core.exceptions import ImproperlyConfigured
from django.utils import translation
from django.utils.html import escape
from django.utils.translation import gettext, gettext_lazy

from page_tours import tours as tours_module
from page_tours.tours import (
    Tour,
    TourStep,
    declared_tours,
    resolve_override,
    tour_overrides,
)
from tests import views

STEP = TourStep(title="Title", text="Body")


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

    def test_a_tour_keeps_the_name_it_is_declared_with(self):
        """The developer names the tour."""
        assert Tour(name="app.book", steps=[STEP]).name == "app.book"

    def test_a_tour_without_a_name_is_an_error(self):
        """The name is required."""
        with pytest.raises(TypeError):
            Tour(steps=[STEP])  # type: ignore[call-arg]

    @pytest.mark.parametrize("name", ["", "   ", "\n\t", None, 3, gettext_lazy("x")])
    def test_a_name_that_is_not_a_non_blank_string_is_an_error(self, name):
        """A name is plain text with something in it."""
        with pytest.raises(ImproperlyConfigured):
            Tour(name=name, steps=[STEP])

    def test_a_tour_without_steps_is_an_error(self):
        """A tour needs at least one step."""
        with pytest.raises(ImproperlyConfigured):
            Tour(name="test", steps=[])

    def test_steps_are_stored_as_a_tuple(self):
        """A declared tour cannot change later."""
        step = TourStep(title="Title", text="Body")

        tour = Tour(name="test", steps=[step])

        assert tour.steps == (step,)

    def test_a_tour_plays_by_itself_unless_told_otherwise(self):
        """Autoplay is on by default."""
        assert (
            Tour(name="test", steps=[TourStep(title="Title", text="Body")]).autoplay
            is True
        )

    def test_a_tour_is_at_version_one_unless_told_otherwise(self):
        """A tour declared without a version has version 1."""
        assert (
            Tour(name="test", steps=[TourStep(title="Title", text="Body")]).version == 1
        )

    def test_a_tour_keeps_the_version_it_is_declared_with(self):
        """The developer sets the version."""
        tour = Tour(
            name="test", steps=[TourStep(title="Title", text="Body")], version=3
        )

        assert tour.version == 3

    @pytest.mark.parametrize("version", [0, -1, 1.5, "2", True, None])
    def test_a_version_that_is_not_a_whole_number_of_one_or_more_is_an_error(
        self, version
    ):
        """Only 1, 2, 3 and so on are versions."""
        with pytest.raises(ImproperlyConfigured):
            Tour(
                name="test",
                steps=[TourStep(title="Title", text="Body")],
                version=version,
            )


class TestTourAsDriverSteps:
    """Converting a tour to the steps Driver.js takes."""

    def test_steps_come_out_in_the_declared_order(self):
        """One dict per step, in the order declared."""
        tour = Tour(
            name="test",
            steps=[
                TourStep(title="First", text="One"),
                TourStep(title="Second", text="Two"),
                TourStep(title="Third", text="Three"),
            ],
        )

        steps = tour.as_driver_steps()

        assert [step["title"] for step in steps] == ["First", "Second", "Third"]

    def test_the_element_key_is_present_only_for_a_step_that_names_one(self):
        """A step with no element has no element key."""
        tour = Tour(
            name="test",
            steps=[
                TourStep(title="Attached", text="One", element="#menu"),
                TourStep(title="Floating", text="Two"),
            ],
        )

        attached, floating = tour.as_driver_steps()

        assert attached["element"] == "#menu"
        assert "element" not in floating

    def test_title_and_text_are_escaped(self):
        """Markup characters come out as text, not as markup."""
        raw = "<b>&\"'"
        tour = Tour(name="test", steps=[TourStep(title=raw, text=raw)])

        (step,) = tour.as_driver_steps()

        assert step["title"] == escape(raw)
        assert step["text"] == escape(raw)

    def test_a_lazy_title_is_translated_into_the_active_language(self):
        """The language active when the steps are built decides the text."""
        tour = Tour(
            name="test", steps=[TourStep(title=gettext_lazy("Yes"), text="Body")]
        )

        with translation.override("de"):
            (step,) = tour.as_driver_steps()
            expected = str(gettext("Yes"))

        assert step["title"] == expected


@pytest.fixture
def tour():
    """Return a valid one-step tour."""
    return Tour(name="test", steps=[STEP])


class TestTourForPage:
    """Finding the tour of the page being rendered."""

    def test_a_class_based_view_supplies_its_tour(self, tour):
        """The tour attribute of the view in the context is found."""
        view = type("View", (), {"tour": tour})()

        assert Tour.for_page({"view": view}) is tour

    def test_a_function_view_supplies_its_tour_through_the_context(self, tour):
        """The tour a view passes in its context under ``tour`` is found."""
        assert Tour.for_page({"tour": tour}) is tour

    def test_the_views_own_tour_comes_before_the_context(self, tour):
        """A class-based view's attribute is its page's tour."""
        view = type("View", (), {"tour": tour})()
        other = Tour(name="other", steps=[STEP])

        assert Tour.for_page({"view": view, "tour": other}) is tour

    def test_an_empty_context_has_no_tour(self):
        """With no view and no tour there is nothing to find."""
        assert Tour.for_page({}) is None

    def test_a_view_without_a_tour_has_no_tour(self, rf):
        """A view that declares no tour yields none."""
        context = {"view": object(), "request": rf.get("/")}

        assert Tour.for_page(context) is None

    @pytest.mark.parametrize("key", ["view", "tour"])
    def test_a_tour_that_is_not_a_tour_is_ignored(self, key):
        """Only a Tour counts as a tour, so a ``tour`` of a site's own is left alone."""
        value = "not a tour"
        context = {key: type("View", (), {"tour": value})() if key == "view" else value}

        assert Tour.for_page(context) is None

    def test_the_request_does_not_supply_a_tour(self, rf, tour):
        """A tour is found from the page's own rendering, never from the request."""
        request = rf.get("/")
        request.page_tour = tour

        assert Tour.for_page({"request": request}) is None


OVERRIDDEN = views.APP_TOUR.name
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

        assert self.page_tour(views.OverriddenTourView).name == OVERRIDDEN

    def test_the_tour_a_page_plays_is_not_declared_again(self, settings):
        """Playing a replacement under the app tour's name is not a second tour."""
        settings.PAGE_TOURS_OVERRIDES = {OVERRIDDEN: REPLACEMENT}

        played = self.page_tour(views.OverriddenTourView)

        assert all(tour is not played for tour in declared_tours()[OVERRIDDEN])

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

    def test_a_function_based_view_gets_the_change(self, settings):
        """A tour passed in the context is replaced by its name."""
        settings.PAGE_TOURS_OVERRIDES = {OVERRIDDEN: REPLACEMENT}

        tour = Tour.for_page({"tour": views.APP_TOUR})

        assert tour.steps == views.REPLACEMENT_TOUR.steps

    def test_a_tour_given_through_as_view_is_changed_by_its_own_name(self, settings):
        """The view a tour is given to does not name it, the tour does."""
        settings.PAGE_TOURS_OVERRIDES = {OVERRIDDEN: REPLACEMENT}

        tour = self.page_tour(views.OverriddenTourView, tour=views.OWN_TOUR)

        assert tour is views.OWN_TOUR

    def test_another_tour_is_untouched(self, settings):
        """A tour the setting does not name is returned as declared."""
        settings.PAGE_TOURS_OVERRIDES = {OVERRIDDEN: REPLACEMENT}

        assert self.page_tour(views.UntouchedTourView) is views.UNTOUCHED_TOUR

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
        declared_tour = replace(views.APP_TOUR, version=declared)

        assert Tour.for_page({"tour": declared_tour}).version == played

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


class TestDeclaredTours:
    """The package records every tour by its name as it is declared."""

    def test_a_declared_tour_is_recorded_under_its_name(self):
        """A tour can be found by its name once it exists."""
        tour = Tour(name="tests.recorded", steps=[STEP])

        assert declared_tours()["tests.recorded"] == [tour]

    def test_two_tours_with_one_name_are_both_recorded(self):
        """Both are kept, so the check can report the clash."""
        first = Tour(name="tests.twice", steps=[STEP])
        second = Tour(name="tests.twice", steps=[STEP], version=2)

        recorded = declared_tours()["tests.twice"]

        assert len(recorded) == 2
        assert any(tour is first for tour in recorded)
        assert any(tour is second for tour in recorded)

    def test_a_tour_that_no_longer_exists_is_forgotten(self):
        """A tour nothing refers to any more is no longer declared."""
        Tour(name="tests.forgotten", steps=[STEP])
        gc.collect()

        assert "tests.forgotten" not in declared_tours()

    def test_tours_made_and_dropped_leave_nothing_behind(self):
        """A view that builds its tour on every request does not grow the record."""
        for _ in range(3):
            Tour(name="tests.per-request", steps=[STEP])
        gc.collect()

        assert "tests.per-request" not in tours_module._declared

    def test_the_tours_of_the_routed_views_are_declared(self):
        """A tour declared in a view module is recorded when the module is imported."""
        assert any(
            tour is views.APP_TOUR for tour in declared_tours()[views.APP_TOUR.name]
        )
