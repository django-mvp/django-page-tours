# Adding a tour to a page

A tour is a short list of steps that Driver.js shows over one page, each step pointing at a part
of the page with a title and a sentence. You declare the tour in Python, next to the view that
renders the page. The page plays it by itself the first time a browser opens it.

## Before you start

Include the package's stylesheet and scripts in your base template, once for the whole project.
[Installation](installation.md#include-the-packages-files-in-your-base-template) shows the three
lines.

A page with a tour then needs two things: the view puts the tour in the template context under
`tour`, and the page's template outputs it with `{{ tour }}`.

## Name the tour

Every tour has a name, given where you declare it:

```python
Tour(name="dashboard", steps=[...])
```

The name is how the tour is known. A browser remembers that it has seen the tour by its name, and
a project changes an installed app's tour by its name (see
[Tours from reusable apps](tours-from-reusable-apps.md)). Pick one that stays put:

- **Keep the name when you change the tour.** Renaming it makes it a different tour, so every
  visitor sees it again. To show a changed tour again on purpose, raise its version instead (see
  [Show a changed tour again](#show-a-changed-tour-again)).
- **Give each tour its own name.** Two tours with one name share one seen state, so seeing one
  hides the other. Django's `check` command warns with `page_tours.W005` when tours with different
  steps are declared with the same name. One tour used on several views is still one tour, and so
  is one tour declared at two versions.
- **In a reusable app, start the name with the app label:** `"<app_label>.<tour>"`, such as
  `"library.book"`. That keeps it apart from the tours of the project and of every other app.
- **The name is in the page's source,** sent to the browser with the steps. Do not put anything
  in it you would not show a visitor.

A name that is not a string with something in it raises `ImproperlyConfigured` when the tour is
declared.

## Add a tour to a class-based view

Put the tour in the view's context under `tour`. `extra_context` is the shortest way:

```python
from django.views.generic import TemplateView

from page_tours import Tour, TourStep

DASHBOARD_TOUR = Tour(
    name="dashboard",
    steps=[
        TourStep(title="Welcome", text="A quick look around."),
        TourStep(
            title="Your projects",
            text="Everything you work on is listed here.",
            element="#projects",
        ),
    ],
)


class DashboardView(TemplateView):
    template_name = "dashboard.html"
    extra_context = {"tour": DASHBOARD_TOUR}
```

A view that builds its context in `get_context_data` adds the tour there instead:

```python
class DashboardView(TemplateView):
    template_name = "dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tour"] = DASHBOARD_TOUR
        return context
```

The tour is on every URL that routes to the view, and on every subclass that inherits the
context. To put a tour on one URL only, give it through `as_view`:
`DashboardView.as_view(extra_context={"tour": DASHBOARD_TOUR})`.

## Add a tour to a function-based view

Pass the tour in the template context under `tour`, like any other value:

```python
from django.shortcuts import render


def dashboard(request):
    return render(request, "dashboard.html", {"tour": DASHBOARD_TOUR})
```

Declare the tour at module level, as above, rather than inside the view. It is then checked when
the module is imported, and the system checks know its name.

## Output the tour in the page's template

Place `{{ tour }}` in the template of the page:

```django
{% extends "base.html" %}
{% block content %}
  <h1>Dashboard</h1>
  <ul id="projects">...</ul>
  {{ tour }}
{% endblock content %}
```

`{{ tour }}` outputs the tour's steps as a `<script type="application/json">` element, which the
package's script reads and plays. It draws nothing where it stands, so it can sit anywhere in the
page, and where it sits does not decide where the tour shows. It needs no tag library: a `Tour`
renders itself, and Django does not escape it.

- **A page has one tour.** Render `{{ tour }}` once. Should it render twice, the first tour plays
  and the second is left alone.
- **`{{ tour }}` with no tour in the context renders nothing,** so a template shared by pages with
  and without a tour can hold it.
- **A tour that a project has turned off renders nothing,** and one it has replaced renders the
  replacement. See [Tours from reusable apps](tours-from-reusable-apps.md).
- **`str(tour)` is the same markup.** Use `repr(tour)` to see the tour's fields.

## Seen tours

A tour is seen from the moment it starts playing, however it ends: the visitor steps to the end,
closes it at any step, or leaves the page while a step shows. A tour that is seen does not play
by itself again in that browser.

- **It is kept in the visitor's browser only.** The browser stores one entry in its local
  storage for each seen tour. Nothing is stored on the server, and no cookie is set.
- **The tour's name identifies it.** A tour shown on many addresses is one tour, so seeing it at
  one address hides it at the others. Renaming or moving the view changes nothing, and renaming
  the tour makes it a different tour, so every visitor is shown it again. See
  [Name the tour](#name-the-tour).
- **A tour that could not play is not seen.** When no step can show, the tour does not start and
  is not remembered.
- **A browser that blocks storage sees the tour on every visit.** The page raises no error.

## Show a changed tour again

Editing a tour does not bring it back to people who have seen it. When a tour changes enough that
they should see it again, for example because the page gained a section or a control moved, give
it a new version:

```python
DASHBOARD_TOUR = Tour(
    name="dashboard",
    steps=[
        TourStep(title="Welcome", text="A quick look around."),
        TourStep(
            title="Reports",
            text="Your reports are here now.",
            element="#reports",
        ),
    ],
    version=2,
)
```

A browser that saw any other version plays the tour by itself the next time it opens the page,
once, and then it is seen again. A browser that has never seen the tour plays it once, as before.

- **A tour without a version is at version 1.** Tours seen before you added a version count as
  seen at version 1, so adding `version=1` changes nothing.
- **Leave the version alone for a small edit.** A fixed typo or a reworded step keeps its version,
  and nobody is shown the tour again for it. The package never works out a version from the
  steps.
- **A tour that plays only on request stays that way.** A new version of a tour declared with
  `autoplay=False` still waits for the replay control.
- **Any other number counts.** Lowering the version, after a revert for example, also plays the
  tour once more.

A version that is not a whole number of 1 or more raises `ImproperlyConfigured` when the tour is
declared.

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

## Translate a tour

A tour is shown in the language the page is served in: the steps you write and the tour's own
controls alike.

Titles and texts are plain text. Markup characters in them are escaped, so
`<b>bold</b>` shows as those characters and not as bold text.

Mark a step for translation with `gettext_lazy`. It is converted when the page is rendered, in
the visitor's language:

```python
from django.utils.translation import gettext_lazy as _

TourStep(title=_("Your projects"), text=_("Everything is listed here."))
```

The tour's own controls are the next, previous and done buttons and the label a screen reader
gives the close button. Their text comes from the package's catalogue, under the context
`page tour control`. The package ships an English catalogue in
`page_tours/locale/en/LC_MESSAGES/django.po`. To show the controls in another language, add the
four entries to your project's catalogue for that language and compile it:

```po
msgctxt "page tour control"
msgid "Next"
msgstr "Weiter"

msgctxt "page tour control"
msgid "Previous"
msgstr "Zurück"

msgctxt "page tour control"
msgid "Done"
msgstr "Fertig"

msgctxt "page tour control"
msgid "Close"
msgstr "Schließen"
```

A control with no translation in the page's language shows in English. Like step text, a
translated label is shown as text, never as markup.

## Pass Driver.js options of its own

Driver.js has more options than `Tour` and `TourStep` set. Pass any of them with
`driver_options`, a mapping the package hands to the Driver.js constructor as it is:

```python
Tour(
    name="dashboard",
    steps=[...],
    driver_options={"showProgress": True, "progressText": "{{current}} / {{total}}"},
)
```

The options reach the page in its source, as JSON, so every value needs a JSON form: strings,
numbers, booleans, `None`, lists and mappings of them, and strings marked for translation. A
function such as an `onNextClick` hook has none. Options that are not a mapping, a name that is
not a string and a value with no JSON form raise `ImproperlyConfigured` when the tour is declared.

The package keeps the settings it sets itself, and an option of the same name changes nothing:

- `steps`
- `skipMissingElement`, so a missing or hidden element is still skipped
- `nextBtnText`, `prevBtnText`, `doneBtnText` and `closeBtnLabel`, which come from the
  package's catalogue
- `onPopoverRender`, `onDestroyStarted` and `onDestroyed`

Driver.js writes some options into the page as markup, `progressText` among them. They are passed
as you wrote them and are not escaped, so never build one from a visitor's input.

The package does not check what an option does. The options Driver.js takes are listed in its
[configuration reference](https://driverjs.com/docs/configuration), and whether one works with
the release the package ships, recorded in `page_tours/static/page_tours/vendor/`, is yours to
check. An option can also undo what the package promises, such as `allowClose: False`, which
leaves a visitor no way out of the tour but its last step.

A tour that a project replaces through `PAGE_TOURS_OVERRIDES` plays with the replacement's
options, not the replaced tour's.

## See a tour in the demo project

The demo project in `demo/` has a tour page at `/tour/`, linked from the bar at the top of every
demo page. Its tour has a step attached to nothing, a step attached to a disclosure, a step
attached to an element that is not on the page, and a closing step attached to a text field. To
run the demo, follow [Run the demo project](../contributing/set-up-a-development-environment.md#run-the-demo-project)
and open the page to see all of them.

The changed-tour page at `/changed-tour/` routes one tour at two versions, at `/changed-tour/`
and `/changed-tour/new-version/`. Open one and then the other to see a new version play once
more in a browser that saw the first.

The function-view page at `/function-view/` is rendered by a function-based view that passes its
tour in the template context. Every demo page outputs its tour with `{{ tour }}` in its own
template, and the demo's base template includes the package's files.

## Why a visitor can always use the page

This is what a visitor sees when a page with a tour opens in their browser.

- **The tour plays by itself the first time a browser opens the page,** and not again in
  that browser. See [Seen tours](#seen-tours).
- **Moving and closing.** A step offers next, back and close. Next on the last step ends the
  tour, and so does close. Nothing of the tour stays on the page afterwards.
- **The keyboard does everything.** The arrow keys move forward and back, Escape closes the
  tour, and Tab moves between the step's buttons and its highlighted element. Focus moves into
  each step as it shows. When the tour ends, at any step and however it ends, focus goes back to
  where it was before the tour started, such as the replay control that started it.
- **Screen readers announce each step.** A step is a dialog named by its title and described by
  its text, so a screen reader reads both as the step opens.
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

## Why a mistake in a tour is an error, not a skipped step

A tour is checked as the module that declares it is imported: at start-up for the development
server and `manage.py check`, and at the latest on the first request a production server handles.
A mistake raises an error there instead of being shown to a visitor. A tour with no name or no
steps, and a step with an empty title or empty text (whitespace counts as empty), raise
`ImproperlyConfigured`.

## Why a tour never shows on an error page

A tour is on a page only when the view that renders the page puts it in the context. When a view
raises, such as `Http404`, Django renders the error page instead, with a template and a context
of its own. There is no tour in that context, so `{{ tour }}` renders nothing there, even when
the error page extends the same base template.
