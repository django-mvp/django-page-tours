"""The demo project's pages."""

from django.views.generic import TemplateView

from page_tours import Tour, TourStep


class OverviewView(TemplateView):
    """What the package is, and which pages of this project show it."""

    template_name = "demo/overview.html"


class TourView(TemplateView):
    """A page with a tour that shows each kind of step."""

    template_name = "demo/tour.html"
    tour = Tour(
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
        ]
    )


class PlaysOnceView(TemplateView):
    """A page whose tour plays by itself the first time a browser opens it."""

    template_name = "demo/plays_once.html"
    tour = Tour(
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
        ]
    )


class OnRequestView(TemplateView):
    """A page whose tour plays only when the replay control is used."""

    template_name = "demo/on_request.html"
    tour = Tour(
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

    Both routes pass their tour to ``as_view``, so both are seen as this view's
    tour and differ only in version.
    """

    template_name = "demo/changed_tour.html"
    tour = None


FIRST_VERSION = Tour(steps=CHANGED_TOUR_STEPS)
NEW_VERSION = Tour(steps=CHANGED_TOUR_STEPS, version=2)
