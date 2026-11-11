# Replaying a tour

A tour plays by itself the first time a browser opens its page. A replay control is a button you
place in your own templates that plays the page's tour again, from its first step, whenever a
visitor presses it.

## Place the replay control

Write your own button in the template of the page that has the tour, and give it the
`data-page-tour-replay` attribute:

```html
<button type="button" class="btn btn-ghost" data-page-tour-replay>Show the tour</button>
```

The package's script makes every element marked `data-page-tour-replay` start the page's tour.
Using the control plays the tour from its first step even when the browser has already seen it.
Using it while the tour is playing starts the tour over from the first step.

Write `type="button"` on the control, so that it never submits a form it sits in.

The control does something only on a page whose template renders a tour with `{{ tour }}`, so
place it in the templates of those pages. If the button sits in a template that pages without a
tour share too, such as a base template, add `hidden` to it. The package's script loads on every
page, but it removes `hidden` only on a page with a tour, so the button stays hidden on the other
pages and when JavaScript is off:

```html
<button type="button" class="btn btn-ghost" data-page-tour-replay hidden>Show the tour</button>
```

## Give the control your own content and attributes

The control is your own element, so it holds what you put in it and carries the attributes you
give it: text, an icon or both, your classes, an `id`. The script adds no class, no style and no
attribute of its own, and removes only `hidden`. The button looks the way your stylesheet makes
it.

## Label an icon-only control

A button that holds only an icon has no name for a screen reader. Give it one with `aria-label`:

```html
<button type="button" class="icon-button" aria-label="Show the tour" data-page-tour-replay>
  <svg aria-hidden="true" width="16" height="16"><!-- your icon --></svg>
</button>
```

The control is a real button, so a visitor reaches it with the Tab key and presses it with Enter
or Space.

## Place the control more than once

Place as many controls as you like. Each one replays the same tour.

## Point a step at the control

The script sets up the control before the tour starts, so a step can point at it with `element`:

```python
TourStep(
    title="Come back to this tour",
    text="Press this button to see the tour again.",
    element="#replay-tour",
)
```

Give the control that `id`:
`<button type="button" id="replay-tour" data-page-tour-replay>Show the tour</button>`.
While a step shows, only the highlighted element can be used. Pressing the control during that
step starts the tour over from its first step.

## A tour that plays only on request

Some tours should never open by themselves, for example a long tour of an advanced page. Declare
the tour with `autoplay=False`, then place the replay control so a visitor can start it:

```python
from django.views.generic import TemplateView

from page_tours import Tour, TourStep

REPORTS_TOUR = Tour(
    name="reports",
    steps=[
        TourStep(title="Reports", text="Everything you have filed, in one place."),
        TourStep(
            title="Filters",
            text="Narrow the list by date or author.",
            element="#filters",
        ),
    ],
    autoplay=False,
)


class ReportsView(TemplateView):
    template_name = "reports.html"
    extra_context = {"tour": REPORTS_TOUR}
```

```django
<button type="button" data-page-tour-replay>Show the tour</button>
{{ tour }}
```

The tour does not open when a browser first visits the page, and a browser that has not seen it
is not changed by that. Pressing the control plays it from its first step, every time.

With no control on the page, a tour declared with `autoplay=False` never plays, so place one on
its page.

## Why a replay does not change what a browser has seen

A replay is recorded as seen, like any play. It does not change whether the tour plays by itself
on a later visit: a tour that the browser had seen stays seen, and a tour that plays by itself
the first time stays one that plays only once. See [Seen tours](tours.md#seen-tours).

## Why the control does nothing on a tour that cannot show

When no step of the tour can show, using the control does nothing. It adds nothing to the page
and raises no error.
