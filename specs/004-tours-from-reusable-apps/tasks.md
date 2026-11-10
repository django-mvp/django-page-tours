# Tasks: Tours shipped by reusable apps

**Input**: [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md)

Every behaviour task is test-first. Tests follow `docs/contributing/standards/testing.md`: no
assertions on wording or layout, one behaviour per test. Browser behaviour is tested in a real
browser; what a test client can see is tested on the rendered HTML.

## Format: `[ID] [Story] Description`

## Phase 1: User Story 1 — A project developer changes or turns off a tour shipped by an installed app (P1)

**Goal**: a project replaces or turns off an installed app's tour with `PAGE_TOURS_OVERRIDES`,
without touching the app.

**Independent test**: open an app's page and see its tour; set a replacement and see the
replacement; set `None` and see no tour and no replay control; the app's files unchanged.

### Group 1 — the setting and the check

- [x] T001 [US1] `tour_overrides()` and the lookup in `Tour.for_page`, as plan.md "Resolving the
  setting", with the test views and routes from plan.md "Tests". Tests in `tests/test_tours.py`
  `TestTourOverrides` (scenarios 2, 4, 5, 6, 7, 11; FR-005, FR-006, FR-008).
- [x] T002 [US1] `PageToursConfig.ready` resolves the setting at start-up (FR-010). Tests in
  `tests/test_tours.py` or `tests/test_apps.py`: each refusal of `tour_overrides()`, and `ready`
  raising for a bad setting and for a replacement module whose tour is invalid.
- [x] T003 [US1] The tag and replay control on an overridden page, as plan.md "The tag and the
  replay control" (no code expected). Tests `TestOverriddenTourPayload` in
  `tests/test_templatetags/test_page_tours.py` (scenarios 2, 3, 4, 5, 8) and
  `TestOverriddenTourSeen` in `tests/test_static/test_page_tours_js.py` (scenario 9).
- [x] T004 [US1] `with_tour` records its name on the wrapper; `declared_tour_names` and
  `page_tours.W002`, as plan.md "The stale-change check". Tests `TestOverridesCheck` in
  `tests/test_checks.py` (scenario 10, FR-009).

### Group 2 — demo and documentation

- [x] T005 [US1] The demo's library app, `demo/tours.py`, the setting and the overview links, as
  plan.md "Demo project". Tests in `tests/test_demo.py` (FR-011).
- [x] T006 [US1] The guide page, the tours guide sentence, README, CHANGELOG and `CONTEXT.md`, as
  plan.md "Documentation" (FR-011). The docs build passes with `-W`.
