# Tasks: Hints on a page

**Input**: [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md)

Every behaviour task is test-first. Tests follow `docs/contributing/standards/testing.md`: no
assertions on wording or layout, one behaviour per test. Browser behaviour is tested in a real
browser; what a test client can see is tested on the rendered HTML. No leading-underscore names,
lines of 88 characters at most, no compatibility aliases.

## Format: `[ID] [Story] Description`

## Phase 1: User Story 1 — A developer puts hints on a page (P1)

**Goal**: a developer declares hints in Python and renders them with `{{ hints }}`; `Tour` and
`TourStep` sit on the same shared bases, behaving as before.

**Independent test**: declare hints with three hints on a demo page, render it, and confirm three
beacons appear on their elements; set an option on the hints and override it on one hint, and
confirm that hint alone differs.

### Group 1 — the shared bases, with `Tour` and `TourStep` moved onto them

- [ ] T001 [US1] `page_tours/driver.py`: `driver_value`, `DriverObject`, `PopoverContent`,
  `Side`, `Alignment`, as plan.md "the shared bases". Tests in `tests/test_driver.py`: a `None`
  and a package field are left out, a nested field goes into its inner object, a lazy string
  renders in the active language, a nested object and a list of them are converted.
- [ ] T002 [US1] `Declaration`, `declared`, `forget`, `resolve_override` (with the class it must
  be), `declaration_overrides`, `declarations`, as plan.md. Tests in `tests/test_driver.py`:
  refusals of a name and a version naming the class, the registry and its weak references, the
  payload element `page-tours-<kind>` and its keys, an override's replacement rendered under the
  original's name and version, turned off, and refused when of another class (FR-008, FR-010).
- [ ] T003 [US1] `TourStep` on `PopoverContent` and `Tour` on `Declaration`, as plan.md
  "`page_tours/tours.py`". Remove `PACKAGE_FIELDS`, `STEP_LEVEL_FIELDS`, `as_driver_steps`,
  `_declared`, `_forget`, `resolve_override`, `tour_overrides`, `declared_tours` and the payload
  code. `apps.py` and `checks.py` call `declaration_overrides` and `declarations`. Move the tests in
  `tests/test_tours.py`, `tests/test_checks.py`, `tests/test_apps.py` and `tests/test_demo.py` to
  the new payload (`page-tours-tour`, `config.steps`) and functions without changing what they
  assert about a tour (FR-021).
- [ ] T004 [US1] `page-tours.js`: `memory`, `addClasses(parts, …)`, `popoverParts`, `playTour`
  reading `page-tours-tour` and `config`, and `play()` playing each kind in its own `try`, as
  plan.md. Tests in `tests/test_static/test_page_tours_js.py`: the existing tour suites green on
  the new payload; a seen record of the old shape (`"1"`) reads as not seen; storage blocked still
  plays the tour.
- [ ] T005 [US1] `Button` documented on `docs/developer/tours.md` with the values `showButtons`
  takes, and the payload element renamed there (the verify docs step).

### Group 2 — `Hints`, `Hint`, `Beacon` and the checks

- [ ] T006 [US1] `page_tours/hints.py` and the exports in `page_tours/__init__.py`, as plan.md.
  Tests in `tests/test_hints.py` on the rendered payload: scenarios 1, 2 (defaults, and the button
  text in the active language with a German catalogue entry in `tests/locale/de`), 3, 4, 5, 6, 7,
  8 (the hint's `id` is in its payload when set, absent when not), 9 (version 1 by default) and 12
  (replaced, turned off, refused for a `Tour` as replacement) (FR-001 to FR-008, FR-010).
- [ ] T007 [US1] W005 across kinds and for hints, W002 for a name only hints carry, as plan.md
  "`page_tours/checks.py`". Tests in `tests/test_checks.py`: two sets of hints with different
  hints under one name warn, the same hints do not, a tour and hints under one name warn, a tour
  at two versions does not (scenario 13, FR-009).
- [ ] T008 [US1] Message catalogue: `makemessages` for the new and changed strings in
  `page_tours/locale/en/LC_MESSAGES/django.po`, as the repo's other features did.

### Group 3 — hints in the browser

- [ ] T009 [US1] `playHints` (show, beacon classes, popover part classes, `onDismiss` into memory)
  and the restore control's visibility, `hints.css` imported by `page-tours.css`, and
  `hints.iife.js` in the test base templates, as plan.md. Test views and routes in
  `tests/views.py` and `tests/urls.py`. Tests in `tests/test_static/test_page_tours_js.py`:
  scenarios 1 (a beacon on each element), 4 (one hint's own beacon side and button text differ,
  the others do not), 10 (restore control shown with hints, hidden without hints and with
  JavaScript off), 11 (hints and a tour on one page, a step pointing at a beacon) and 15 (a hint
  whose element is missing shows no beacon, the others do).

### Group 4 — demo and documentation

- [ ] T010 [US1] Demo: `demo/hints.py`, `REPORT_TOUR` in `demo/tours.py`, `HintsView`, the route,
  `demo/templates/demo/hints.html`, `hints.iife.js` in `demo/templates/base.html`, the nav link
  and the overview paragraph, as plan.md "Demo project". Tests in `tests/test_demo.py`: the hints
  page renders the hints payload and the tour payload (FR-022).
- [ ] T011 [US1] Documentation, as plan.md "Documentation": `docs/developer/hints.md` in the
  guides toctree, installation, styling, reusable apps, `CONTEXT.md`, `CHANGELOG.md`, README. The
  docs build passes with `-W` (FR-007, FR-022).

## Phase 2: User Story 2 — A visitor reads a page's hints and dismisses them (P1)

**Goal**: beacons open in any order over a usable page, a dismissal lasts in that browser, the
restore control brings them back, and nothing breaks the page.

**Independent test**: open the demo hints page in a fresh browser, open two hints in reverse
order while clicking a button on the page, dismiss one, reload and confirm only that beacon is
gone; use the restore control and confirm it is back.

### Group 5 — reading, dismissing and restoring

- [ ] T012 [US2] Tests in `tests/test_static/test_page_tours_js.py`, and any fix they show in
  `page-tours.js`: scenarios 1 (two hints opened in reverse order), 2 (a page button takes a click
  with a hint open; it does not with `overlay=True`), 3 (dismissed hint gone after reload, others
  shown), 4 (the same hints on another address stay dismissed), 5 (a fresh browser context shows
  every beacon), 6 (restore brings every beacon back without reloading), and a raised version
  shows dismissed hints again (FR-011, FR-012, FR-013, FR-014).
- [ ] T013 [US2] Tests, and any fix they show: scenarios 7 (no beacon visible while a tour plays,
  back when it ends), 8 (keyboard alone reaches each beacon in declared order, opens it, presses
  its button, closes the popover), 9 (no pulse animation under reduced motion), 10 (storage
  blocked: a dismissal lasts the page view, no page error), 11 (JavaScript off and the hints
  script missing: no beacon, no page error) (FR-015 to FR-018).

## Phase 3: User Story 3 — A developer gives hints their site's look (P2)

**Goal**: a hint's popover carries the step's part classes, and the beacon is a configurable part.

**Independent test**: configure classes for box, title, text and beacon in `PAGE_TOURS_CLASSES`,
open a hint, and confirm the popover's parts and the beacon carry them.

### Group 6 — part classes on hints

- [ ] T014 [US3] `"beacon"` in `TourParts.parts`. Tests in `tests/test_parts.py` (the beacon's
  documented name and configured classes, from the setting and from an installed app) and
  `tests/test_checks.py` (W003/W004 for the beacon part) (FR-019, FR-020).
- [ ] T015 [US3] Tests in `tests/test_static/test_page_tours_js.py`: scenario 1 (a hint's box,
  title, text and button carry their part's name and classes), 2 (every beacon carries the beacon
  part's name and classes ahead of the hint's own class, and a hint with no class keeps the hints'
  beacon class) and 3 (an installed app's beacon classes apply when the setting has none). The
  styling page documents the beacon part (FR-019, SC-006).
