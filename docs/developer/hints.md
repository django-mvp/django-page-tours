# Adding hints to a page

Hints are small pulsing markers, called beacons, that sit on parts of a page. A visitor opens
them in any order, reads what they say and carries on. Unlike a [tour](tours.md), hints do not
take over the page: it stays usable while one is open, and a visitor can ignore them all. You
declare the hints in Python, next to the view that renders the page, and Driver.js shows them.

## Before you start

Include the package's stylesheet and scripts in your base template, and Driver.js's hints
script beside them. [Installation](installation.md#include-the-packages-files-in-your-base-template)
shows the lines.

A page with hints then needs two things: the view puts the hints in the template context under
`hints`, and the page's template outputs them with `{{ hints }}`.

## Declare the hints of a page

Three classes describe hints, and each mirrors an object of Driver.js:

- `Hints` is the page's hints: a name, the list of hints, and the options that apply to all of
  them.
- `Hint` is one hint: the element it is about, a title and a description.
- `Beacon` is the marker of a hint.

```python
from django.views.generic import TemplateView

from page_tours import Beacon, Hint, Hints

REPORT_HINTS = Hints(
    name="reports.quarterly",
    hints=[
        Hint(
            element="#export",
            title="Export the report",
            description="Download this quarter's figures as a spreadsheet.",
        ),
        Hint(
            element="#figures",
            title="The figures",
            description="Each row is one month.",
            beacon=Beacon(side="left", align="center"),
        ),
    ],
)


class ReportView(TemplateView):
    template_name = "report.html"
    extra_context = {"hints": REPORT_HINTS}
```

Place `{{ hints }}` in the page's template, once:

```django
{% extends "base.html" %}
{% block content %}
  <h1>Quarterly report</h1>
  <button id="export" type="button">Export</button>
  <table id="figures">...</table>
  {{ hints }}
{% endblock content %}
```

`{{ hints }}` outputs a `<script id="page-tours-hints" type="application/json">` element, which
the package's script reads and shows. It draws nothing where it stands. It needs no tag library:
`Hints` renders itself, and Django does not escape it. The same applies as for a tour:

- **Declare the hints at module level,** so the system checks know their name.
- **`{{ hints }}` with no hints in the context renders nothing,** so a template shared by pages
  with and without hints can hold it.
- **A function-based view** passes the hints in the context it renders with, as it passes a tour:
  `render(request, "report.html", {"hints": REPORT_HINTS})`.
- **A page without hints is unaffected.** Nothing shows, and nothing is stored.

## Name the hints

Every set of hints has a name, given where you declare it. A browser remembers which hints a
visitor dismissed by the name, and a project changes a reusable app's hints by it. Choose a
name that stays put, and in a reusable app start it with the app label, as for a tour.

**Hints, tours and checklists share one namespace of names.** A name belongs to one declaration,
whether it is a `Tour`, a `Hints` or a `Checklist`. Django's `check` command warns with `page_tours.W005` when two different
declarations are given one name.

A name that is not a string with something in it raises `ImproperlyConfigured` when the hints
are declared. An empty list of hints is allowed: the page renders and shows no beacon.

## Set the options of the hints

`Hints`, `Hint` and `Beacon` take Driver.js's options as fields, named as Driver.js names them.
See the [Driver.js hints reference](https://driverjs.com/docs/hints) for what each does. The
package does not check their values: what you write is what Driver.js receives.

A field of a `Hint` or a `Beacon` that you leave out is not sent, and the value set on the `Hints`
applies, or else Driver.js's own default.

### Options of the hints

| Field | Default | What it does |
|---|---|---|
| `beacon` | none | The `Beacon` of every hint that has none of its own. |
| `buttonText` | "Got it", in the active language | The text of every popover's button. |
| `popoverClass` | `""` | A class added to every popover. |
| `popoverOffset` | `10` | The distance between the popover and its element, in pixels. |
| `overlay` | `False` | Whether the page is dimmed while a popover is open. |
| `overlayColor` | `"#000"` | The colour of the overlay. |
| `overlayOpacity` | `0.7` | The opacity of the overlay, from 0 to 1. |
| `version` | `1` | See [Show changed hints again](#show-changed-hints-again). |

### Options of a hint

| Field | Default | What it does |
|---|---|---|
| `element` | required | A CSS selector for the element the hint is about. |
| `title` | none | The heading of the popover. Give every hint one. |
| `description` | none | The body of the popover. |
| `id` | the hint's position | What a browser remembers the hint was dismissed under. |
| `beacon` | the hints' | The `Beacon` of this hint. |
| `side`, `align` | Driver.js's | Where the popover sits against the element. |
| `popoverClass` | the hints' | A class added to this hint's popover. |
| `showButton` | the hints' | Whether the popover shows its button. |
| `buttonText` | the hints' | The text of the popover's button. |

### Options of a beacon

| Field | Default | What it does |
|---|---|---|
| `side`, `align` | Driver.js's | Where the beacon sits against the element. |
| `animate` | Driver.js's | Whether the beacon pulses. |
| `className` | none | A class added to the beacon. |
| `offsetX`, `offsetY` | Driver.js's | How far the beacon moves across and down, in pixels. |

Titles, descriptions and button text are passed to Driver.js as they are, and it writes them into
the page as HTML. Never build one from a visitor's input.

### Options that are not available

Driver.js options whose value is a JavaScript function cannot be written in Python, so `Hints`
and `Hint` leave them out: `onDismiss`, `onButtonClick` and `onPopoverRender`. One consequence is
that a hint's button only dismisses the hint. It cannot start a [tour](tours.md). Put a control of
your own on the page for that (see [Replay a tour](replaying-a-tour.md)).

## Give every hint a title

A beacon is a button with no text of its own. The package names it with the hint's title, in the
language of the page, so a screen reader announces "Export the report" rather than nothing. A hint
without a title has a beacon without a name.

## Dismissal

A visitor opens a hint, reads it and presses its button. The hint is dismissed, and its beacon goes
for good in that browser, until you raise the version of the hints or the visitor brings the hints
back with the [restore control](#let-visitors-bring-the-hints-back). The hints they did not
dismiss still show.

- **It is kept in the visitor's browser only.** The browser stores one entry in its local storage
  for the hints, holding the version and which hints were dismissed. Nothing is stored on the
  server, and no cookie is set.
- **A hint is remembered by its `id`, or by its `element` when it has none.** Give a hint an `id`
  to keep its dismissal when you change its element.
- **Give two hints on one element identifiers.** Hints with no `id` that name the same element
  share what is remembered, so dismissing one dismisses both.
- **A hint you add shows its beacon,** and the ones a visitor dismissed stay dismissed. A dismissed
  hint you remove, or whose `id` you rename, leaves a record that is ignored.
- **A browser that blocks storage shows every hint on every visit,** and the page raises no
  error.

## Show changed hints again

Editing hints does not bring them back for visitors who dismissed them. When the hints have
changed enough that they should read them again, raise the version:

```python
REPORT_HINTS = Hints(name="reports.quarterly", hints=[...], version=2)
```

A browser that dismissed hints at any other version shows every hint again, once. Lowering the
version does the same. Leave the version alone for a fixed typo.

## Let visitors bring the hints back

Mark an element of your own with `data-page-hints-restore` to make it a control that shows every
dismissed beacon again, without reloading the page. Write it `hidden`:

```html
<button type="button" data-page-hints-restore hidden>Show the hints again</button>
```

The package's script removes `hidden` on a page with hints. On a page without hints, and with
JavaScript off, it stays hidden, so the control can sit in a template shared by every page. Place
it more than once and each one brings the hints back.

## Hints and a tour on one page

A page can render both `{{ hints }}` and `{{ tour }}`. While the tour plays, the beacons are
hidden, so they do not sit over it, and they return when it ends. A step of the tour can point at
an element a hint is about.

## Style the hints

A hint's popover carries the same parts as a tour step, so the classes you give those parts apply
to a hint too. The beacon is a part of its own, named `beacon`, with the documented class name
`page-tour-beacon`. See [Styling tours](styling-tours.md#style-hints). A single beacon can also
take a class through `Beacon(className=...)`, which follows the classes of the part.

## Change the hints of a reusable app

An app ships hints the same way a project does. A project replaces them or turns them off with
`PAGE_TOURS_OVERRIDES`, by name, as it does a tour: the value is the dotted path of a `Hints` to
play in their place, or `None`. The replacement must be a `Hints`, and a tour in its place
raises `ImproperlyConfigured`. See [Tours from reusable apps](tours-from-reusable-apps.md).

## See it in the demo project

The demo project's Hints page is a report with four hints, a restore control and a tour that the
hints step aside for.
