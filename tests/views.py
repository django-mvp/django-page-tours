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
