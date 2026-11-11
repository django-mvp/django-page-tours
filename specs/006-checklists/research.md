# Research — FS-006 A checklist

## Assumptions checked

Run before the specification was written. `main` has no checklist and still ships Driver.js
1.10.2, so the surfaces the specification hands something new to were read from Driver.js
1.11.0's checklist build as vendored on the prototype branch
(`page_tours/static/page_tours/vendor/driver.js-1.11.0/checklist.iife.js`).

- **The checklist build takes the completed items as a plain option.** It seeds its done set from
  `completed` and reports every change through `onProgress` with the full list. Holds, so the app's
  report (FR-005) and the browser's ticks (FR-008) can both be handed to it as one list.
- **It keeps nothing between page loads.** The build never touches `localStorage`. Holds, so the
  package keeps the ticks itself (FR-008), through the shared browser memory FS-005 builds.
- **An item's tour may be a Driver.js instance.** The build drives an item's `tour` as given when
  it is already a driver, and calls the instance's own `onDestroyed` before deciding the item from
  how the tour ended. Holds, so a tour built by the package's shared tour builder keeps its
  element lookup, part classes and seen record when a checklist starts it (FR-003, FR-009), as
  long as the tour's cleanup is in `onDestroyed` (issue #46).
- **A link item is ticked when followed.** An item with an `href` and no tour is an anchor, and
  the build ticks it on activation. Holds (FR-007).
- **Per-item and checklist-wide manual ticking.** `allowManualComplete` is read on the item first,
  then on the checklist. Holds (US1 scenario 5).
- **Opening and closing from the page.** The instance exposes `toggle`, and `launcher` can be
  turned off. Holds (FR-010).
- **The prototype's screens.** The checklist on every page of the demo and the book page's
  borrow action that ticks an item from the app are served from the prototype branch. Both pages
  return 200 and carry the checklist's payload element. Holds.

Not checked here, because they do not exist on `main` yet: the shared bases, browser memory and
entry point FS-005 builds, and the `Tour` fields of pull request #43. The build checks them on the
main it starts from.

## The base this is built on

`main` still lacks pull requests #43, #54 and #47 (FS-005). The build starts from `006-checklists`
with `origin/005-hints` merged in, which carries all three. Read there:

- `page_tours/driver.py`: `driver_value`, `DriverObject` (`package_fields`, `nested`),
  `PopoverContent`, `Declaration` (`name`, `version`, `kind`, `content_field`, `payload()`,
  `__html__` with the `PAGE_TOURS_OVERRIDES` lookup written inline), `resolve_override(name,
  value, cls)`, `declaration_overrides()`, `declarations()`. Every declaration is keyword-only.
- `page_tours/tours.py`: `Tour(Declaration)` with `kind = "tour"`, `content_field = "steps"`,
  `autoplay` as a package field, and `payload()` adding `autoplay`.
- `page_tours/static/page_tours/page-tours.js`: `visibleElement`, `memory(kind, payload)`,
  `addClasses`, `popoverParts(parts)`, `playTour(payload, driver)`, `playHints(payload,
  hintsDriver)` and `play()`, which plays each kind found as `page-tours-<kind>` in its own `try`.
  `playTour` holds everything a tour needs in one closure: the step mapping, `showable`, overlay
  naming, the error guard, focus restored, cleanup in `onDestroyed`, the seen record, the replay
  controls and autoplay.
- `page_tours/parts.py`: `TourParts.parts` has ten parts, the last `beacon`.
- `page_tours/checks.py`: W002 and W005 read `declarations()`; W005 groups by
  `(type, getattr(item, item.content_field))`.
- `driver.js-1.11.0/checklist.iife.js` and `checklist.css` are vendored. Neither is loaded yet:
  `page-tours.css` imports `driver.css` and `hints.css` only, and the templates load
  `driver.js.iife.js` and `hints.iife.js`.

The suite is green on this base: 485 tests.

## Planning notes, answered

Each entry of `planning-notes.md`, under its own words.

- **The prototype.** Adopted as the agreed design: `Checklist`, `ChecklistItem` and `Offset` with
  the prototype's fields and defaults, the context processor in the demo, and the book page's
  borrow action. Its code is rebuilt test-first; nothing is merged or cherry-picked from the
  branch.
- **The design rule every class follows.** Adopted. Every field is named as Driver.js names it,
  `Checklist` defaults each field to Driver.js's own default (`None` where Driver.js falls back to
  another option or to nothing), `ChecklistItem` and `Offset` default every optional field to
  `None`, nothing is checked beyond the name and version `Declaration` already checks, and text is
  passed as it is.
- **Reused: a base class, `DriverObject`.** Adopted. `Offset` and `ChecklistItem` are declared on
  it. `ChecklistItem.tour` is a package field, because what Driver.js receives for it is the tour's
  payload, built by `Checklist`, not the tour's own fields.
- **Reused: the base class for what a page renders.** Adopted, under FS-005's name, `Declaration`.
  `Checklist(Declaration)` with `kind = "checklist"` and `content_field = "items"`. The override
  lookup that `Declaration.__html__` writes inline is moved into one method, `playing()`, so the
  checklist can look up its items' tours the same way (D10).
- **Reused: rendering element id per kind.** Adopted: `page-tours-checklist`, with no new code.
- **Reused: one function in the script for what the browser remembers.** Adopted:
  `memory("ticked", payload)` keeps the ticks. An item's tour writes the tour's own seen record
  through the shared tour builder, so it is the same entry the page's own tour reads.
- **Reused: one function in the script for part classes on a popover.** Adopted: the shared tour
  builder gives every step of an item's tour `popoverParts(payload.parts)`, as the page's tour
  does today.
- **Built here: one function in the script that builds a Driver.js tour.** Adopted:
  `buildTour(payload, driver)`, cut out of FS-005's `playTour`. It returns the Driver.js instance,
  whose `drive` runs the package's start (nothing showable means no start, focus kept, error
  guard, overlay naming, seen record). `playTour` keeps only the replay controls and autoplay, and
  the checklist hands the instance to Driver.js as an item's `tour` (D15).
- **Reused: one entry point that plays every kind found on the page.** Adopted: `play()` gains
  `["checklist", playChecklist, …]` between hints and the tour, so a tour step can point at the
  checklist's launcher.
- **Also: an item's tour looked up in `PAGE_TOURS_OVERRIDES`.** Adopted through `playing()` (D10).
- **Also: the system check compares something meaningful.** Adopted with no new code: W005 already
  compares each kind's `content_field`, which for a checklist is its items. A checklist set per
  request with another `completed` is the same checklist.
- **Also: a tour's cleanup in `onDestroyed`.** Holds on the base: `playTour` already ends in
  `onDestroyed`, and `buildTour` keeps it. Driver.js's checklist calls the instance's own
  `onDestroyed` and then ticks the item when the tour ended as `done`.

## What the checklist build does, read from the vendored file

- `driverChecklist.checklist(config)` returns an instance with `show`, `hide`, `open`, `close`,
  `toggle`, `complete`, `uncomplete`, `reset`, `refresh` and `getProgress`.
- It reads the global `driver.js` when its own script runs, so `checklist.iife.js` loads after
  `driver.js.iife.js`.
- `show()` builds the whole widget once: a root `.driver-checklist` with the position and
  `className`, a `.driver-checklist-panel` (a dialog), its `.driver-checklist-title`,
  `.driver-checklist-description`, `.driver-checklist-progress`, `.driver-checklist-close-btn`,
  one `li.driver-checklist-item` per item, and the `.driver-checklist-launcher` unless `launcher`
  is `false`. Later changes set text inside those elements and toggle classes on them, so classes
  added once after `show()` stay.
- An item with a `tour` that is already a driver instance is driven as it is: the build wraps the
  instance's `onDestroyed` through `getConfig`/`setConfig`, calls the instance's own `onDestroyed`
  first, ticks the item only when the reason is `done`, then reopens the panel.
- A link item is an anchor; activating it ticks the item and the browser follows the link.
- `onProgress({completed, done, total})` is called at every tick and untick, with every id ticked.
- Its defaults: `title` "Get started", `progressText` "{{done}} of {{total}}",
  `launcherProgressText` "{{done}}/{{total}}", `position` "bottom-right", `launcher` on,
  `allowManualComplete` off. `description`, `launcherText`, `completeTitle`,
  `completeDescription`, `completeLauncherText` and `offset` fall back to another option or to
  nothing when absent.
- The words the build writes itself ("Close checklist", "Mark … as done", "(done)") are not
  options and cannot be translated by the package.

## What already exists

One line per new piece the plan writes, at the first place on `kit/checklists/existing-first.md`'s
list where the search stopped.

- `Checklist`, `ChecklistItem`, `Offset`: new code, on `DriverObject` and `Declaration` (this repo).
- The checklist's payload element, overrides, record of names and refusals: this repo,
  `Declaration`.
- An item's tour looked up in `PAGE_TOURS_OVERRIDES`: this repo, the lookup in
  `Declaration.__html__`, moved into `Declaration.playing()`.
- The two-names check for checklists: this repo, W005, with no new code.
- The `launcher` and `item` parts: this repo, `TourParts.parts`, two entries.
- The default labels in the visitor's language: Django, `pgettext_lazy`.
- Drawing the checklist, its progress, opening an item's tour, ticking a link, manual ticks,
  keyboard use: Driver.js 1.11.0's checklist build, vendored.
- What the browser remembers: this repo, `memory()`.
- Building a tour in the browser: this repo, `playTour`, cut into `buildTour`.
- Part classes on a tour step's popover: this repo, `popoverParts()`.
- Part classes on the checklist: new code, a few lines in `playChecklist` on `addClasses()`.
- The toggle control: new code, the pattern of the replay and restore controls.
- The checklist's look: Driver.js's `checklist.css`, imported into the `page-tours` layer.
- The demo's borrow action: Django, a `require_POST` view and the session.
