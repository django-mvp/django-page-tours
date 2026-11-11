"""The demo project's pages."""

from django.shortcuts import render
from django.views.generic import TemplateView

from page_tours import Tour, TourStep


class OverviewView(TemplateView):
    """What the package is, and which pages of this project show it."""

    template_name = "demo/overview.html"


class TourView(TemplateView):
    """A page with a tour that shows each kind of step."""

    template_name = "demo/tour.html"
    extra_context = {
        "tour": Tour(
            name="demo.tour",
            steps=[
                TourStep(
                    title="Welcome",
                    text="This step points at nothing, so it shows mid-page.",
                ),
                TourStep(
                    title="A disclosure",
                    text="Open it while this step shows. It stays usable.",
                    element="#demo-disclosure",
                ),
                TourStep(
                    title="An element that is not here",
                    text="Nothing on this page matches, so this step is skipped.",
                    element="#not-on-this-page",
                ),
                TourStep(
                    title="A text field",
                    text="Type here and press Enter. The page reloads with your text.",
                    element="#demo-field",
                ),
            ],
        )
    }


class PlaysOnceView(TemplateView):
    """A page whose tour plays by itself the first time a browser opens it."""

    template_name = "demo/plays_once.html"
    extra_context = {
        "tour": Tour(
            name="demo.plays-once",
            steps=[
                TourStep(
                    title="Plays once",
                    text=(
                        "This tour opened by itself. "
                        "It will not open again in this browser."
                    ),
                ),
                TourStep(
                    title="Play it again",
                    text=(
                        "The button in the page bar plays the tour again "
                        "from its first step."
                    ),
                    element="[aria-label='Demo pages'] button",
                ),
            ],
        )
    }


class OnRequestView(TemplateView):
    """A page whose tour plays only when the replay control is used."""

    template_name = "demo/on_request.html"
    extra_context = {
        "tour": Tour(
            name="demo.on-request",
            steps=[
                TourStep(
                    title="Only on request",
                    text="This tour did not open by itself. A control started it.",
                ),
                TourStep(
                    title="The page's own control",
                    text="This button sits next to the heading and starts the same tour.",
                    element="#demo-replay",
                ),
            ],
            autoplay=False,
        )
    }


class OwnLookView(TemplateView):
    """A page whose tour is styled by the page's own stylesheet."""

    template_name = "demo/own_look.html"
    extra_context = {
        "tour": Tour(
            name="demo.own-look",
            steps=[
                TourStep(
                    title="A look of its own",
                    text="This step points at nothing, so it shows mid-page.",
                ),
                TourStep(
                    title="An attached step",
                    text="The rest of the page is dimmed, and this paragraph is not.",
                    element="#demo-own-look-target",
                ),
            ],
        )
    }


CHANGED_TOUR_STEPS = [
    TourStep(
        title="A changed tour",
        text="This browser has not seen this version of the tour, so it opened.",
    ),
    TourStep(
        title="Its version",
        text="The heading says which version of the tour this page is at.",
        element="#demo-version",
    ),
]


class ChangedTourView(TemplateView):
    """A page whose tour is routed at two versions, so a new one can be seen once.

    Both routes pass their tour to ``as_view`` in ``extra_context``. The two tours
    have one name, so they are seen as one tour and differ only in version.
    """

    template_name = "demo/changed_tour.html"


FIRST_VERSION = Tour(name="demo.changed-tour", steps=CHANGED_TOUR_STEPS)
NEW_VERSION = Tour(name="demo.changed-tour", steps=CHANGED_TOUR_STEPS, version=2)

FUNCTION_VIEW_TOUR = Tour(
    name="demo.function-view",
    steps=[
        TourStep(
            title="From a function",
            text="A function-based view rendered this page and passed this tour in its context.",
        ),
        TourStep(
            title="The same tour",
            text="The page renders it with {{ tour }}, as a class-based view's page does.",
            element="#demo-function-view",
        ),
    ],
)


def function_view(request):
    """Render a page whose tour a function-based view passes in its context."""
    return render(request, "demo/function_view.html", {"tour": FUNCTION_VIEW_TOUR})


class DriverOptionsView(TemplateView):
    """A page whose tour sets some of Driver.js's options on the Tour."""

    template_name = "demo/driver_options.html"
    extra_context = {
        "tour": Tour(
            name="demo.driver-options",
            steps=[
                TourStep(
                    title="Options of its own",
                    text="This tour shows how far through it you are, below.",
                ),
                TourStep(
                    title="Where they are set",
                    text="Each is a field of the Tour, named like Driver.js's option.",
                    element="#demo-driver-options",
                ),
            ],
            show_progress=True,
            progress_text="Step {{current}} of {{total}}",
            next_btn_text="Onwards",
        )
    }
