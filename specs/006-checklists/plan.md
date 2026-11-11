# Implementation Plan: A checklist

**Branch**: `006-checklists` | **Spec**: [spec.md](spec.md) | **Research**: [research.md](research.md)

## Summary

A developer declares a checklist as `Checklist(name=…, items=[ChecklistItem(…)], …)`, puts it in
the page's template context, often for every page through a context processor, and outputs it
with `{{ checklist }}`. It is a third kind of declaration on FS-005's `Declaration`, beside the
tour and the hints. Driver.js 1.11.0's checklist build, already vendored, draws it. In the
browser, the script that FS-005 wrote gains one function that builds a Driver.js tour from a
tour's payload, cut out of today's `playTour`. The page's own tour plays through it, and so does
the tour of a checklist item, so both find their elements, carry their part classes and are
remembered as seen in one way. The visitor's ticks are kept with the shared `memory()` function,
next to what the app reports for each request.

## Technical Context

- **Language**: Python 3.12+, Django 5.2, 6.0 and 6.1. JavaScript in the starter script, no build.
- **Dependencies**: none added. Driver.js 1.11.0's `checklist.iife.js` and `checklist.css` are
  vendored.
- **Storage**: none on the server. No models, no migrations. The browser's `localStorage`.
- **Testing**: pytest-django for Python and rendered HTML, pytest-playwright (Chromium) for
  browser behaviour, as the existing suites.
- **Base**: `006-checklists` with `origin/005-hints` merged in (pull requests #43, #54 and #47).

## Constitution Check

- **Article II (simplicity)**: one new module of three small classes, one method moved out of
  `Declaration.__html__`, one script function cut out of another. No new registry, setting or
  check.
- **Article III (anti-abstraction)**: the one new shared piece, `buildTour`, has two uses in this
  feature: the page's own tour and a checklist item's tour. `Declaration.playing()` has two: a
  declaration's own rendering and an item's tour.
- **Article V (escaping)**: the payload goes through `json_script`. Text inside it reaches
  Driver.js as it is, as a step's and a hint's does.
- **Article VI (documentation)**: a new guide page, and the installation, styling, reusable-app
  pages, README, CHANGELOG and `CONTEXT.md`, in this pull request.
- **Article VIII (translation)**: the checklist's default heading and progress text, and every new
  message, are lazy translated.
- **Article XI (compatibility)**: before 0.1.0. Nothing public is renamed. The changelog lists the
  checklist under Added.
- **Article XIII (a page never breaks)**: the checklist plays inside its own `try` in `play()`. A
  missing checklist script, blocked storage or a Driver.js error leaves the page as it would be
  without a checklist.

## Design

### `page_tours/driver.py` — `Declaration.playing()`

`Declaration.__html__` looks the declaration up in `PAGE_TOURS_OVERRIDES` inline. That lookup
moves, unchanged, into one method:

```python
def playing(self) -> tuple["Declaration", int] | None:
    """Return the declaration that plays under this one's name, and its version.

    The replacement the ``PAGE_TOURS_OVERRIDES`` setting names, at this version plus the
    replacement's less one; this declaration at its own version when the setting does not
    name it; ``None`` when the setting turns it off.
    """
```

`__html__` becomes: `playing()`; `""` when it is `None`; otherwise
`json_script(played.payload(self.name, version), f"page-tours-{self.kind}")`. Its docstring keeps
what it says about overrides and points at `playing()`. The existing override tests for tours and
hints pass unchanged. `playing()` gets its own tests in `tests/test_driver.py`.

### `page_tours/checklists.py` — `Offset`, `ChecklistItem`, `Checklist`

Every class keyword-only (`@dataclass(frozen=True, kw_only=True)`), as FS-005's.

```python
Position = Literal["bottom-right", "bottom-left", "top-right", "top-left"]

GET_STARTED_LABEL = pgettext_lazy("page checklist", "Get started")
CHECKLIST_PROGRESS_TEXT = pgettext_lazy("page checklist", "{{done}} of {{total}}")
LAUNCHER_PROGRESS_TEXT = "{{done}}/{{total}}"

class Offset(DriverObject):
    x: int | None = None
    y: int | None = None

class ChecklistItem(DriverObject):
    package_fields = frozenset({"tour"})
    id: str
    title: str | Promise
    description: str | Promise | None = None
    tour: Tour | None = None
    href: str | None = None
    allowManualComplete: bool | None = None

class Checklist(Declaration):
    kind = "checklist"
    content_field = "items"
    items: Sequence[ChecklistItem]
    title: str | Promise = GET_STARTED_LABEL
    description: str | Promise | None = None
    launcherText: str | Promise | None = None
    completeTitle: str | Promise | None = None
    completeDescription: str | Promise | None = None
    completeLauncherText: str | Promise | None = None
    progressText: str | Promise = CHECKLIST_PROGRESS_TEXT
    launcherProgressText: str | Promise = LAUNCHER_PROGRESS_TEXT
    position: Position = "bottom-right"
    launcher: bool = True
    offset: Offset | None = None
    className: str = ""
    allowManualComplete: bool = False
    completed: Sequence[str] = ()
```

- `Checklist.__post_init__` freezes `items` and `completed` to tuples, then calls
  `super().__post_init__()`. Nothing else is refused: an empty list of items renders an empty
  checklist, as hints declared with an empty list do (FS-005 T016).
- `Checklist.as_driver()` calls `super().as_driver()`, then rebuilds `items`: for each item, the
  item's own `as_driver()`; for an item with a tour, `item.tour.playing()`, the item left out when
  it is `None`, and otherwise `tour` set to `played.payload(item.tour.name, version)`. An item's
  tour therefore reaches the browser in exactly the shape the page's own tour does, under its own
  name and version, with its overrides applied (FR-003, FR-009, FR-013, D10, D11).
- The checklist's `name` is Driver.js's `id`. It stays a package field of `Declaration`, and the
  script sets `id` from the payload's `id`, as every kind's payload carries it.
- `completed` reaches Driver.js under its own name. It is what the app reports for this request:
  a view or context processor sets it with `dataclasses.replace(CHECKLIST, completed=…)` (FR-005,
  D3). A checklist made per request is recorded under its name by `Declaration` and collected with
  the request, as one built per request already is.
- No `ImproperlyConfigured` for an option value, no check that an item has a tour or a link, no
  check that item ids are unique (Driver.js warns in the console). The design rule.

`page_tours/__init__.py` exports `Checklist`, `ChecklistItem` and `Offset`.

### `page_tours/parts.py`

`TourParts.parts` gains `"launcher"` and `"item"` after `"beacon"`. Their documented names are
`page-tour-launcher` and `page-tour-item`. W003 and W004 cover them with no further code. The
class docstring names the checklist's parts (FR-012).

### `page_tours/checks.py`

No new check. W005 already groups every declaration under a name by `(type, content)`, and a
checklist's content is its items, so two checklists with different items under one name are
reported and two that differ only in `completed` are not (FR-014). The messages and docstrings of
W002 and W005 that name "a tour or hints" name the checklist too.

### `page_tours/static/page_tours/page-tours.js`

**`buildTour(payload, driver)`** — cut out of today's `playTour`, with no change in behaviour. It
holds the step mapping, `showable`, overlay naming and its watcher, `guarded`, the focus
restore, `finished`, `endTour` and the seen record, and returns one Driver.js instance, made
once, with the configuration `playTour` passes today (the tour's own options first, then
`steps`, `skipMissingElement`, `onPopoverRender` and `onDestroyed`). Its `drive` is replaced by
the package's start, so whoever starts the tour starts it the same way:

- nothing showable: nothing happens;
- otherwise focus is noted, the error listener and the overlay watcher are set, Driver.js's own
  `drive` runs, and `memory("seen", payload).set([payload.id])` records it;
- a Driver.js error ends the tour and cleans up, as `endTour` does today.

The instance also carries `isSeen()`, `memory("seen", payload).get().length > 0`.

**`playTour(payload, driver)`** keeps only what belongs to a page's own tour: `buildTour`, the
replay controls (destroy the instance when it is active, then `drive()`), shown as today, and
autoplay when the tour is not seen. Every existing tour test passes unchanged; that suite is what
proves the cut changed nothing.

**`playChecklist(payload, checklistDriver, tourDriver)`**, when `window.driverChecklist` is there:

- `ticked = memory("ticked", payload)`. `reported = payload.config.completed`.
- Driver.js's configuration is `payload.config` with `id: payload.id`, `completed` set to the
  reported ids followed by every stored id not among them, `items` with each tour item's `tour`
  replaced by `buildTour(item.tour, tourDriver)`, and `onProgress` storing
  `progress.completed` less the reported ids. The app's report is not stored, so an item it stops
  reporting is ticked only where the browser holds a tick of its own (FR-008, D12).
- `instance.show()`, then the part classes, once, on the widget the build made: `box` on
  `.driver-checklist-panel`, `title` on `.driver-checklist-title`, `text` on
  `.driver-checklist-description`, `progress` on `.driver-checklist-progress`, `close` on
  `.driver-checklist-close-btn`, `launcher` on `.driver-checklist-launcher`, `item` on each
  `.driver-checklist-item`, through `addClasses` (FR-012, D14).
- Each `[data-page-checklist-toggle]` control: on click, `instance.toggle()`; then
  `hidden = false` (FR-010, D16).

**`play()`**: the kinds become hints, checklist, tour, so the checklist's launcher is on the page
before a tour step can point at it. The checklist's driver is `window.driverChecklist.checklist`,
and `play()` hands the tour driver to every player after its own, so `playChecklist` can build
item tours. Each kind still plays in its own `try`.

### `page_tours/static/page_tours/page-tours.css`

Imports `checklist.css` into the `page-tours` layer after `hints.css`, and holds nothing else.

### Templates loading the scripts

`checklist.iife.js` is one more `<script … defer>` after `hints.iife.js`, in every test base
template that loads Driver.js, in `demo/templates/base.html` and on the installation page. It
must come after `driver.js.iife.js`, because it reads the global `driver.js` when it runs.

### Demo project

As the prototype's:

- `WELCOME_TOUR` in `demo/tours.py`, under `demo.welcome`, `autoplay=False`, three steps.
- `demo/checklists.py`: `ONBOARDING`, under `demo.onboarding`, with four items: the welcome
  tour, a link to the hints page, borrowing a book (done in the app) and Driver.js's checklist
  guide (an external link the visitor ticks). `onboarding(request)`, the context processor, puts
  `replace(ONBOARDING, completed=("borrow",) if request.session.get("borrowed") else ())` under
  `checklist`. Registered in `demo/settings.py`.
- `demo/templates/base.html`: `checklist.iife.js`, `{{ checklist }}` at the end of `body`, and
  room under `main` so the corner widget covers no content.
- `demo/library`: a `borrow` view (`require_POST`, sets `request.session["borrowed"]`, redirects
  to the book page), its route `library-borrow`, and the book page's borrow button in a form that
  posts to it, with a line saying the checklist ticked it.
- The overview page: one paragraph on the checklist.

### Documentation

- `docs/developer/checklists.md`, a new guide in the Guides toctree after hints: declaring a
  checklist and its items, the options, the three kinds of item, reporting items done from the
  app with `dataclasses.replace` in a view or context processor, ticks and the version, the
  toggle control and `launcher=False`, the checklist beside a tour and hints, its parts, overrides
  of a checklist and of an item's tour, and what is not available: `completeWhen`, an item's
  `action`, `onProgress`, `onItemComplete`, `onComplete`, `onEvent`, and the build's own words
  that cannot be translated.
- `installation.md`: the checklist script. `styling-tours.md`: the checklist's reused parts and
  its two new ones. `tours-from-reusable-apps.md`: a checklist by name, and an item's tour changed
  wherever it plays.
- `CONTEXT.md`: Checklist, Checklist item, Ticked, Toggle control; Declaration names the
  checklist.
- `CHANGELOG.md`: the checklist under Added; the two new parts.
- `README.md`: the scope includes checklists (D7).

### ADR

Decided at converge against the bar. The candidate is D15: one function builds a tour in the
browser wherever it is started, so a tour has one behaviour and one seen record. ADR 0008 already
covers the shared base of declarations, which this feature only extends.

## Tests

Mirroring the source tree (`docs/contributing/standards/testing.md`):

- `tests/test_driver.py`: `playing()` returns the declaration at its version, the replacement at
  the combined version, and `None` when turned off.
- `tests/test_checklists.py`: US1 scenarios 1 (items in order, payload element
  `page-tours-checklist`), 2 and 12 on the payload (an item's tour carries the tour's payload, an
  overridden tour its replacement at the combined version, a turned-off tour leaves its item out),
  3 (`href`), 4 (`completed` reaches Driver.js), 5 (`allowManualComplete` on the checklist and the
  item), 8 (every option set reaches Driver.js unchanged; defaults; `Offset`), 9 (the default
  heading and progress text in German from `tests/locale/de`) and 11 (the checklist replaced and
  turned off).
- `tests/test_checks.py`: W005 for two checklists with different items; none for two that differ
  in `completed` only; W002 for a name only a checklist carries.
- `tests/test_parts.py`: the `launcher` and `item` parts' names and classes.
- `tests/test_static/test_page_tours_js.py`: the existing tour suites, unchanged, over
  `buildTour`; US1 scenarios 1, 2, 3, 4, 5, 6, 7, 10, 14 and 15 and US2 scenarios 1 to 12 and the
  Edge Cases in a real browser.
- `tests/test_static/test_page_tours_css.py`: `checklist.css` imported into the layer, as the
  existing import tests do.
- `tests/test_demo.py`: every demo page renders the checklist payload; borrowing reports the
  borrow item done.

Test views, routes and templates for checklists go in `tests/views.py`, `tests/urls.py` and
`tests/templates/`, as the tour and hint ones do.
