# Tasks: A site's own look for its tours

**Input**: [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md)

Every behaviour task is test-first. Tests follow `docs/contributing/standards/testing.md`: no
assertions on wording or layout, elements found by id, role, attribute or documented class name,
one behaviour per test. Browser behaviour is tested in a real browser; what a test client can see
is tested on the rendered HTML. The cascade tests assert that a site's rule takes effect on the
part it names, which FR-003 makes a contract; they never assert what Driver.js's default looks
like.

## Format: `[ID] [Story] Description`

## Phase 1: User Story 1 — A developer styles a site's tours with the site's own CSS (P1)

**Goal**: every part of a shown step carries its documented name and the project's configured
classes, and a site's own rules beat Driver.js's defaults wherever they are linked.

**Independent test**: on a page with a tour, add a rule against one documented name to the
site's stylesheet and give one part a class through configuration; play the tour and confirm both
take effect on the parts they name and on no other part.

### Group 1 — the parts, the setting and the checks

- [ ] T001 [US1] `page_tours/parts.py` with `TourParts`, as plan.md "The parts" and "Classes for
  the parts", with the project setting as the only source for now (`TourParts.sources()` yields
  the setting only; US2 adds the apps). Tests in `tests/test_parts.py` (`TestTourParts`): with no setting every
  part carries only its documented name; a configured part carries its name then its classes,
  split on whitespace, and no other part carries them (US1-3); an empty string leaves the name
  only; an unknown part, a non-string value and a setting that is not a dict are skipped without
  raising (FR-008).
- [ ] T002 [US1] The payload gains `"parts"`, as plan.md "The tag's payload". Tests in
  `tests/test_templatetags/test_page_tours.py` (`TestPageTourPayload`): the payload carries every
  part with its name; a configured value is carried; a value holding `"><script>` and `</script>`
  stays inside the `json_script` element and adds no element to the page (US1-8, FR-007); a page
  with no tour still emits nothing (US1-10); a page renders with a wrong setting (FR-008). The
  existing test that lists the payload's keys gains `"parts"` in its expected set, as the
  specified change to the payload, and nothing else in it changes.
- [ ] T003 [US1] Checks `page_tours.W002` and `page_tours.W003` for the setting, as plan.md
  "System checks". Tests in `tests/test_checks.py` (`TestClassesCheck`): an unknown part gives
  `W002` naming the part and the setting; a non-string value and a non-dict setting give `W003`;
  a valid setting and no setting give nothing; both are warnings, so they do not stop the checks
  passing (US1-9). Assert ids and the named part, never the sentence.

### Group 2 — the browser

- [ ] T004 [US1] The stylesheet layer, as plan.md "The stylesheet layer" and "The starter
  script" item 1: `page_tours/static/page_tours/page-tours.css`, the template links it with
  `data-page-tour-stylesheet` in place of `driver.css`, and the starter script prepends that link
  to `<head>`. Tests: in `tests/test_templatetags/test_page_tours.py` the page links the
  package's one stylesheet; in `tests/test_static/test_vendor.py` `page-tours.css` is found by the
  finders; in the browser (`TestOwnLook`), the package's link is the
  first stylesheet in the document once the tour shows, and the page's only package stylesheet
  rules are Driver.js's (US1-7, FR-006).
- [ ] T005 [US1] Naming the parts and adding their classes, as plan.md "The starter script"
  item 2, with the `try` → `endTour()` guard. Test views, URLs and templates as needed. Browser
  tests (`TestPartNames`): on an attached step every part listed in plan.md carries its name
  (US1-1); an unattached step carries the same names and classes (US1-4); the first step's
  previous control (disabled), a middle step's next and the last step's done control carry their
  own names and configured classes, `done` never `next` on the last step (US1-5); a configured
  class is on its part on every step and on no other part (US1-3); with classes on the controls
  their accessible names are unchanged, Tab reaches them, Enter activates them, and arrow keys and
  Escape work as without classes (US1-6, FR-005); a tour started from the replay control carries
  the same names and classes (FR-011); with no setting no element of the tour (the box, the overlay and their
  descendants) carries a class outside `driver-` and `page-tour-` (US1-7); with an init script that makes `classList.add` throw for one
  part, the tour ends, `assert_no_driver_markup` holds and no page error is raised (edge case).
- [ ] T006 [US1] The highlight and the cascade, as plan.md "The starter script" item 3. Test
  templates placing a site `<style>` before and after `{% page_tour %}`. Browser tests
  (`TestOwnLook`): a rule against `page-tour-box` at the specificity of Driver.js's `.driver-popover`
  takes effect with the site's style before the tag, and again after it (US1-2, FR-003); a rule
  against `page-tour-highlight` sets the overlay's computed fill, before and after (edge case,
  FR-003); a class configured on the box whose rule sits in a site `@layer` declared before the
  tag takes effect (plan.md "The stylesheet layer"); the highlight carries its name on an attached
  and an unattached step.

### Group 3 — documentation and demo

- [ ] T007 [US1] `docs/developer/styling-tours.md` and its toctree entry, as plan.md
  "Documentation and demo", without the design-system section (US2 adds it); README public
  surface and "Styling" pointer; CHANGELOG `[Unreleased]` Added and Changed entries; `CONTEXT.md`
  "Part of a step" and "Highlight" (D10). The docs build clean with `-W`.
- [ ] T008 [US1] The demo's "Own look" page, as plan.md "Documentation and demo": view, URL,
  template, nav link, `PAGE_TOURS_CLASSES` in `demo/settings.py`. `tests/test_demo.py`: the page
  renders with its tour and its steps, as the other demo pages are tested (FR-012).

## Phase 2: User Story 2 — A design-system author styles tours once for every site built on it (P2)

**Goal**: an installed app supplies classes for the parts as defaults; the project replaces them
part by part; the first listed app wins.

**Independent test**: install a reusable app that supplies classes for the parts and a
stylesheet against the documented names into a project with no tour styling of its own; play a
tour and confirm the parts carry the app's classes and the app's rules take effect. Then give one
part a class in the project's configuration and confirm that part takes the project's classes
while the others keep the app's.

### Group 1 — app defaults

- [ ] T009 [US2] `TourParts.sources()` reads `AppConfig.page_tour_classes`, as plan.md "Classes for
  the parts" and "Design-system defaults". Test apps `tests/design_system/` and
  `tests/other_design_system/` (each `__init__.py`, `apps.py`; the first also a static stylesheet
  against the documented names). Tests in `tests/test_parts.py` (`TestTourPartsAppDefaults`), with
  `override_settings(INSTALLED_APPS=...)`: an installed app's classes apply with no setting
  (US2-1); a project setting for one part replaces the app's for that part only (US2-3); an empty
  string in the setting clears the app's classes for that part; the first of two apps wins per
  part, and the second still supplies the parts the first does not (edge case, FR-010); no app
  and no setting gives names only (US2-4); a bad entry from an app is skipped.
- [ ] T010 [US2] The checks report app entries, naming the app's label (US2-5). Tests in
  `tests/test_checks.py` (`TestClassesCheck`): an app's unknown part gives `W002` naming the part
  and the app; an app's bad value gives `W003` naming the app.
- [ ] T011 [US2] Browser test (`TestAppDefaults` in `tests/test_static/test_page_tours_js.py`):
  with the test app installed and a test base template linking its stylesheet, the parts carry
  the app's classes and its rule against a documented name takes effect (US2-1, US2-2); with the
  setting configuring one part, that part carries the project's classes and another keeps the
  app's (US2-3).
- [ ] T012 [US2] The design-system section of `docs/developer/styling-tours.md`, the
  `AppConfig.page_tour_classes` entry in the README's public surface and its CHANGELOG line.
