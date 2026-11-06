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
