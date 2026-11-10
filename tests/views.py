"""Views that give the tests pages with and without a tour."""

from django.http import Http404
from django.shortcuts import render
from django.utils import translation
from django.utils.translation import gettext_lazy
from django.views.generic import TemplateView

from page_tours import Tour, TourStep

MARKUP_TITLE = "<b>bold</b> & co"

CLASS_TOUR = Tour(
    name="tests.class",
    steps=[
        TourStep(title="Welcome", text="Start here."),
        TourStep(title="The heading", text="What the page is.", element="h1"),
        TourStep(title="The control", text="Press it.", element="#control"),
    ],
)
FUNCTION_TOUR = Tour(
    name="tests.function", steps=[TourStep(title="From a function", text="Plain view.")]
)
MARKUP_TOUR = Tour(
    name="tests.markup", steps=[TourStep(title=MARKUP_TITLE, text="<i>text</i> & more")]
)
TRANSLATED_TOUR = Tour(
    name="tests.translated", steps=[TourStep(title=gettext_lazy("Yes"), text="Body.")]
)


def steps_for(name, *selectors):
    """Build a tour whose steps point at the given selectors, titled by position.

    Args:
        name: The tour's name.
        *selectors: One CSS selector per step; an empty string attaches to nothing.

    Returns:
        A tour with one step per selector, titled "Step 1", "Step 2" and so on.
    """
    return Tour(
        name=name,
        steps=[
            TourStep(title=f"Step {number}", text="Text.", element=selector)
            for number, selector in enumerate(selectors, start=1)
        ],
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


def function_tour_view(request):
    """Render a function-based page with a tour."""
    return render(request, "test_page.html", {"tour": FUNCTION_TOUR})


def missing_function_tour_view(request):
    """Raise not found from a function-based page that renders with a tour."""
    if "found" not in request.GET:
        raise Http404
    return render(request, "test_page.html", {"tour": FUNCTION_TOUR})


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

    tour = steps_for("tests.navigation-tour", "h1", "#control", "#output")


class GermanNavigationTourView(NavigationTourView):
    """The three-step page, served in German."""

    def get(self, request, *args, **kwargs):
        """Render the page with German active."""
        with translation.override("de"):
            response = super().get(request, *args, **kwargs)
            response.render()
        return response


class MissingFirstTourView(ControlsTourView):
    """The first step's element is not on the page."""

    tour = steps_for("tests.missing-first-tour", "#absent", "h1", "#control")


class MissingMiddleTourView(ControlsTourView):
    """The second step's element is not on the page."""

    tour = steps_for("tests.missing-middle-tour", "h1", "#absent", "#control")


class HiddenMiddleTourView(ControlsTourView):
    """The second step's element carries the hidden attribute."""

    tour = steps_for("tests.hidden-middle-tour", "h1", "#secret", "#control")


class InvalidSelectorTourView(ControlsTourView):
    """The second step's selector is not valid CSS."""

    tour = steps_for("tests.invalid-selector-tour", "h1", "[[", "#control")


class NothingShowableTourView(ControlsTourView):
    """Every step names an element that is not on the page."""

    tour = steps_for("tests.nothing-showable-tour", "#absent", "#also-absent")


class TwinTourView(ControlsTourView):
    """A step whose selector matches two elements."""

    tour = steps_for("tests.twin-tour", ".twin", "#control")


class FragileTourView(ControlsTourView):
    """The second step's element throws when Driver.js measures it."""

    tour = steps_for("tests.fragile-tour", "h1", "#output", "#control")
    fragile = "output"


class BareTourView(TemplateView):
    """A page with a tour, for comparing with the same page without one."""

    template_name = "test_controls.html"
    tour = steps_for("tests.bare-tour", "h1", "#control")


class NoTourControlsView(TemplateView):
    """The same page as BareTourView, with no tour."""

    template_name = "test_controls.html"


class ReplayView(TemplateView):
    """A page with a tour and a replay control carrying attributes of its own."""

    template_name = "test_replay.html"
    tour = steps_for("tests.replay", "h1", "#control")

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

    tour = steps_for("tests.replay-pointed-at", "h1", "#replay", "#control")


class ReplayNothingShowableView(ReplayView):
    """Every step names an element that is not on the page."""

    tour = steps_for("tests.replay-nothing-showable", "#absent", "#also-absent")


class ReplayTwiceView(ReplayView):
    """A page placing the replay control twice."""

    template_name = "test_replay_twice.html"


def on_request_tour():
    """Build a tour of the page's heading and button that plays only on request.

    Returns:
        A tour with ``autoplay`` off.
    """
    return Tour(
        name="tests.on-request",
        steps=[
            TourStep(title="Step 1", text="Text.", element="h1"),
            TourStep(title="Step 2", text="Text.", element="#control"),
        ],
        autoplay=False,
    )


class OnRequestView(ReplayView):
    """A page whose tour plays only when the replay control is used."""

    tour = on_request_tour()


class VersionedTourView(ControlsTourView):
    """A page whose tour is routed at several versions, all seen as one tour."""

    tour = steps_for("tests.versioned", "h1", "#control")


VERSION_TWO = Tour(
    name="tests.versioned", steps=VersionedTourView.tour.steps, version=2
)
VERSION_TWO_EDITED = Tour(
    name="tests.versioned",
    steps=[TourStep(title="Step 1", text="Text, with a typo fixed.", element="h1")],
    version=2,
)
ON_REQUEST_VERSION_TWO = Tour(
    name="tests.on-request",
    steps=on_request_tour().steps,
    autoplay=False,
    version=2,
)


class OnRequestNoControlView(TemplateView):
    """A page whose tour plays only on request, with no control placed."""

    template_name = "test_controls.html"
    tour = on_request_tour()


class ControlInBaseView(TemplateView):
    """A page with a tour, extending a base template that places the control."""

    template_name = "test_control_in_base_page.html"
    tour = steps_for("tests.control-in-base", "h1", "#control")


class ControlInBaseNoTourView(TemplateView):
    """A page with no tour, extending the base template that places the control."""

    template_name = "test_control_in_base_page.html"


APP_TOUR = Tour(
    name="app.page",
    steps=[
        TourStep(title="Step 1", text="Text.", element="h1"),
        TourStep(title="Step 2", text="Text.", element="#control"),
        TourStep(title="Step 3", text="Text."),
    ],
    version=2,
)
OFF_TOUR = steps_for("app.off", "h1", "#control")
UNTOUCHED_TOUR = steps_for("app.untouched", "h1", "#control")
OWN_TOUR = steps_for("tests.own", "h1")
REPLACEMENT_TOUR = Tour(
    name="tests.replacement",
    steps=[
        TourStep(title="Ours 1", text="Our first.", element="h1"),
        TourStep(title="Ours 2", text="Our second.", element="#control"),
    ],
)
REWORDED_TOUR = Tour(
    name="tests.reworded",
    steps=[
        APP_TOUR.steps[0],
        TourStep(title="Step 2", text="Reworded for us.", element="#control"),
        APP_TOUR.steps[2],
    ],
)
QUIET_REPLACEMENT_TOUR = Tour(
    name="tests.quiet-replacement", steps=REPLACEMENT_TOUR.steps, autoplay=False
)
REPLACEMENT_TOUR_VERSION_TWO = Tour(
    name="tests.replacement-two", steps=REPLACEMENT_TOUR.steps, version=2
)
NOT_A_TOUR = "not a tour"


class OverriddenTourView(ReplayView):
    """A page of an installed app, whose tour a project changes."""

    tour = APP_TOUR


class OverriddenTourSubclassView(OverriddenTourView):
    """A page that sets no tour and so shares the tour of the page it extends."""


class OverriddenTourOwnView(OverriddenTourView):
    """A page that sets a tour of its own, which is another tour."""

    tour = OWN_TOUR


class OffTourView(ReplayView):
    """A page of an installed app, whose tour a project turns off."""

    tour = OFF_TOUR


class UntouchedTourView(ReplayView):
    """A page of an installed app whose tour a project leaves alone."""

    tour = UNTOUCHED_TOUR


def overridden_function_view(request):
    """Render a function-based page of an installed app, whose tour is changed."""
    return render(request, "test_controls.html", {"tour": APP_TOUR})


class PartsTourView(TemplateView):
    """A tour whose first and last steps are attached and whose middle one is not."""

    template_name = "test_page.html"
    tour = steps_for("tests.parts-tour", "h1", "", "#control")


class StyleBeforeView(TemplateView):
    """A page whose own style sits before the tag."""

    template_name = "test_style_before.html"
    tour = steps_for("tests.style-before", "h1", "", "#control")


class StyleAfterView(StyleBeforeView):
    """A page whose own style sits after the tag."""

    template_name = "test_style_after.html"


class LayerBeforeView(StyleBeforeView):
    """A page whose own layered style sits before the tag."""

    template_name = "test_layer_before.html"


class DesignSystemView(TemplateView):
    """A page whose base template loads a design system's stylesheet."""

    template_name = "test_design_system_page.html"
    tour = steps_for("tests.design-system", "h1", "#control")
