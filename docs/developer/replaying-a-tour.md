# Replaying a tour

A tour plays by itself the first time a browser opens its page. A replay control is a button you
place in your own templates that plays the page's tour again, from its first step, whenever a
visitor presses it.

## Place the replay control

Load the tag library, then place the tag where the button should appear. A base template is the
usual place, because the control then shows on every page that has a tour and on no other:

```django
{% load page_tours %}
<nav>
  <a href="{% url 'home' %}">Home</a>
  {% page_tour_replay class="btn btn-ghost" %}
    Show the tour
  {% endpage_tour_replay %}
</nav>
```

The control shows only where both of these are true:

- **The page has a tour.** On a page with no tour the tag renders nothing, so a control placed once
  in a base template appears only where there is something to replay.
- **JavaScript is on.** The button does nothing without the starter script, so it is not shown
  when JavaScript is off.

Using the control plays the tour from its first step even when the browser has already seen it.
Using it while the tour is playing starts the tour over from the first step.

## Give the control your own content and attributes

The block between the tags is the content of the button. Put text, an icon or both in it. The
package adds no class and no style of its own, so the button looks the way your stylesheet makes
it.

Every `name="value"` argument becomes an attribute of the button. An underscore in a name becomes
a hyphen, so `data_role="replay"` renders `data-role="replay"`. Values are escaped. The button is
always `type="button"`, and a `type` argument is ignored, so the control never submits a form.

If you leave the block empty, the button holds a translated default text.

## Label an icon-only control

A button that holds only an icon has no name for a screen reader. Give it one with `aria_label`:

```django
{% page_tour_replay class="icon-button" aria_label="Show the tour" %}
  <svg aria-hidden="true" width="16" height="16"><!-- your icon --></svg>
{% endpage_tour_replay %}
```

The control is a real button, so a visitor reaches it with the Tab key and presses it with Enter
or Space.

## Place the control more than once

Place the tag as many times as you like. Each button replays the same tour.

## Point a step at the control

The control is in the page before the tour starts, so a step can point at it with `element`:

```python
TourStep(
    title="Come back to this tour",
    text="Press this button to see the tour again.",
    element="#replay-tour",
)
```

Give the control that `id`: `{% page_tour_replay id="replay-tour" %}Show the tour{% endpage_tour_replay %}`.
While a step shows, only the highlighted element can be used. Pressing the control during that
step starts the tour over from its first step.

## A tour that plays only on request

Some tours should never open by themselves, for example a long tour of an advanced page. Declare
the tour with `autoplay=False`, then place the replay control so a visitor can start it:

```python
from django.views.generic import TemplateView

from page_tours import Tour, TourStep


class ReportsView(TemplateView):
    template_name = "reports.html"
    tour = Tour(
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
```

```django
{% load page_tours %}
{% page_tour_replay %}Show the tour{% endpage_tour_replay %}
```

The tour does not open when a browser first visits the page, and a browser that has not seen it
is not changed by that. Pressing the control plays it from its first step, every time.

With no control on the page, a tour declared with `autoplay=False` never plays. Place the control
in your base template, as in [Place the replay control](#place-the-replay-control), so it shows
on every page that has a tour.

## Why a replay does not change what a browser has seen

A replay is recorded as seen, like any play. It does not change whether the tour plays by itself
on a later visit: a tour that the browser had seen stays seen, and a tour that plays by itself
the first time stays one that plays only once. See [Seen tours](tours.md#seen-tours).

## Why the control does nothing on a tour that cannot show

When no step of the tour can show, using the control does nothing. It adds nothing to the page
and raises no error.
