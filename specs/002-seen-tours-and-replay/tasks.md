# Tasks: Seen tours and replay

**Input**: [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md)

Every behaviour task is test-first. Tests follow `docs/contributing/standards/testing.md`: no
assertions on wording or layout, elements found by id, role or attribute, one behaviour per test.
Browser behaviour is tested in a real browser; what a test client can see is tested on the
rendered HTML.

## Format: `[ID] [Story] Description`

## Phase 1: User Story 1 — A returning visitor is not shown a tour they have already seen (P1)

**Goal**: a tour plays by itself once per browser, and is seen per declaring view.

**Independent test**: open a page with a tour in a fresh browser and see it play; reload and see
it not play; open a page with a different tour and see it play.

### Group 1 — seen once per browser

- [ ] T001 [US1] Tour identity, as plan.md "Tour identity": `with_tour` sets and cleans up
  `request.page_tour_view`; `tour_id(context)` in `page_tours/tours.py`. Tests in
  `tests/test_tours.py` (`TestTourId`, and `TestWithTour` for the clean-up): a class-based view,
  a subclass inheriting the tour shares its parent's id, a subclass declaring its own tour has
  its own, a function-based view (FR-004).
- [ ] T002 [US1] The tag's payload object `{"id", "autoplay", "steps"}`, as plan.md "The tag's
  payload". `Tour` gains `autoplay: bool = True` here, used only to fill the payload. Update the
  FS-001 tag tests in `tests/test_templatetags/test_page_tours.py` that read the bare list so
  they read `steps` (they assert the same behaviour; the change is the payload's shape). New
  tests (`TestPageTourPayload`): the payload carries the page's id and `autoplay` true; the two
  URLs of one view carry the same id (FR-004); a page with no tour still carries nothing.
- [ ] T003 [US1] Seen in the starter script, as plan.md "The starter script", without the
  replay wiring: `isSeen`, `markSeen`, `start()` checking showable at call time, autoplay only
  when not seen, seen written after `drive()`. Browser tests in
  `tests/test_static/test_page_tours_js.py` (`TestSeenTour`): plays on first open (US1-1); not
  after stepping to the end and reopening (US1-2); not after closing mid-tour (US1-3); not after
  navigating away mid-tour (US1-4); a page with a different tour still plays (US1-5); one view
  on two URLs is seen once (US1-6); a fresh browser context plays it again (US1-7); with
  `localStorage` made to throw by an init script, the tour plays on every open and no page error
  is raised (US1-8, FR-006); a nothing-showable tour is not seen (US1-9). The FS-001 browser
  tests keep passing unchanged, each test starting in a fresh context.
- [ ] T004 [US1] FS-001's specification to current state, as plan.md "FS-001's specification",
  and `docs/developer/tours.md`: every sentence saying a tour plays each time its page opens now
  says it plays by itself the first time a browser opens the page. A short "Seen tours" section
  in `tours.md`: what counts as seen, kept in the browser only, keyed by the declaring view so
  renaming or moving it shows the tour again. CHANGELOG `[Unreleased]` entry.

## Phase 2: User Story 2 — A visitor replays a page's tour (P1)

**Goal**: a replay control the developer places plays the tour from its first step, on pages
with a tour only.

**Independent test**: on a page whose tour has been seen, use the control and see the tour play
from its first step; on a page with no tour, see no control.

### Group 1 — the replay control

- [ ] T005 [US2] `{% page_tour_replay %}…{% endpage_tour_replay %}`, as plan.md "The replay
  control". Test templates in `tests/templates/` placing it, test views and URLs in
  `tests/views.py` and `tests/urls.py`. Rendered-HTML tests in
  `tests/test_templatetags/test_page_tours.py` (`TestPageTourReplayTag`): nothing on a page with
  no tour (US2-4); on a page with a tour, one `<template data-page-tour-replay>` holding a
  `<button type="button">` with the block's content; the developer's `class` and other
  attributes are on the button and no other class is (US3-2, FR-011); attribute values are
  escaped; an empty block gives a non-empty translatable fallback (assert it is not empty and
  comes from `gettext`, not its words); a `type` argument does not change `type="button"`; a
  positional argument raises `TemplateSyntaxError`.
- [ ] T006 [US2] Replay wiring in the starter script: each `<template data-page-tour-replay>`
  becomes its button, whose click calls `start()`; an active tour is destroyed before it starts
  again. Browser tests (`TestReplay`): on a seen tour the control plays from step one (US2-1);
  after the end or a close, the page has no Driver.js markup and the control starts it again
  (US2-2); after a replay, reopening does not autoplay (US2-3, FR-013); with JavaScript off no
  replay button is visible (US2-5); the control is focused with Tab and started with Enter
  (US2-6, FR-010); on a nothing-showable tour, using it leaves no Driver.js markup and no page
  error (US2-7); two controls on one page each start it (edge case); with a step pointing at the
  control, using it during that step restarts the tour at step one, with one popover on the page
  (FR-009).
- [ ] T007 [US2] Documentation: new `docs/developer/replaying-a-tour.md` in the Guides toctree
  after `tours`, covering placing the control, giving it your own content and attributes,
  `aria-label` for an icon-only control, and that it shows only on pages with a tour and only
  with JavaScript on. CHANGELOG entry.

## Phase 3: User Story 3 — A developer chooses how a page's tour is started (P2)

**Goal**: a tour marked `autoplay=False` plays only from the control; the control placed once in
a base template shows only where there is a tour; the demo shows both.

**Independent test**: place the control once in a base template shared by a page with a tour and
one without, and see it only on the first; mark a tour `autoplay=False` and see it wait for the
control.

### Group 1 — play only on request, and the demo

- [ ] T008 [US3] `autoplay=False` in the starter script and its tests. `tests/test_tours.py`:
  `autoplay` defaults to `True` (US3-7). Rendered HTML: the payload carries `autoplay` false for
  such a tour. A base test template placing the control once, extended by a page with a tour and
  one without: the control is only on the first (US3-1). Browser tests (`TestOnRequestTour`): a
  fresh browser does not autoplay it (US3-4); the control plays it from step one (US3-5); with
  no control placed, no Driver.js markup appears and the page has no page error (US3-6); with no
  control and an ordinary tour, it still plays once (US3-3).
- [ ] T009 [US3] Demo, as plan.md "Demo": the control in `demo/templates/base.html`; the
  `/plays-once/` and `/on-request/` pages with their templates, views and URLs, linked from the
  header nav and named on the overview. Tests in `tests/test_demo.py`, as its existing tests do:
  both pages answer and carry a tour, `/on-request/` with `autoplay` false; the overview and the
  header link to both (FR-015).
- [ ] T010 [US3] Documentation: `autoplay=False` in `docs/developer/replaying-a-tour.md`
  ("A tour that plays only on request"), with a full example declaring it. CHANGELOG entry.

## Dependencies

US1 → US2 → US3, in that order: US2's replay calls US1's `start()`, and US3's `autoplay=False`
needs the control to be useful. One dispatch per story.

## Requirement coverage

| Requirement | Tasks |
|---|---|
| FR-001 | T003, T008 |
| FR-002, FR-003 | T003 |
| FR-004 | T001, T002, T003 |
| FR-005 | T003 (nothing server-side; no model added) |
| FR-006, FR-014 | T003, T006 |
| FR-007, FR-008 | T005, T006, T008 |
| FR-009, FR-010, FR-013 | T006 |
| FR-011 | T005 |
| FR-012 | T002, T008 |
| FR-015 | T004, T007, T009, T010 |
