# Tasks: A checklist

**Input**: [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md)

Every behaviour task is test-first. Tests follow `docs/contributing/standards/testing.md`: no
assertions on wording or layout, one behaviour per test. Browser behaviour is tested in a real
browser; what a test client can see is tested on the rendered HTML. No leading-underscore names,
lines of 88 characters at most, no compatibility aliases, Cotton components and never
`{% include %}` partials.

## Format: `[ID] [Story] Description`

## Phase 1: User Story 1 — A developer adds a checklist to a site's pages (P1)

**Goal**: a developer declares a checklist in Python and outputs it with `{{ checklist }}`; its
items start a tour built as a page's own tour is, follow a link, or are reported done by the app.

**Independent test**: declare a checklist with one item of each kind, put it in a page's context
and output it; open the page and see every item in order; report one item done from the view and
see it ticked; render the page with JavaScript off and see the page without a checklist.

### Group 1 — the declarations

- [ ] T001 [US1] `Declaration.playing()` in `page_tours/driver.py`, with `__html__` calling it,
  as plan.md "`Declaration.playing()`". Tests in `tests/test_driver.py`: the declaration at its
  own version when the setting does not name it, the replacement at the combined version, `None`
  when turned off. The existing override tests pass unchanged.
- [ ] T002 [US1] `page_tours/checklists.py` (`Position`, the labels, `Offset`, `ChecklistItem`,
  `Checklist` with `as_driver()` building the items) and the exports in `page_tours/__init__.py`,
  as plan.md. Tests in `tests/test_checklists.py` on the rendered payload: US1 scenarios 1 (the
  element `page-tours-checklist`, items in declared order), 2 (an item's tour carries the tour's
  payload: kind, id, version, parts, config), 3 (`href`), 4 (`completed` reaches Driver.js), 5
  (`allowManualComplete` on the checklist and on one item), 8 (each option set reaches Driver.js
  unchanged; the defaults; an `Offset`), 9 (the default `title` and `progressText` in German from
  a catalogue entry in `tests/locale/de`), 11 (the checklist replaced and turned off under its
  name) and 12 (an item's tour replaced plays the replacement at the combined version; turned off
  leaves its item out; a replaced checklist plays with its own `completed`, D17) (FR-001 to
  FR-005, FR-011, FR-013).
- [ ] T003 [US1] `"launcher"` and `"item"` in `TourParts.parts` and its docstring. Tests in
  `tests/test_parts.py` (both parts' documented names and configured classes). The existing test
  that pins the list of parts, `test_the_parts_are_the_nine_of_a_step_and_the_beacon_of_a_hint`,
  is updated to the new list and renamed to match (FR-012).
- [ ] T004 [US1] W002 and W005 messages and docstrings name the checklist, as plan.md
  "`page_tours/checks.py`". Tests in `tests/test_checks.py`: two checklists with different items
  under one name warn, two that differ only in `completed` do not, a name only a checklist carries
  satisfies W002 (scenario 13, FR-014).
- [ ] T005 [US1] Message catalogue: `makemessages` for the new and changed strings in
  `page_tours/locale/en/LC_MESSAGES/django.po`, as FS-005 did.

### Group 2 — the checklist in the browser

- [ ] T006 [US1] `buildTour(payload, driver)` cut out of `playTour`, and `playTour` on it, as
  plan.md "`page_tours/static/page_tours/page-tours.js`": the Driver.js instance is made on first
  use, after the showable check. No behaviour changes: every existing test in
  `tests/test_static/test_page_tours_js.py` passes unchanged, and none is edited.
- [ ] T007 [US1] `playChecklist` (configuration with `id`, the reported `completed`, item tours
  through `buildTour`; `show()`; part classes), its place in `play()` between hints and the tour,
  `checklist.css` imported by `page-tours.css`, and `checklist.iife.js` after `hints.iife.js` in
  the test base templates, as plan.md. Ticks are not stored yet: `onProgress` is T011. Test views
  and routes in `tests/views.py` and `tests/urls.py`, templates in `tests/templates/`. Tests in
  `tests/test_static/test_page_tours_js.py`: US1 scenarios 1 (every item shown, in order), 2 (an
  item's tour plays its steps with their part classes, skipping a step whose element is missing,
  and is recorded seen), 3 (a link item is followed), 4 (an item the view reports done is shown
  ticked), 5 (only the allowed items can be ticked by the visitor), 10 (the panel, title,
  description, progress and close control carry their part's name and classes; the launcher and
  each item carry theirs), 14 (JavaScript off, and the checklist script missing: no checklist, no
  page error) and 15 (a tour, hints and a checklist on one page each play). In
  `tests/test_static/test_page_tours_css.py`: `checklist.css` is imported into the layer
  (FR-003, FR-006, FR-007, FR-012, FR-015, FR-016).
- [ ] T008 [US1] The toggle control, as plan.md. Tests: US1 scenarios 6 (with `launcher=False`,
  the control opens the checklist and closes it again) and 7 (the control stays hidden on a page
  with no checklist and with JavaScript off) (FR-010).

### Group 3 — demo and documentation

- [ ] T009 [US1] Demo, as plan.md "Demo project": `WELCOME_TOUR`, `demo/checklists.py` with
  `ONBOARDING` and `onboarding`, the context processor setting, `base.html`, the borrow view,
  route and form, and the overview paragraph. Tests in `tests/test_demo.py`: every demo page
  renders the checklist payload, and after a borrow posted with
  `Client(enforce_csrf_checks=True)` and the page's token, the payload reports the borrow item
  done (FR-017).
- [ ] T010 [US1] Documentation, as plan.md "Documentation": `docs/developer/checklists.md` in the
  Guides toctree, installation, styling, reusable apps, `CONTEXT.md`, `CHANGELOG.md`, README. The
  docs build passes with `-W` (FR-017).

## Phase 2: User Story 2 — A visitor works through a site's checklist (P2)

**Goal**: the visitor's ticks last in their browser beside what the app reports, until the
version is raised, and the checklist stays usable and keyboard-operable.

**Independent test**: on a page with a checklist of one item of each kind, finish the item's
tour, follow the link, have the app report its item, tick the manual one; see the progress rise;
reload and see every tick kept; see the completed state.

### Group 4 — ticks kept in the browser

- [ ] T011 [US2] `onProgress` into `memory("ticked", …)`, storing the ticked ids less the
  reported ones, and the stored ticks shown after the reported ones, as plan.md and D12,
  test-first. Tests in `tests/test_static/test_page_tours_js.py`: US2 scenarios 1 (every item,
  which are done, done of total), 2 (finishing an item's tour ticks it; finishing the second item's tour before the first
  ticks only the second), 3 (closing it early does
  not), 4 (a tour started from the checklist does not autoplay as the page's own tour
  afterwards), 5 (a followed link is ticked), 6 (tick and untick follow), 7 (ticks kept on reload
  and on another page with the checklist), 8 (the app's report and the browser's ticks together),
  9 (a raised version forgets the browser's ticks and keeps the app's report) and 10 (the
  completed state), and the Edge Cases: an item's tour with nothing to show does not start and
  stays unticked, an item the app stops reporting is unticked unless the browser ticked it (also
  when the visitor ticked it before the app reported it and ticked another item while it did), a
  stored tick for a removed item does not count, a tick is kept when its item is reworded or
  moved, and blocked storage still works for the page view with no page error (FR-007 to
  FR-009).
- [ ] T012 [US2] Tests, and any fix they show: US2 scenarios 11 (with the checklist open, a
  button on the page beside it still takes a click, and closing it uncovers everything) and 12
  (keyboard alone opens the checklist, starts an item and closes it) (FR-015).

## Review fixes

- [x] T013 [US1] The duplicate-name check compares declarations of one name for equality, so a
  checklist whose item's tour sets a list option no longer stops `manage.py check`.
- [x] T014 [US1] The checklist guide says which module the checks see a checklist in and what a
  reported item stores; the hints and reusable-app pages and ADR 0009 name every kind they cover.
- [x] T015 [US1] Three checklist tests pin literal defaults or are removed, so each can fail.
