"""The demo project's pages."""

from django.views.generic import TemplateView


class OverviewView(TemplateView):
    """What the package is, and which pages of this project show it."""

    template_name = "demo/overview.html"
