# Hints and checklists: the hand-over

This branch is a prototype. It is a reference for the rebuild and is never merged. The record of
the prototype, with the owner's decisions, is issue 45 on this repository. It starts from the branch
of pull request 43, which made `Tour` and `TourStep` mirror Driver.js's configuration.

## The design rule every feature follows

Every Python class mirrors a Driver.js object:

- Each option that takes a plain value is a field, named exactly as Driver.js names it (camelCase).
- Top-level objects default each field to Driver.js's own default. Objects that override a parent
  (a step, a hint, a beacon) default every field to `None`, and a `None` is left out of the
  payload, so the parent's value applies.
- Nothing is checked for the developer beyond what the package itself depends on. A value that
  cannot be serialised fails in `json_script`, and that is enough.
- Options that take a JavaScript function are not available, and the docs say so.
- Text is passed to Driver.js as it is. Default labels are lazy translated strings.

## Build order

| Order | Item | Lane | Who can newly do what |
|---|---|---|---|
| 1 | Ship Driver.js 1.11.0 | resolve | Nobody new. Replaces the vendored 1.10.2. |
| 2 | Hints on a page | feature-request | A developer puts hints on a page: beacons a visitor opens in any order, while the page stays usable, and dismisses for good in that browser. |
| 3 | A checklist | feature-request | A developer adds a "get started" checklist whose items start a tour, follow a link, are ticked by the app, or are ticked by the visitor. |

The checklist depends on hints only for the shared pieces hints builds. Hints depends on item 1.

### 1. Ship Driver.js 1.11.0 (resolve)

- Vendor `driver.js.iife.js`, `driver.css`, `hints.iife.js`, `hints.css`, `checklist.iife.js` and
  `checklist.css` from the npm package `driver.js@1.11.0` under `vendor/driver.js-1.11.0/`, with
  its licence. Remove 1.10.2. Update every path in docs, the demo, tests and installation docs.
- `Tour` and `TourStep`: `advanceOnClick` becomes `advanceOn` (`False`, an event name or a tuple
  of names), as 1.11.0 deprecates the old option. `overlayClickBehavior` takes `"none"`.
- Recheck the workarounds `page-tours.js` carries for 1.10.2 (focus restored after a step's
  popover is removed, closing while a step is still opening, the error handler) and drop any
  1.11.0 no longer needs.
- The script's tour cleanup must run in `onDestroyed`. With `onDestroyStarted` set, 1.11.0
  reports a finished tour as ended by the page, which the checklist feature depends on.
- Changelog entry, marked breaking for `advanceOnClick`.

### 2. Hints on a page (feature)

Screens: the hints page of the demo, `/hints/` (`demo/templates/demo/hints.html`,
`demo/guides.py` `REPORT_HINTS`, `REPORT_TOUR`).

- `Hints(name=…, hints=[Hint(…)], beacon=Beacon(…), buttonText=…, popoverClass=…,
  popoverOffset=…, overlay=…, overlayColor=…, overlayOpacity=…)`, rendered with `{{ hints }}`.
  `page_tours/hints.py`.
- `Hint(element=…, id=…, title=…, description=…, side=…, align=…, popoverClass=…, beacon=…,
  showButton=…, buttonText=…)`. The popover fields sit flat on the hint, as on a step, and go into
  `popover` in the payload. `id` defaults to the element.
- `Beacon(side, align, animate, className, offsetX, offsetY)` is its own class, because its
  `side` and `align` mean the edge of the element, not the popover.
- `buttonText` defaults to a lazy translated "Got it" (msgctxt `page hint control`).
- A dismissed hint is remembered in the browser under the hints' name and version, and a raised
  version shows every hint again. A control carrying `data-page-hints-restore` brings dismissed
  hints back (written `hidden`, shown by the script).
- A tour on the same page hides the beacons while it plays (Driver.js does this).
- A hint's popover carries the part classes a tour step's popover carries. The beacon carries a
  new part, `beacon`, before its own `className`.
- `PAGE_TOURS_OVERRIDES` and the name checks cover hints.

### 3. A checklist (feature)

Screens: the checklist on every demo page, through the context processor
`demo.guides.onboarding`; the book page `/library/book/` ticks an item from the app.

- `Checklist(name=…, items=[ChecklistItem(…)], title, description, launcherText, completeTitle,
  completeDescription, completeLauncherText, progressText, launcherProgressText, position,
  launcher, offset=Offset(x, y), className, allowManualComplete, completed)`, rendered with
  `{{ checklist }}`. `name` is Driver.js's `id`. `page_tours/checklists.py`.
- `ChecklistItem(id, title, description, tour, href, allowManualComplete)`. An item's `tour` is
  an ordinary `Tour`. Finishing it from the checklist ticks the item and counts the tour as seen.
- `completed` stands in for Driver.js's `completeWhen`: a view or context processor sets it per
  request with `dataclasses.replace(CHECKLIST, completed=…)` from what the app knows.
- Ticks are remembered in the browser under the checklist's name and version, merged with
  `completed`.
- A control carrying `data-page-checklist-toggle` opens and closes a checklist declared with
  `launcher=False`.
- `title` and `progressText` default to lazy translated strings (msgctxt `page checklist`).
- Part classes: the panel, title, description, progress and close control reuse `box`, `title`,
  `text`, `progress` and `close`. New parts: `launcher`, `item`.

## The shared pieces

Each is built by the first feature that needs it. The sibling specification that reuses it is the
second use Article III asks for.

| Piece | Where the prototype has it | Becomes | Built by | Reused by |
|---|---|---|---|---|
| A dataclass that turns its fields into the Driver.js object: `None` left out, lazy strings rendered, nested objects and lists converted, fields routed into an inner object such as `popover` | `page_tours/driver.py:37` `driver_value`, `:60` `DriverObject` | A base class, `DriverObject` | Hints | Checklist. `Tour` and `TourStep` move onto it in the hints feature, replacing `as_driver_steps` and the options comprehension in `__html__` |
| The popover fields a step and a hint share | `page_tours/driver.py:94` `PopoverContent`; used at `tours.py:37`, `hints.py:50` | A base class | Hints | — (step and hint) |
| What a page renders: name, version, record of declared names, `PAGE_TOURS_OVERRIDES`, `{{ … }}` rendering, payload with `kind` | `page_tours/driver.py:136` `Guide`, `:222` `resolve_override`, `:260`, `:270`; subclassed at `tours.py:87`, `hints.py:77`, `checklists.py:72` | A base class, `Guide`, and the module functions it needs | Hints | Checklist |
| Rendering element id per kind: `page-tours-<kind>` | `page_tours/driver.py:189` | Part of `Guide` | Hints | Checklist. Tours move from `page-tour-steps` |
| What the browser remembers: a list of ids under the guide's name, for its version | `page-tours.js:26` `memory` | One function in the script | Hints | Checklist, and the tour's seen record |
| Part classes on a popover, whatever shows it | `page-tours.js:65` `popoverParts` | One function in the script | Hints | Tours already, checklist item tours |
| Building a Driver.js tour from a tour's payload, with element lookup, part classes, overlay naming, cleanup and seen record | `page-tours.js:104` `buildTour`; used at `:199` and `:328` | One function in the script | Checklist | The page's own tour |
| One entry point that plays every kind found on the page | `page-tours.js:355` `play` | Part of the script | Hints | Checklist |

## Duplication to remove

- `tours.py:151` `tour_overrides` and `:160` `declared_tours` only forward to the `Guide`
  functions. The rebuild renames the callers (`apps.py`, `checks.py`) instead of keeping aliases.
- `page_tours/checks.py` W005 compares `repr(as_driver())` in the prototype as a quick hack. The
  rebuild compares something meaningful per kind (a tour's steps, the hints, the items).
- The error and messages still say "Tour" for every kind (`driver.py:222`).

## The data model

No database models. Every declaration is a frozen dataclass in Python and every record of what a
visitor did is in the browser's local storage.

| Class | Feature |
|---|---|
| `DriverObject`, `PopoverContent`, `Guide` | Hints |
| `Tour`, `TourStep` (moved onto the bases) | Hints |
| `Hints`, `Hint`, `Beacon` | Hints |
| `Checklist`, `ChecklistItem`, `Offset` | Checklist |

## Decisions

From the owner, in this session and on pull request 43:

- Fields are named exactly as Driver.js names them, camelCase, with no conversion.
- No defensive checks of option values, no `ImproperlyConfigured` for them.
- A step's and a hint's popover fields sit flat on the class.
- Step titles and descriptions are not escaped.
- "Identify opportunity for abstraction where possible" — the shared pieces above.

## Faked or skipped

| What | Which item does it properly |
|---|---|
| No tests, docs, changelog or specs; the existing suite fails on this branch | Each item |
| Storage format changed to a version and a list of ids, so a browser that saw a tour under the old format sees it once more | Hints (it introduces `memory`); the changelog says so |
| 1.10.2 workarounds not rechecked on 1.11.0 | Ship Driver.js 1.11.0 |
| W005 comparison | Hints |
| A checklist item's tour is not looked up in `PAGE_TOURS_OVERRIDES` | Checklist |
| Error messages say "Tour" for every kind | Hints |
| Function options (`completeWhen`, `action`, `onButtonClick`, event hooks) are not available, so a hint cannot start a tour from its button | Not built. Documented as a limit |

## What it replaces

- `vendor/driver.js-1.10.2/`.
- In `tours.py`: `_declared`, `_forget`, `resolve_override`, `tour_overrides`, `declared_tours`,
  `PACKAGE_FIELDS`, `STEP_LEVEL_FIELDS`, `as_driver_steps` and the payload code in `__html__`,
  all moved onto the shared bases.
- The tour payload element `page-tour-steps` becomes `page-tours-tour`, and its `options` key
  becomes `config` with the steps inside it.
- The local storage key `page-tours:seen:<name>` and its value format.
- Nothing in a database, so nothing to drop.
