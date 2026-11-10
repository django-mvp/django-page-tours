# Research — FS-003 A site's own look for its tours

## Assumptions checked

The specification assumes these already work. Each was run or read on 2026-11-10 against `main`
at the 0.1.0 release.

- **The demo project is served and has a place for a styled tour.** `tests/test_demo.py` and the
  template-tag tests pass (56 passed). `demo/templates/base.html` places `{% page_tour %}` in the
  `<head>`, with a `head` block after it, so a demo page can add its own stylesheet.
- **Driver.js 1.10.2 takes a class for the box a step is shown in.** The shipped
  `driver.js.iife.js` reads `popoverClass` from the tour's configuration and from each step, and
  adds it to the box. It also calls an `onPopoverRender` hook with the box's parts after each step
  is drawn. FR-004 and FR-009 have a surface to build on without changing the shipped Driver.js
  (Article XII).
- **Driver.js's own class names are what a site targets today.** The box, title, text, progress,
  footer, previous, next, done and close controls carry `driver-popover-*` classes, and the
  highlight is drawn as `driver-overlay`. These are Driver.js's internal names, the ones the issue
  says can change with any release. FR-001 and FR-002 put the package's own documented names
  beside them.
- **A site's ordinary CSS loses to Driver.js's today.** `driver.css` styles the box with a
  single-class rule that begins with `all: unset`, and the package links it from wherever
  `{% page_tour %}` sits. The demo's own `<style>` comes before that tag, so a site rule as
  specific as Driver.js's, placed there, is overridden. FR-003 exists for this.
- **Driver.js's stylesheet is not only a look.** It also fixes the box's position and stacking and
  draws the highlight overlay, which is why the specification keeps it loaded in every case.
- **The package already has system checks.** `page_tours/checks.py` registers a check with
  Django's framework, so FR-008 adds to an existing surface.
