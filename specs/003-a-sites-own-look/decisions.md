# Decisions — FS-003 A site's own look for its tours

Readings taken where issue #22 was silent, while specifying. Each is integrated into `spec.md` and
can be overruled.

## D1 — Two developer stories, no visitor story

A visitor of the site gains no new way to do anything: they see the same tour in the site's
design. The two people who gain something are the developer styling one site and the author of a
design system styling every site built on it. They set out to do different things, so they are
separate stories.

**ADR:** none — the shape of the specification

## D2 — Both ways of styling: rules against documented names, and classes in configuration

The issue asks for a site's own CSS. A site that writes its own rules needs names to write them
against that survive a Driver.js release. A site built on a utility-class framework styles with
classes it already has rather than new rules, so it needs to give the parts those classes. Either
alone leaves one kind of site overriding the template, which is what the issue rules out (FR-001,
FR-004).

**ADR:** none — a behaviour fixed by the specification

## D3 — The documented names are public surface

Names that may change with a Driver.js release are what the site has today, so the new names are
only worth having if Article XI covers them (FR-002).

**ADR:** none — Article XI applied

## D4 — A site's rule wins at equal specificity, wherever it is linked

Today the package's copy of Driver.js's stylesheet is linked where `{% page_tour %}` sits, so a
site rule of the same specificity linked before it loses. Asking sites to out-rank it, or to place
their stylesheet after the tag, makes styling depend on template order (FR-003).

**ADR:** none — a behaviour fixed by the specification

## D5 — Driver.js's stylesheet always loads

It positions the box and draws the highlight as well as giving the default look. Making it
optional would mean splitting the shipped stylesheet or rewriting its layout, and the site's rules
already lay over it once D4 holds. Out of scope.

**ADR:** none — a scope boundary of this feature, which nothing downstream inherits

## D6 — Site-wide only, not per tour or per step

The issue asks for a site's tours to look like the site. Per-tour or per-step styling is a new
way that nothing asks for yet, and "fewer settings beat more" (README). It can be added later as
one more story.

**ADR:** none — a scope boundary of this feature, which a later story can widen

## D7 — A design system reaches every site by being installed

A design system's own base template already loads its stylesheet, so its rules against the
documented names need nothing from the package. Its classes for the parts are defaults an
installed app supplies. The project's own configuration replaces them part by part, and the first
app in the installed apps wins between two apps, as Django resolves templates and static files
(FR-009, FR-010).

**ADR:** none — a behaviour fixed by the specification. How an app supplies its defaults is for
planning.

## D8 — A wrong configuration is reported by the system checks and never breaks a page

Article XIII: a tour never breaks its page, and a styling mistake is no reason to. The checks
framework is where the package already reports a project's setup (FR-008).

**ADR:** none — Article XIII applied

## D9 — The replay control and the tour's wording are out of scope

The replay control already takes the site's own content and classes (issue #6). What a step says
belongs to its declaration, and the controls' labels to the package's translations.

**ADR:** none — a scope boundary of this feature, which nothing downstream inherits

## D10 — Glossary terms for the build

The build adds "part of a step" and the highlight to `CONTEXT.md`, under Tour step, so the
documented names have a definition. "Popover" stays avoided as a word for the step itself.

**ADR:** none — vocabulary

## D11 — Driver.js's stylesheet is imported into a layer by a one-line file of the package's

FR-003 needs Driver.js's rules under the site's wherever the site links its stylesheet, and only a
cascade layer does that without editing `driver.css`. An inline `<style>` import would break under
the strict content security policy the README promises, so the package links
`page-tours.css`, which holds one `@import` of `driver.css` into layer `page-tours` and no rule of
its own. FR-006 is read as the package adding no style rules: Driver.js's are still the only ones.

**ADR:** docs/adr/0005-driver-js-styles-sit-in-the-lowest-cascade-layer.md

## D12 — The layer is kept first in the document by the starter script

A layer declared after a framework's layers outranks them, so a site whose framework classes sit
in layers (Tailwind v4) would lose to Driver.js's defaults whenever `{% page_tour %}` comes after
its stylesheet. The starter script moves the package's link to the start of `<head>`, so the
`page-tours` layer is always the lowest, and no rule about where the tag sits is needed.

**ADR:** docs/adr/0005-driver-js-styles-sit-in-the-lowest-cascade-layer.md

## D13 — The highlight's fill and opacity become presentation attributes

Driver.js writes them as inline styles, which no stylesheet rule can beat. As the `fill` and
`fill-opacity` presentation attributes on the overlay they look the same and give way to any rule
a site writes. The opacity goes to `fill-opacity` because Driver.js's fade-in animates the
overlay's own `opacity`.

**ADR:** none — local to the starter script

## D14 — App defaults are an `AppConfig` attribute, warnings are warnings

`page_tour_classes` on an app's `AppConfig`, read in `INSTALLED_APPS` order through Django's app
registry, is the least machinery that gives per-part, first-app-wins defaults (planning note 2).
Wrong entries are `Warning`s, not `Error`s, because an error stops `runserver`, and FR-008 says a
styling mistake never stops a page.

**ADR:** none — follows from FR-008 and FR-010 with Django's own mechanisms

## D15 — Values are strings; an empty string clears a part

One shape for configured classes keeps the setting simple. An empty string is the way a project
removes an app's classes from one part, which FR-010's part-by-part replacement implies.

**ADR:** none — local to the setting's shape

## D16 — The part lookup is one class, `TourParts`

The plan first had two module-level functions over the same subject. Article X puts them on one
class with classmethods, `TourParts.sources()` and `TourParts.classes()`, with the parts as its
class attribute. No base class and no registry: one class grouping today's behaviour.

**ADR:** none — Article X applied

## D17 — Lesser points from the design review, carried as watch items

- The existing test listing the payload's keys gains `"parts"`, the specified payload change.
- `page-tours.css` is tested as found by the finders, not for its one line, which would only
  record a decision.
- The CHANGELOG and the styling page say that a framework's layered reset now reaches the tour as
  it reaches the page, and that styling the documented names settles it.
- If the first step's cascade assertions are flaky, the tour starts from the moved link's `load`
  event. If ending the tour from inside the render hook raises, it ends from a microtask.
- The pull request description names D11's reading of FR-006 for the merge gate.

**ADR:** none — review record

## D18 — The overlay is named by a watcher, and a failed hook ends the tour from a microtask

Driver.js renders the first step's box before it creates the overlay, and creates the overlay a
moment before it reports that step as highlighted, so the render hook finds no overlay on the first
step and a later hook would leave the first step unnamed for the length of its animation. The
starter script watches the body for the overlay being added and names it then, on every tour. A
hook that throws ends the tour from a microtask, because ending it inside the hook let Driver.js
add its markup to the page afterwards.

**ADR:** none — local to the starter script
