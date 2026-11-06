"""Template tags that put a page's tour on the page."""

from django import template

from page_tours.tours import Tour

register = template.Library()


@register.inclusion_tag("page_tours/page_tour.html", takes_context=True)
def page_tour(context):
    """Emit the tour of the page being rendered, or nothing when it has none.

    Place it once in the ``<head>`` of the base template.

    Args:
        context: The template context, supplied by Django.

    Returns:
        The context for ``page_tours/page_tour.html``: the steps in the form
        Driver.js takes, empty when the page has no tour.
    """
    tour = Tour.for_page(context)
    return {"steps": tour.as_driver_steps() if tour else []}
