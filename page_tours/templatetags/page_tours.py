"""Template tags that put a page's tour on the page."""

from django import template
from django.utils.html import escape
from django.utils.translation import pgettext

from page_tours.parts import TourParts
from page_tours.tours import Tour

register = template.Library()


@register.inclusion_tag("page_tours/page_tour.html", takes_context=True)
def page_tour(context):
    """Emit the tour of the page being rendered, or nothing when it has none.

    Place it once in the ``<head>`` of the base template.

    Args:
        context: The template context, supplied by Django.

    Returns:
        The context for ``page_tours/page_tour.html``: the tour's name and
        version, whether it plays by itself, its steps in the form Driver.js
        takes, the labels of its controls in the active language and the classes
        each part of a shown step carries, or an empty payload when the page has
        no tour.
    """
    tour = Tour.for_page(context)
    if tour is None:
        return {"payload": None}
    return {
        "payload": {
            "id": tour.name,
            "version": tour.version,
            "autoplay": tour.autoplay,
            "steps": tour.as_driver_steps(),
            # Driver.js writes the button labels as HTML and the close label as an
            # attribute value, so only the button labels are escaped.
            "controls": {
                "next": escape(pgettext("page tour control", "Next")),
                "previous": escape(pgettext("page tour control", "Previous")),
                "done": escape(pgettext("page tour control", "Done")),
                "close": pgettext("page tour control", "Close"),
            },
            "parts": TourParts.classes(),
        }
    }
