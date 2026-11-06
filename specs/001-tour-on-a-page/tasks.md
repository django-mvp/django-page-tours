# Tasks: A tour on a page

**Input**: [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md)

Every behaviour task is test-first. Tests follow `docs/contributing/standards/testing.md`: no
assertions on wording or layout, elements found by id or role, one behaviour per test.

## Format: `[ID] [Story] Description`

## Phase 1: User Story 1 — A developer gives a page a tour (P1)

**Goal**: a tour declared in Python reaches the page its view renders, escaped and in order,
and plays in the browser.

**Independent test**: declare a three-step tour on a view, open the page, and find the steps in
the page in the declared order, with every file served by the site.

### Group 1 — declaring a tour

- [ ] T001 [US1] Vendor Driver.js 1.10.2: copy `dist/driver.js.iife.js`, `dist/driver.css` and
  `license` (as `LICENSE`) byte for byte into
  `page_tours/static/page_tours/vendor/driver.js-1.10.2/`. Test in
  `tests/test_static/test_vendor.py` (`TestVendoredDriverJs`) that the staticfiles finders find
  all three (FR-008).
- [ ] T002 [US1] `TourStep` and `Tour` in `page_tours/tours.py`, frozen dataclasses. Empty
  `steps`, and a step with an empty or whitespace-only `title` or `text`, raise
  `ImproperlyConfigured` on
  construction. `steps` is stored as a tuple (FR-003, FR-004). Tests: `TestTourStep`,
  `TestTour` in `tests/test_tours.py`.
- [ ] T003 [US1] `Tour.as_driver_steps()`: one dict per step in declared order, `title` and
  `text` as `escape(str(...))`, `element` only when the step names one. Tests: order kept; a
  step with and without an element; `<b>&"'` in a title and a text come out escaped; a
  `gettext_lazy("Yes")` title under `translation.override("de")` comes out as the German string
  (FR-003, FR-005, FR-006).
- [ ] T004 [US1] `with_tour(tour)` decorator and `Tour.for_page(context)`, exactly as plan.md
  "Declaring a tour": a class-based view's tour from `context["view"].tour`; a function-based
  view's from `request.page_tour`, which `with_tour` sets before calling the view and removes if
  the view raises; through `login_required` in either order; `None` with no view and no
  request, for a view with no tour, and for a non-`Tour` value (FR-001, FR-002). Export `Tour`,
  `TourStep`, `with_tour` from `page_tours/__init__.py`. Tests: `TestWithTour`,
  `TestTourForPage` in `tests/test_tours.py`, using `rf` requests and plain context dicts.

### Group 2 — the one-time setup and the starter script

- [ ] T005 [US1] `{% page_tour %}` inclusion tag in `page_tours/templatetags/page_tours.py` and
  `page_tours/templates/page_tours/page_tour.html`, exactly as plan.md "The one-time setup".
  Test views (one class-based, one function-based with `with_tour`, one with no tour, the
  class-based one routed on two URLs) in `tests/views.py`, `tests/urls.py`, and a base
  template in `tests/templates/` with the tag in `<head>`; `TEMPLATES[0]["DIRS"]` in
  `tests/settings.py`. Tests in `tests/test_templatetags/test_page_tours.py`
  (`TestPageTourTag`), through `client`: the page carries the steps in `#page-tour-steps` in
  order (US1-1); a step's element is in its JSON entry and a step with none has no `element`
  key (US1-2, US1-3); a page with no tour carries no `page-tour-steps` and no reference to
  `page_tours/` (US1-4, FR-007); every `src` and `href` the tag emits starts with
  `STATIC_URL` and names no scheme or host (US1-5, SC-003); markup characters in a step reach
  the page escaped inside the JSON (US1-7); a signed-in and an anonymous visitor get the same
  tag output (US1-9, FR-014); both URLs of the same view carry the tour (edge case); the
  function-based view's page carries its tour (FR-002); a template rendered with no request in
  its context renders the tag as nothing; a class-based and a function-based test view with a
  tour that raise `Http404` give a 404 page (a `tests/templates/404.html` extending the test
  base template) with no `page-tour-steps` (plan.md "A tour is emitted only on the page its own
  view renders"); a page rendered under `translation.override("de")` carries the German title
  of a `gettext_lazy("Yes")` step in `#page-tour-steps` (US1-6).
- [ ] T006 [US1] `page_tours.W001` in `page_tours/checks.py`, registered in
  `PageToursConfig.ready()`, a `Warning` when no `DjangoTemplates` backend has
  `django.template.context_processors.request`; message wrapped with `gettext_lazy`. Tests:
  `TestRequestContextProcessorCheck` in `tests/test_checks.py`, through
  `django.core.checks.run_checks()` (warns without it, silent with it, asserted by check id).
- [ ] T007 [US1] `page_tours/static/page_tours/page-tours.js`: plan.md "The starter script"
  steps 1, 2 (without the visibility test: an element step resolves to the first
  `querySelector` match) and 4. Browser-test set-up: `DJANGO_ALLOW_ASYNC_UNSAFE=true` in
  `[tool.pytest.ini_options] env`; `tests/test_static/` declared in
  `[tool.forge.conformance] non-mirror-paths`; `tests/test_static/__init__.py`. Test in
  `tests/test_static/test_page_tours_js.py` (`TestTourPlays`): opening the class-based test
  page in Chromium shows a Driver.js popover whose title is the first step's (US2-1), and a
  step whose title has markup characters shows them as text (US1-7, FR-006), asserting by
  `.driver-popover-title` `text_content()` equal to the fixture value.
- [ ] T008 [US1] Documentation: new `docs/developer/tours.md` ("Adding a tour to a page": the
  one-time setup, declaring a tour on a class-based and a function-based view, the two kinds of
  step, what is checked at start-up, the `W001` warning, that titles and texts are plain text
  and translatable); add it to `docs/developer/index.md`; the base-template step in
  `docs/developer/installation.md`; the quickstart in `docs/index.md` and `README.md`;
  `CHANGELOG.md` under Unreleased with the Driver.js release and both sha256 values. The docs
  build clean (`-W`).

**Checkpoint**: US1's acceptance scenarios 1–9 each have a passing test.

## Phase 2: User Story 2 — A visitor follows a page's tour (P1)

**Goal**: the tour plays, moves both ways, closes, skips what it cannot show, and never breaks
the page, with or without JavaScript.

**Independent test**: on the demo tour page in a browser, go forward to the last step and back
to the first, close part-way, and use the page's own controls throughout.

### Group 1 — the visitor's tour

- [ ] T009 [US2] Moving and closing, in `TestTourNavigation`: next and previous show the next
  and previous step in declared order (US2-2); closing at a middle step leaves no element with
  a `driver-` class or `#driver-dummy-element` and no `driver-` class on `body` (US2-3); next on
  the last step does the same (US2-4).
- [ ] T010 [US2] Skipping, plan.md "The starter script" steps 2 and 3 in full: visibility test,
  invalid selector treated as missing, no tour when nothing is showable. Tests in
  `TestTourSkipsSteps`: a step whose element is missing is skipped going forward and going back
  with no console error (US2-5); a step whose element is `hidden` is skipped (edge case,
  FR-012); a step whose selector is invalid is skipped; a tour whose first step's element is
  missing starts at its second step (FR-010); a tour whose every step names a missing
  element plays nothing and leaves no `driver-` markup (US2-6); a selector matching two
  elements highlights the first (edge case).
- [ ] T011 [US2] Failure, plan.md "The starter script" step 5. Tests in `TestTourFailure`, each
  fault injected as plan.md "Tests" describes, each asserting no `driver-` markup left and the
  page's own control still working and no element carrying
  `aria-controls="driver-popover-content"`: the Driver.js file cannot load (FR-009); Driver.js fails
  while starting (US2-7); a step fails while the tour is playing (US2-7, SC-005).
- [ ] T012 [US2] JavaScript off, `TestTourWithoutJavaScript`: the same template rendered with and
  without a tour has equal `inner_text("body")` and equal bounding boxes for every element in
  `body` (US2-8, FR-009, SC-004).
- [ ] T013 [US2] Demo page per plan.md "Demo page": `TourView` at `/tour/`, `demo/tour.html`,
  the tag in `demo/templates/base.html`, the link in the page bar, the overview page updated.
  Tests in `tests/test_demo.py`: `TestTourPage` responds, is linked from the bar, and its
  `#page-tour-steps` carries a step with an element on the page, a step with none, and a step
  whose element is not on the page (FR-015); one browser test walks the demo tour forward
  through every showable step, back to the first, and closes it, then uses the page's
  disclosure (SC-002, SC-005).
- [ ] T014 [US2] Documentation: what a visitor sees in `docs/developer/tours.md` (plays on every
  visit, moving and closing, missing and hidden elements skipped, a failing tour ends, nothing
  with JavaScript off); `CHANGELOG.md` and `README.md` updated to match. The docs build clean.

**Checkpoint**: US2's acceptance scenarios 1–8 each have a passing test; the demo page shows all
three kinds of step.

## Dependencies

US1 Group 1 → US1 Group 2 → US2. One worktree, one dispatch at a time. US2 builds on the tag,
the test pages and the browser set-up US1 Group 2 leaves.

## Requirement coverage

| Requirement | Tasks |
|---|---|
| FR-001 | T004, T005 |
| FR-002 | T004, T005 |
| FR-003 | T002, T003, T005 |
| FR-004 | T002 |
| FR-005 | T003 |
| FR-006 | T003, T005, T007 |
| FR-007 | T005 |
| FR-008 | T001, T005 |
| FR-009 | T011, T012 |
| FR-010 | T007, T010 |
| FR-011 | T009 |
| FR-012 | T010 |
| FR-013 | T011 |
| FR-014 | T005 (no models: nothing to migrate) |
| FR-015 | T008, T013, T014 |
| SC-001 | T005, T007 (the test pages are Python and one template tag) |
| SC-002 | T013 |
| SC-003 | T005 |
| SC-004 | T012 |
| SC-005 | T011, T013 |
