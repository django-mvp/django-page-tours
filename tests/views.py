"""Views that give the tests pages with and without a tour."""

from django.http import Http404
from django.shortcuts import render
from django.utils.translation import gettext_lazy
from django.views.generic import TemplateView

from page_tours import Tour, TourStep, with_tour

MARKUP_TITLE = "<b>bold</b> & co"

CLASS_TOUR = Tour(
    steps=[
        TourStep(title="Welcome", text="Start here."),
        TourStep(title="The heading", text="What the page is.", element="h1"),
        TourStep(title="The control", text="Press it.", element="#control"),
    ]
)
FUNCTION_TOUR = Tour(steps=[TourStep(title="From a function", text="Plain view.")])
MARKUP_TOUR = Tour(steps=[TourStep(title=MARKUP_TITLE, text="<i>text</i> & more")])
TRANSLATED_TOUR = Tour(steps=[TourStep(title=gettext_lazy("Yes"), text="Body.")])


def steps_for(*selectors):
    """Build a tour whose steps point at the given selectors, titled by position.

    Args:
        *selectors: One CSS selector per step; an empty string attaches to nothing.

    Returns:
        A tour with one step per selector, titled "Step 1", "Step 2" and so on.
    """
    return Tour(
        steps=[
            TourStep(title=f"Step {number}", text="Text.", element=selector)
            for number, selector in enumerate(selectors, start=1)
        ]
    )


class ClassTourView(TemplateView):
    """A class-based page with a tour."""

    template_name = "test_page.html"
    tour = CLASS_TOUR


class MarkupTourView(ClassTourView):
    """A page whose step carries markup characters."""

    tour = MARKUP_TOUR


class TranslatedTourView(ClassTourView):
    """A page whose step title is translated."""

    tour = TRANSLATED_TOUR


class NoTourView(TemplateView):
    """A page with no tour."""

    template_name = "test_page.html"


class MissingClassTourView(ClassTourView):
    """A class-based page with a tour that is not found."""

    def get(self, request, *args, **kwargs):
        """Raise instead of rendering the page."""
        raise Http404


@with_tour(FUNCTION_TOUR)
def function_tour_view(request):
    """Render a function-based page with a tour."""
    return render(request, "test_page.html")


@with_tour(FUNCTION_TOUR)
def missing_function_tour_view(request):
    """Raise not found from a function-based page with a tour."""
    raise Http404


class ControlsTourView(TemplateView):
    """A page with controls of its own, whose tour is set per URL."""

    template_name = "test_controls.html"
    tour = None
    fragile = ""

    def get_context_data(self, **kwargs):
        """Add the id of the element whose measuring is made to throw."""
        context = super().get_context_data(**kwargs)
        context["fragile"] = self.fragile
        return context


class NavigationTourView(ControlsTourView):
    """Three steps, each attached to an element."""

    tour = steps_for("h1", "#control", "#output")


class MissingFirstTourView(ControlsTourView):
    """The first step's element is not on the page."""

    tour = steps_for("#absent", "h1", "#control")


class MissingMiddleTourView(ControlsTourView):
    """The second step's element is not on the page."""

    tour = steps_for("h1", "#absent", "#control")


class HiddenMiddleTourView(ControlsTourView):
    """The second step's element carries the hidden attribute."""

    tour = steps_for("h1", "#secret", "#control")


class InvalidSelectorTourView(ControlsTourView):
    """The second step's selector is not valid CSS."""

    tour = steps_for("h1", "[[", "#control")


class NothingShowableTourView(ControlsTourView):
    """Every step names an element that is not on the page."""

    tour = steps_for("#absent", "#also-absent")


class TwinTourView(ControlsTourView):
    """A step whose selector matches two elements."""

    tour = steps_for(".twin", "#control")


class FragileTourView(ControlsTourView):
    """The second step's element throws when Driver.js measures it."""

    tour = steps_for("h1", "#output", "#control")
    fragile = "output"


class BareTourView(TemplateView):
    """A page with a tour, for comparing with the same page without one."""

    template_name = "test_controls.html"
    tour = steps_for("h1", "#control")


class NoTourControlsView(TemplateView):
    """The same page as BareTourView, with no tour."""

    template_name = "test_controls.html"


class ReplayView(TemplateView):
    """A page with a tour and a replay control carrying attributes of its own."""

    template_name = "test_replay.html"
    tour = steps_for("h1", "#control")

    def get_context_data(self, **kwargs):
        """Add an attribute value full of markup characters."""
        context = super().get_context_data(**kwargs)
        context["hostile"] = 'a "quoted" <b>&'
        return context


class ReplayNoTourView(ReplayView):
    """The same page with no tour."""

    tour = None


class ReplayPointedAtView(ReplayView):
    """The second step points at the replay control."""

    tour = steps_for("h1", "#replay", "#control")


class ReplayNothingShowableView(ReplayView):
    """Every step names an element that is not on the page."""

    tour = steps_for("#absent", "#also-absent")


class ReplayTwiceView(ReplayView):
    """A page placing the replay control twice."""

    template_name = "test_replay_twice.html"


def on_request_tour():
    """Build a tour of the page's heading and button that plays only on request.

    Returns:
        A tour with ``autoplay`` off.
    """
    return Tour(steps=steps_for("h1", "#control").steps, autoplay=False)


class OnRequestView(ReplayView):
    """A page whose tour plays only when the replay control is used."""

    tour = on_request_tour()


class OnRequestNoControlView(TemplateView):
    """A page whose tour plays only on request, with no control placed."""

    template_name = "test_controls.html"
    tour = on_request_tour()


class ControlInBaseView(TemplateView):
    """A page with a tour, extending a base template that places the control."""

    template_name = "test_control_in_base_page.html"
    tour = steps_for("h1", "#control")


class ControlInBaseNoTourView(TemplateView):
    """A page with no tour, extending the base template that places the control."""

    template_name = "test_control_in_base_page.html"
