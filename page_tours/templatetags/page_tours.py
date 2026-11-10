"""Template tags that put a page's tour on the page."""

from django import template
from django.forms.utils import flatatt
from django.utils.html import escape, format_html
from django.utils.translation import gettext_lazy, pgettext

from page_tours.tours import Tour, tour_id

register = template.Library()


@register.inclusion_tag("page_tours/page_tour.html", takes_context=True)
def page_tour(context):
    """Emit the tour of the page being rendered, or nothing when it has none.

    Place it once in the ``<head>`` of the base template.

    Args:
        context: The template context, supplied by Django.

    Returns:
        The context for ``page_tours/page_tour.html``: the tour's id and
        version, whether it plays by itself, its steps in the form Driver.js takes and the labels of
        its controls in the active language, or an empty payload when the page has
        no tour.
    """
    tour = Tour.for_page(context)
    if tour is None:
        return {"payload": None}
    return {
        "payload": {
            "id": tour_id(context),
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
        }
    }


@register.simple_block_tag(takes_context=True)
def page_tour_replay(context, content, **attrs):
    """Place a control that plays the page's tour again, from its first step.

    The control is a button holding the block's content. It shows only on a page
    with a tour, and only when JavaScript is on. The package adds no class or
    style to it.

    Args:
        context: The template context, supplied by Django.
        content: The rendered block. When it is only whitespace, a translated
            default text is used.
        **attrs: Attributes for the button. Underscores in a name become hyphens,
            so ``aria_label`` renders ``aria-label``. ``type`` is ignored: the
            button never submits a form.

    Returns:
        A ``<template>`` holding the button, or an empty string when the page
        has no tour.
    """
    if Tour.for_page(context) is None:
        return ""
    attributes = {
        name.replace("_", "-"): value for name, value in attrs.items() if name != "type"
    }
    return format_html(
        '<template data-page-tour-replay><button type="button"{}>{}</button>'
        "</template>",
        flatatt(attributes),
        content if content.strip() else gettext_lazy("Show the tour"),
    )
