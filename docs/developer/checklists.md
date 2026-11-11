# Adding a checklist to a page

A checklist is a panel in the corner of a page that lists what a visitor can do there: take a
tour, open a page, do something in the app. It shows how many items are done, and a visitor can
close the panel and open it again from a small launcher. You declare the checklist in Python, next
to the view or the context processor that puts it on the page, and Driver.js shows it.

## Before you start

Include the package's stylesheet and scripts in your base template, and Driver.js's checklist
script beside them. [Installation](installation.md#include-the-packages-files-in-your-base-template)
shows the lines.

A page with a checklist then needs two things: a view or a context processor puts the checklist
in the template context under `checklist`, and the page's template outputs it with
`{{ checklist }}`.

## Declare a checklist

Three classes describe a checklist, and each mirrors an object of Driver.js:

- `Checklist` is the checklist: a name, its items, and the options that apply to all of them.
- `ChecklistItem` is one item: an id, a title and a description.
- `Offset` is how far the checklist sits from the corner of the window.

```python
from page_tours import Checklist, ChecklistItem, Tour, TourStep

WELCOME_TOUR = Tour(
    name="shop.welcome",
    autoplay=False,
    steps=[
        TourStep(title="Welcome", description="A quick look around."),
        TourStep(title="Your basket", description="Items wait here.", element="#basket"),
    ],
)

ONBOARDING = Checklist(
    name="shop.onboarding",
    title="Get started",
    items=[
        ChecklistItem(id="welcome", title="Take the welcome tour", tour=WELCOME_TOUR),
        ChecklistItem(id="orders", title="Open your orders", href="/orders/"),
        ChecklistItem(id="first-order", title="Place your first order"),
        ChecklistItem(
            id="guide",
            title="Read the guide",
            href="https://example.com/guide",
            allowManualComplete=True,
        ),
    ],
)
```

Put the checklist in the context of the pages that carry it. A context processor puts it on
every page, so a base template can hold `{{ checklist }}` once, at the end of `<body>`:

```python
def onboarding(request):
    return {"checklist": ONBOARDING}
```

Register the processor in the `context_processors` of your `TEMPLATES` setting, and place
`{{ checklist }}` in the base template:

```django
    ...
    {{ checklist }}
  </body>
```

`{{ checklist }}` outputs a `<script id="page-tours-checklist" type="application/json">`
element, which the package's script reads and shows. It draws nothing where it stands. It needs
no tag library: `Checklist` renders itself, and Django does not escape it. As for a tour:

- **Declare the checklist at module level,** so the system checks know its name.
- **`{{ checklist }}` with no checklist in the context renders nothing,** so a template shared
  by pages with and without one can hold it.
- **A function-based view** passes the checklist in the context it renders with.
- **A page without a checklist is unaffected.** Nothing shows, and nothing is stored.
- **A page can carry a checklist, a tour and hints.** They play side by side. See
  [A checklist beside a tour and hints](#a-checklist-beside-a-tour-and-hints).

## Name the checklist

Every checklist has a name, given where you declare it. A browser remembers what a visitor ticked
by the name and the version, and a project changes a reusable app's checklist by it. Choose a name
that stays put, and in a reusable app start it with the app label, as for a tour.

**Checklists, tours and hints share one namespace of names.** A name belongs to one
declaration, whichever kind it is. Django's `check` command warns with `page_tours.W005` when two
different declarations are given one name. Two checklists that differ only in `completed` are one
checklist.

A name that is not a string with something in it, or a version that is not a whole number of 1 or
more, raises `ImproperlyConfigured` when the checklist is declared. An empty list of items is
allowed: the page renders an empty checklist.

## Set the options of the checklist

`Checklist`, `ChecklistItem` and `Offset` take Driver.js's options as fields, named as Driver.js
names them. See the [Driver.js checklists reference](https://driverjs.com/docs/checklists) for
what each does. The package does not check their values: what you write is what Driver.js
receives. A field of an item that you leave out is not sent, and the value set on the checklist
applies, or else Driver.js's own default.

### Options of the checklist

| Field | Default | What it does |
|---|---|---|
| `name` | required | What the checklist is known by. Driver.js receives it as `id`. |
| `items` | required | The items, in order. |
| `version` | `1` | See [Show a changed checklist again](#show-a-changed-checklist-again). |
| `title` | "Get started", in the active language | The heading of the checklist. |
| `description` | none | The text under the heading. |
| `launcherText` | none | The text of the launcher. |
| `completeTitle` | none | The heading once every item is done. |
| `completeDescription` | none | The text once every item is done. |
| `completeLauncherText` | none | The text of the launcher once every item is done. |
| `progressText` | "{{done}} of {{total}}", in the active language | The progress in the panel. |
| `launcherProgressText` | `"{{done}}/{{total}}"` | The progress on the launcher. |
| `position` | `"bottom-right"` | Which corner of the window the checklist sits in: a `Position`, one of `"bottom-right"`, `"bottom-left"`, `"top-right"` or `"top-left"`. |
| `launcher` | `True` | Whether a launcher shows while the panel is closed. |
| `offset` | none | An `Offset`: how far the checklist sits from that corner. |
| `className` | `""` | A class added to the checklist. |
| `allowManualComplete` | `False` | Whether the visitor can tick any item. |
| `completed` | `()` | The ids of the items the app reports done. |

In the progress text, `{{done}}` and `{{total}}` stand for the counts.

### Options of an item

| Field | Default | What it does |
|---|---|---|
| `id` | required | What the app reports the item done under, and what a browser remembers it was ticked under. |
| `title` | required | The heading of the item. |
| `description` | none | The body of the item. |
| `tour` | none | A `Tour` that starts when the item is chosen. |
| `href` | none | The address the item opens when it is chosen. |
| `allowManualComplete` | the checklist's | Whether the visitor can tick this item. |

### Options of an offset

| Field | Default | What it does |
|---|---|---|
| `x` | Driver.js's | The distance from the side of the window, in pixels. |
| `y` | Driver.js's | The distance from the top or bottom of the window, in pixels. |

Titles, descriptions and text are passed to Driver.js as they are, and it writes them into the
page as HTML. Never build one from a visitor's input.

### Options that are not available

Driver.js options whose value is a JavaScript function cannot be written in Python, so the
classes leave them out: `completeWhen` and `action` on an item, and `onProgress`,
`onItemComplete`, `onComplete` and `onEvent` on a checklist. The package uses `onProgress` itself,
to keep what a visitor ticked.

Driver.js's build also has words of its own: the label of the close control ("Close checklist"),
the "Mark … as done" control of an item and the "(done)" it adds to a done item. The package
cannot translate them, so they read the same in every language.

## The three kinds of item

An item does one of three things when a visitor chooses it. Every item can also be ticked by the
app.

- **An item with a `tour`** starts the tour. The tour is an ordinary `Tour`, declared as on a page
  of its own. Its name, its version and `PAGE_TOURS_OVERRIDES` apply to it, it plays with the same
  controls, and it counts as seen once it has played. The item is ticked when the tour ends.
- **An item with an `href`** opens the address. It can be a page of your site or another site.
- **An item with neither** only reports. It is ticked by the app, or by the visitor when it takes
  `allowManualComplete`.

Setting `allowManualComplete=True` on the checklist lets the visitor tick every item. Setting it
on an item lets the visitor tick that item alone.

## Report items done from the app

What the app knows is done is reported when the page is built. Replace the checklist with a copy
that has the ids in `completed`, with `dataclasses.replace`. In a context processor:

```python
from dataclasses import replace


def onboarding(request):
    done = ("first-order",) if request.user.orders.exists() else ()
    return {"checklist": replace(ONBOARDING, completed=done)}
```

A view does the same in its context. The copy keeps the name of the original, and a checklist that
differs only in `completed` is not a second declaration.

The page shows the items the app reports as ticked. An item the app stops reporting is no longer
ticked, unless the visitor ticked it in the browser.

## Ticks kept in the browser

What a visitor ticks is kept in their browser, under the checklist's name and version, so it is
still ticked on their next visit. Nothing is stored on the server, and no cookie is set. What the
app reports is never stored by the browser: it is shown again from the page each time. A browser
that blocks storage shows only what the app reports, and the page raises no error.

### Show a changed checklist again

Editing a checklist does not clear what visitors ticked. When the checklist has changed enough
that they should start again, raise the version:

```python
ONBOARDING = Checklist(name="shop.onboarding", items=[...], version=2)
```

A browser that ticked items at any other version shows none of them ticked, once. Leave the
version alone for a fixed typo.

## Open and close the checklist from a control

With `launcher=False` the checklist shows no launcher when its panel is closed. Mark an element
of your own with `data-page-checklist-toggle` to make it open the panel and close it again.
Write it `hidden`:

```html
<button type="button" data-page-checklist-toggle hidden>Checklist</button>
```

The package's script removes `hidden` on a page with a checklist. On a page without one, and with
JavaScript off, it stays hidden, so the control can sit in a template shared by every page. Place
it more than once and each one opens and closes the checklist.

## A checklist beside a tour and hints

A page can render `{{ checklist }}`, `{{ tour }}` and `{{ hints }}`, and each plays. The checklist
is on the page before a tour step can point at its launcher. An item's tour is a separate tour
from the page's own: starting it plays it in the usual way, and it is recorded as seen under its
own name.

## Style the checklist

A checklist reuses the parts of a tour step, and adds two of its own:

| Part | Documented name | What it is on a checklist |
|---|---|---|
| `box` | `page-tour-box` | The panel. |
| `title` | `page-tour-title` | The heading of the checklist. |
| `text` | `page-tour-text` | The text under the heading. |
| `progress` | `page-tour-progress` | The progress in the panel. |
| `close` | `page-tour-close` | The control that closes the panel. |
| `launcher` | `page-tour-launcher` | The launcher shown while the panel is closed. |
| `item` | `page-tour-item` | Each item. |

Classes from `PAGE_TOURS_CLASSES` and from an app's `page_tour_classes` apply to a checklist's
parts as to those of a tour. See [Styling tours](styling-tours.md#style-a-checklist).

## Change the checklist of a reusable app

An app ships a checklist the same way a project does. A project replaces it or turns it off with
`PAGE_TOURS_OVERRIDES`, by name, as it does a tour: the value is the dotted path of a `Checklist`
to play in its place, or `None`. The replacement must be a `Checklist`, and a tour in its place
raises `ImproperlyConfigured`.

A replacement plays with the `completed` it was declared with. What the app reports for the
original does not carry over. A project that wants the app's report on its replacement sets
`completed` on the replacement in its own context processor.

A project can also change the tour of an item wherever it plays. An override of the tour's name
applies to the item's tour as it does to a tour on a page of its own, and an item whose tour is
turned off is left out of the checklist. See
[Tours from reusable apps](tours-from-reusable-apps.md#change-a-checklist-or-an-items-tour).

## See it in the demo project

The demo project carries an onboarding checklist on every page. It has four items: a welcome
tour, a link to the hints page, borrowing a book on the library's book page, which the app
reports done, and Driver.js's checklist guide, which the visitor ticks.
