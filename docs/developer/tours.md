# Adding a tour to a page

A tour is a short list of steps that Driver.js shows over one page, each step pointing at a part
of the page with a title and a sentence. You declare the tour in Python, next to the view that
renders the page. The page plays it when it opens in the browser.

## Set up the tour tag once

Every page that can carry a tour needs two things in its base template and its settings. You do
this once for the whole project.

1. Load the tag library and place the tag in the `<head>` of your base template:

   ```django
   {% load page_tours %}
   <head>
     ...
     {% page_tour %}
   </head>
   ```

2. Check that `django.template.context_processors.request` is listed in the
   `context_processors` option of your `DjangoTemplates` backend in `TEMPLATES`:

   ```python
   TEMPLATES = [
       {
           "BACKEND": "django.template.backends.django.DjangoTemplates",
           "OPTIONS": {
               "context_processors": [
                   "django.template.context_processors.request",
                   # ...
               ],
           },
           # ...
       },
   ]
   ```

A page with no tour gets nothing from the tag: no script, no stylesheet, no reference to
Driver.js. A page with a tour gets the Driver.js stylesheet and script from your own static
files, and the page's steps.

Django's `check` command warns with `page_tours.W001` when no `DjangoTemplates` backend lists
the request context processor. Without it a tour on a function-based view is never found.

## Add a tour to a class-based view

Set `tour` on a view built on Django's generic views, which put `view` in the template context:

```python
from django.views.generic import TemplateView

from page_tours import Tour, TourStep


class DashboardView(TemplateView):
    template_name = "dashboard.html"
    tour = Tour(
        steps=[
            TourStep(title="Welcome", text="A quick look around."),
            TourStep(
                title="Your projects",
                text="Everything you work on is listed here.",
                element="#projects",
            ),
        ]
    )
```

The tour is on every URL that routes to the view.

## Add a tour to a function-based view

Decorate the view with `with_tour`. The page the view renders carries the tour:

```python
from django.shortcuts import render

from page_tours import Tour, TourStep, with_tour


@with_tour(Tour(steps=[TourStep(title="Welcome", text="A quick look around.")]))
def dashboard(request):
    return render(request, "dashboard.html")
```

The tag finds the tour through the request, so the request context processor from the setup
above must be listed.

## Attach a step to an element, or to nothing

A step with `element` points at the first element on the page matching that CSS selector. Driver.js
highlights it and places the step beside it:

```python
TourStep(title="Your projects", text="Everything is listed here.", element="#projects")
```

A step without `element` is attached to nothing. Driver.js shows it in the middle of the page,
which suits a welcome or a closing step:

```python
TourStep(title="Welcome", text="A quick look around.")
```

## Translate a step

Titles and texts are plain text. Markup characters in them are escaped, so
`<b>bold</b>` shows as those characters and not as bold text.

Mark a step for translation with `gettext_lazy`. It is converted when the page is rendered, in
the visitor's language:

```python
from django.utils.translation import gettext_lazy as _

TourStep(title=_("Your projects"), text=_("Everything is listed here."))
```

## See a tour in the demo project

The demo project in `demo/` has a tour page at `/tour/`, linked from the bar at the top of every
demo page. Its tour has a step attached to nothing, a step attached to a disclosure, a step
attached to an element that is not on the page, and a closing step attached to a text field. Run
`python manage.py runserver` from the repository root and open the page to see all of them.

## Why a visitor can always use the page

This is what a visitor sees when a page with a tour opens in their browser.

- **The tour plays every time the page opens.** Nothing is remembered between visits.
- **Moving and closing.** A step offers next, back and close. Next on the last step ends the
  tour, and so does close. Nothing of the tour stays on the page afterwards.
- **Only the highlighted element can be used while a step shows.** The rest of the page is dimmed.
  One click anywhere on the dimmed part closes the tour, so the rest of the page is one click away.
- **Steps whose element cannot be shown are skipped,** going forward and going back. That covers
  an element that is not on the page, one that is hidden, and a selector that is not valid CSS.
  The first step shown is the first one that can be.
- **A tour whose every element is missing does not play.** The page opens as if it had no tour.
- **A tour that fails ends, and the page keeps working.** If the Driver.js file cannot be loaded,
  fails while starting, or a step raises an error while the tour plays, the tour ends and
  everything it added to the page is removed. Every control on the page works afterwards.
- **With JavaScript off nothing of the tour shows.** The page looks and lays out exactly as it
  does on a page with no tour.

## Why a mistake in a tour stops the project at start-up

A tour is declared as the module that holds it is imported, so a mistake stops the project
starting and never reaches a visitor. A tour with no steps, and a step with an empty title or
empty text (whitespace counts as empty), raise `ImproperlyConfigured`.

## Why a tour never shows on an error page

A tour is found only from the page its own view renders. When a view raises, such as `Http404`,
Django renders the error page instead, and the tour is not on it, even when the error page
extends the same base template.
