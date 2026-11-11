"""Views that give the tests pages with and without a tour."""

from django.http import Http404
from django.shortcuts import render
from django.utils import translation
from django.utils.translation import gettext_lazy
from django.views.generic import TemplateView

from page_tours import Beacon, Hint, Hints, Tour, TourStep

CLASS_TOUR = Tour(
    name="tests.class",
    steps=[
        TourStep(title="Welcome", description="Start here."),
        TourStep(title="The heading", description="What the page is.", element="h1"),
        TourStep(title="The control", description="Press it.", element="#control"),
    ],
)
FUNCTION_TOUR = Tour(
    name="tests.function",
    steps=[TourStep(title="From a function", description="Plain view.")],
)
TRANSLATED_TOUR = Tour(
    name="tests.translated",
    steps=[TourStep(title=gettext_lazy("Yes"), description="Body.")],
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
            TourStep(title=f"Step {number}", description="Text.", element=selector)
            for number, selector in enumerate(selectors, start=1)
        ],
    )


OPTIONS_TOUR = Tour(
    name="tests.options",
    steps=CLASS_TOUR.steps,
    showProgress=True,
    progressText="{{current}} / {{total}}",
)


class ClassTourView(TemplateView):
    """A class-based page with a tour."""

    template_name = "test_page.html"
    extra_context = {"tour": CLASS_TOUR}


class OptionsTourView(ClassTourView):
    """A page whose tour passes options of its own to Driver.js."""

    extra_context = {"tour": OPTIONS_TOUR}


class TranslatedTourView(ClassTourView):
    """A page whose step title is translated."""

    extra_context = {"tour": TRANSLATED_TOUR}


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
    """A page with controls of its own, whose tour each subclass sets."""

    template_name = "test_controls.html"
    fragile = ""

    def get_context_data(self, **kwargs):
        """Add the id of the element whose measuring is made to throw."""
        context = super().get_context_data(**kwargs)
        context["fragile"] = self.fragile
        return context


NAVIGATION_TOUR = steps_for("tests.navigation-tour", "h1", "#control", "#output")


class NavigationTourView(ControlsTourView):
    """Three steps, each attached to an element."""

    extra_context = {"tour": NAVIGATION_TOUR}


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

    extra_context = {
        "tour": steps_for("tests.missing-first-tour", "#absent", "h1", "#control")
    }


class MissingMiddleTourView(ControlsTourView):
    """The second step's element is not on the page."""

    extra_context = {
        "tour": steps_for("tests.missing-middle-tour", "h1", "#absent", "#control")
    }


class HiddenMiddleTourView(ControlsTourView):
    """The second step's element carries the hidden attribute."""

    extra_context = {
        "tour": steps_for("tests.hidden-middle-tour", "h1", "#secret", "#control")
    }


class InvalidSelectorTourView(ControlsTourView):
    """The second step's selector is not valid CSS."""

    extra_context = {
        "tour": steps_for("tests.invalid-selector-tour", "h1", "[[", "#control")
    }


class NothingShowableTourView(ControlsTourView):
    """Every step names an element that is not on the page."""

    extra_context = {
        "tour": steps_for("tests.nothing-showable-tour", "#absent", "#also-absent")
    }


class TwinTourView(ControlsTourView):
    """A step whose selector matches two elements."""

    extra_context = {"tour": steps_for("tests.twin-tour", ".twin", "#control")}


class FragileTourView(ControlsTourView):
    """The second step's element throws when Driver.js measures it."""

    extra_context = {
        "tour": steps_for("tests.fragile-tour", "h1", "#output", "#control")
    }
    fragile = "output"


class BareTourView(TemplateView):
    """A page with a tour, for comparing with the same page without one."""

    template_name = "test_controls.html"
    extra_context = {"tour": steps_for("tests.bare-tour", "h1", "#control")}


class NoTourControlsView(TemplateView):
    """The same page as BareTourView, with no tour."""

    template_name = "test_controls.html"


class ReplayView(TemplateView):
    """A page with a tour and a replay control carrying attributes of its own."""

    template_name = "test_replay.html"
    extra_context = {"tour": steps_for("tests.replay", "h1", "#control")}


class ReplayNoTourView(ReplayView):
    """The same page with no tour."""

    extra_context = None


class ReplayPointedAtView(ReplayView):
    """The second step points at the replay control."""

    extra_context = {
        "tour": steps_for("tests.replay-pointed-at", "h1", "#replay", "#control")
    }


class ReplayNothingShowableView(ReplayView):
    """Every step names an element that is not on the page."""

    extra_context = {
        "tour": steps_for("tests.replay-nothing-showable", "#absent", "#also-absent")
    }


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
            TourStep(title="Step 1", description="Text.", element="h1"),
            TourStep(title="Step 2", description="Text.", element="#control"),
        ],
        autoplay=False,
    )


class OnRequestView(ReplayView):
    """A page whose tour plays only when the replay control is used."""

    extra_context = {"tour": on_request_tour()}


VERSIONED_TOUR = steps_for("tests.versioned", "h1", "#control")


class VersionedTourView(ControlsTourView):
    """A page whose tour is routed at several versions, all seen as one tour."""

    extra_context = {"tour": VERSIONED_TOUR}


VERSION_TWO = Tour(name="tests.versioned", steps=VERSIONED_TOUR.steps, version=2)
VERSION_TWO_EDITED = Tour(
    name="tests.versioned",
    steps=[
        TourStep(title="Step 1", description="Text, with a typo fixed.", element="h1")
    ],
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
    extra_context = {"tour": on_request_tour()}


class ControlInBaseView(TemplateView):
    """A page with a tour, extending a base template that places the control."""

    template_name = "test_control_in_base_page.html"
    extra_context = {"tour": steps_for("tests.control-in-base", "h1", "#control")}


class ControlInBaseNoTourView(TemplateView):
    """A page with no tour, extending the base template that places the control."""

    template_name = "test_control_in_base_page.html"


APP_TOUR = Tour(
    name="app.page",
    steps=[
        TourStep(title="Step 1", description="Text.", element="h1"),
        TourStep(title="Step 2", description="Text.", element="#control"),
        TourStep(title="Step 3", description="Text."),
    ],
    version=2,
)
OFF_TOUR = steps_for("app.off", "h1", "#control")
UNTOUCHED_TOUR = steps_for("app.untouched", "h1", "#control")
OWN_TOUR = steps_for("tests.own", "h1")
REPLACEMENT_TOUR = Tour(
    name="tests.replacement",
    steps=[
        TourStep(title="Ours 1", description="Our first.", element="h1"),
        TourStep(title="Ours 2", description="Our second.", element="#control"),
    ],
)
REWORDED_TOUR = Tour(
    name="tests.reworded",
    steps=[
        APP_TOUR.steps[0],
        TourStep(title="Step 2", description="Reworded for us.", element="#control"),
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

    extra_context = {"tour": APP_TOUR}


class OffTourView(ReplayView):
    """A page of an installed app, whose tour a project turns off."""

    extra_context = {"tour": OFF_TOUR}


class UntouchedTourView(ReplayView):
    """A page of an installed app whose tour a project leaves alone."""

    extra_context = {"tour": UNTOUCHED_TOUR}


def overridden_function_view(request):
    """Render a function-based page of an installed app, whose tour is changed."""
    return render(request, "test_controls.html", {"tour": APP_TOUR})


class PartsTourView(TemplateView):
    """A tour whose first and last steps are attached and whose middle one is not."""

    template_name = "test_page.html"
    extra_context = {"tour": steps_for("tests.parts-tour", "h1", "", "#control")}


class StyleBeforeView(TemplateView):
    """A page whose own style sits before the package's stylesheet."""

    template_name = "test_style_before.html"
    extra_context = {"tour": steps_for("tests.style-before", "h1", "", "#control")}


class StyleAfterView(StyleBeforeView):
    """A page whose own style sits after the package's stylesheet."""

    template_name = "test_style_after.html"


class LayerBeforeView(StyleBeforeView):
    """A page whose own layered style sits before the package's stylesheet."""

    template_name = "test_layer_before.html"


class DesignSystemView(TemplateView):
    """A page whose base template loads a design system's stylesheet."""

    template_name = "test_design_system_page.html"
    extra_context = {"tour": steps_for("tests.design-system", "h1", "#control")}


class ScriptsNotDeferredView(TemplateView):
    """A page loading the package's scripts at the top of the head, without defer."""

    template_name = "test_scripts_not_deferred.html"
    extra_context = {"tour": steps_for("tests.not-deferred", "h1", "#control")}


class TourTwiceView(TemplateView):
    """A page whose template renders its tour twice."""

    template_name = "test_tour_twice.html"
    extra_context = {"tour": steps_for("tests.rendered-twice", "h1", "#control")}


THREE_HINTS = Hints(
    name="tests.browser.three",
    hints=[
        Hint(element="#first", title="First hint", description="One."),
        Hint(element="#second", title="Second hint", description="Two."),
        Hint(element="#third", title="Third hint", description="Three."),
    ],
)
OWN_BEACON_HINTS = Hints(
    name="tests.browser.own-beacon",
    buttonText="Shared button",
    beacon=Beacon(className="shared-beacon"),
    hints=[
        Hint(
            element="#first",
            title="Own",
            description="One.",
            buttonText="Own button",
            beacon=Beacon(className="own-beacon", animate=False),
        ),
        Hint(element="#second", title="Shared", description="Two."),
    ],
)
MISSING_ELEMENT_HINTS = Hints(
    name="tests.browser.missing",
    hints=[
        Hint(element="#first", title="First hint", description="One."),
        Hint(element="#absent", title="Absent hint", description="Nowhere."),
        Hint(element="#third", title="Third hint", description="Three."),
    ],
)
RAISED_HINTS = Hints(name=THREE_HINTS.name, hints=THREE_HINTS.hints, version=2)
OVERLAY_HINTS = Hints(
    name="tests.browser.overlay", overlay=True, hints=list(THREE_HINTS.hints)
)
IDENTIFIED_HINTS = Hints(
    name="tests.browser.identified",
    hints=[
        Hint(element="#first", id="alpha", title="Alpha", description="One."),
        Hint(element="#second", id="beta", title="Beta", description="Two."),
    ],
)
MOVED_HINTS = Hints(
    name=IDENTIFIED_HINTS.name,
    hints=[
        Hint(element="#third", id="alpha", title="Alpha", description="One."),
        Hint(element="#second", id="beta", title="Beta", description="Two."),
    ],
)
SHARED_ELEMENT_HINTS = Hints(
    name="tests.browser.shared-element",
    hints=[
        Hint(element="#first", title="Left", description="One."),
        Hint(element="#first", title="Right", description="Two."),
        Hint(element="#second", title="Other", description="Three."),
    ],
)
HINTS_TOUR = Tour(
    name="tests.browser.hints-tour",
    steps=[
        TourStep(title="Tour step", description="About a hint.", element="#first"),
    ],
)


class HintsView(TemplateView):
    """A page with three hints."""

    template_name = "test_hints_page.html"
    extra_context = {"hints": THREE_HINTS}


class OwnBeaconHintsView(HintsView):
    """A page whose first hint has a beacon and button text of its own."""

    extra_context = {"hints": OWN_BEACON_HINTS}


class MissingElementHintsView(HintsView):
    """A page whose second hint points at an element that is not there."""

    extra_context = {"hints": MISSING_ELEMENT_HINTS}


class HintsAndTourView(HintsView):
    """A page with hints and a tour that plays by itself."""

    extra_context = {"hints": THREE_HINTS, "tour": HINTS_TOUR}


class NoHintsView(TemplateView):
    """A page with a restore control and no hints."""

    template_name = "test_hints_page.html"


class HintsWithoutScriptView(TemplateView):
    """A page with hints whose template does not load the hints script."""

    template_name = "test_hints_no_script.html"
    extra_context = {"hints": THREE_HINTS}


class HintsAgainView(HintsView):
    """The same hints as the hints page, rendered at another address."""


class RaisedHintsView(HintsView):
    """The hints of the hints page, declared at a higher version."""

    extra_context = {"hints": RAISED_HINTS}


class OverlayHintsView(HintsView):
    """A page whose hints dim the page while a popover is open."""

    extra_context = {"hints": OVERLAY_HINTS}


class IdentifiedHintsView(HintsView):
    """A page whose hints have identifiers."""

    extra_context = {"hints": IDENTIFIED_HINTS}


class MovedHintsView(HintsView):
    """The identified hints, one of them now pointing at another element."""

    extra_context = {"hints": MOVED_HINTS}


class SharedElementHintsView(HintsView):
    """A page with two hints on one element, neither with an identifier."""

    extra_context = {"hints": SHARED_ELEMENT_HINTS}
