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

## Planning notes

### "FR-003 is the main risk. Keep the shipped Driver.js stylesheet byte-identical to its release: put it in a cascade layer rather than editing a copy of it."

**Adopted.** `driver.css` stays byte-identical. The package links one new file,
`page_tours/static/page_tours/page-tours.css`, whose only content is
`@import url("vendor/driver.js-1.10.2/driver.css") layer(page-tours);`. Rules outside any layer
beat every layered rule whatever their specificity or order, so a site's ordinary stylesheet wins
over Driver.js's defaults wherever it is linked (FR-003).

Two findings shape how the layer is used:

- **Layer order is set by where a layer first appears.** A site built on a framework that puts its
  own rules in layers (Tailwind v4 puts `.btn`-style classes in `@layer utilities` and
  `@layer components`) would lose to the `page-tours` layer whenever the package's stylesheet is
  linked after the site's, because a later layer outranks an earlier one. The starter script
  therefore moves the package's `<link>` to the start of `<head>` before the tour starts, so the
  `page-tours` layer is always declared first and is the lowest of all layers. With JavaScript
  off nothing is moved, and nothing needs to be: no tour plays.
- **An inline `<style>@import … layer()</style>` was ruled out.** The README promises the package
  works under a strict content security policy (`README.md`, "Scope & philosophy"), and
  `style-src 'self'` blocks inline style. A linked file is allowed by it.

FR-006 is read as the package adding no style rules of its own: the new file holds one import and
no rules, so Driver.js's stylesheet is still the only one whose rules apply (decision D11).

Consequence, recorded in the CHANGELOG: a site rule written against a bare element, such as
`button { … }`, now reaches the tour's controls as it reaches the rest of the page, where today
Driver.js's more specific class rules win. Driver.js 1.10.2 builds its box from `div`, `span` and
`button` elements only (read from `driver.js.iife.js`), and its positioning rules are on its own
classes, so no common element rule moves the box. That is the behaviour the issue asks for: the
tour takes the site's look.

### "For the defaults an installed app supplies (FR-009, FR-010), choose the least machinery that meets them, and look first for an existing Django mechanism before building any discovery of the package's own."

**Adopted.** An installed app supplies its defaults as an attribute on its own `AppConfig`,
`page_tour_classes`, a dict from part to class names. The package reads it with
`django.apps.apps.get_app_configs()`, which returns apps in `INSTALLED_APPS` order, so "the first
listed wins" (FR-010) is the order Django already gives, as it does for templates and static
files. The `AppConfig` attribute is the mechanism Django itself uses for per-app settings
(`default_auto_field`). Overriding a package template was considered and ruled out: a template is
replaced whole by the first app that has it, so it cannot merge two apps part by part as the
edge case requires, and the issue rules template overrides out.

## The parts and how they are reached

Driver.js 1.10.2 creates a new box for every step and calls `onPopoverRender(popover, opts)` after
drawing it (`driver.js.iife.js`, the `onRender` callback). `popover` holds the elements:
`wrapper` (the box), `title`, `description`, `progress`, `previousButton`, `nextButton`,
`closeButton`. The next button is the done control on the last step: Driver.js writes
`doneBtnText` into the same element when no later step can be shown, and `opts.driver.isLastStep()`
answers the same question with the same skipping rule. The first step's previous control is
present and marked disabled by Driver.js (`driver-popover-btn-disabled`), so it is reached the same
way.

The highlight is the overlay `svg.driver-overlay`, created once when the tour starts and kept
between steps; later steps only rewrite its path. Driver.js sets the path's fill and opacity as
inline styles (`a.style.fill`, `a.style.opacity`), and an inline style beats any rule in a
stylesheet, so FR-003 cannot hold for the highlight as Driver.js leaves it. The starter script
moves those two values onto the `svg` as `fill` and `opacity` presentation attributes. A
presentation attribute gives way to any stylesheet rule, the path inherits the fill, and with no
site rule the overlay looks exactly as before.

## What already exists

- documented names on the parts · 7, new · Driver.js offers `popoverClass` for the box only;
  searched the `onPopoverRender` hook's arguments, which reach every part, and the hook is used
- applying classes to the parts · 5, browser · `Element.classList.add`, from the existing
  `json_script` payload (FR-007: the values never pass through HTML)
- the list of parts and their names · 7, new · a tuple in `page_tours/parts.py`; nothing in
  Django or Driver.js names these parts
- classes from the project · 4, Django · `django.conf.settings`, one setting `PAGE_TOURS_CLASSES`
- classes from an installed app · 4, Django · `AppConfig` attribute read through
  `django.apps.apps.get_app_configs()`
- reporting a wrong configuration · 2, this repo · `page_tours/checks.py`, Django's checks
  framework, as `page_tours.W001` already does
- putting Driver.js's rules under the site's · 5, browser · CSS cascade layers, `@import … layer()`
- the highlight giving way to site rules · 5, browser · SVG presentation attributes
- documentation page · 2, this repo · `docs/developer/`, beside `replaying-a-tour.md`
- the demo's styled tour · 2, this repo · a demo page with its own `head` block, as `base.html`
  already allows
