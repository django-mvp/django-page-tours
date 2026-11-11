# Decisions — FS-001: A tour on a page

Readings taken while specifying and building, where issue #5 and the specification were silent.
D1 to D6 were seen by the maintainer while specifying. D7 to D13 were self-resolved while
specifying, and D14 onward while planning and building. Each can be overruled.

## D1 — A step whose element is not on the page is skipped silently

No error, no placeholder; the tour moves on. This is CONSTITUTION Article XIII applied to steps.
A hidden element is treated the same way, because highlighting something the visitor cannot see
helps nobody.

**ADR:** none — a behaviour fixed by the specification, not a structural choice

## D2 — A step attached to no element is shown on its own

It is shown on its own as CONTEXT.md describes, which suits an opening welcome.

**ADR:** none — a behaviour fixed by the specification

## D3 — Step titles and texts are translatable

They are the developer's own strings, so Article VIII applies to them now. The tour's own
controls and a translation catalogue stay with R4.

**ADR:** none — a behaviour fixed by the specification

## D4 — Tours work for signed-in and anonymous visitors alike

Nothing about a visitor is needed to play a tour, and the package keeps nothing in the database.

**ADR:** none — a behaviour fixed by the specification

## D5 — One tour belongs to one page

No tours across several pages (README, "What it deliberately is not").

**ADR:** none — already stated in the README and CONTEXT.md

## D6 — The look is Driver.js's own

Article XIV applies, so this feature carries no design work and no sketch.

**ADR:** none — already the constitution's Article XIV

## D7 — The tour plays every time the page opens

Seen state, playing once per browser, the replay control and play-only-on-request are #6. This
feature does not anticipate them beyond leaving room for them.

**ADR:** none — a scope boundary with the next feature, recorded in its specification

## D8 — A step's title and description are passed to Driver.js as they are

Driver.js writes a step's title and description into the page as HTML. They come from the
developer's code, like the tour's own labels, so they are passed on unchanged and markup in them
renders. The documentation tells the developer never to build one from a visitor's input.

**ADR:** none — a behaviour fixed by the specification (FR-006)

## D9 — Both class-based and function-based views can have a tour

Django projects use both, and a package that served only one would leave half of every project
out. How the tour attaches to each is a planning question.

**ADR:** none — a behaviour fixed by the specification (FR-002)

## D10 — One-time setup in the base template is allowed

"No JavaScript" (G1) is about each tour. Installing the app and placing the package's setup once
in the base template is ordinary Django package setup and is not the developer writing
JavaScript.

**ADR:** none — a reading of goal G1, recorded in the specification's assumptions

## D11 — A mistake in a declared tour is reported to the developer, not hidden from the visitor

A tour with no name or no steps is an error raised before any visitor
sees the page. Skipping silently is reserved for what depends on the page at run time (a missing
element), where the developer cannot know in advance.

**ADR:** none — a behaviour fixed by the specification (FR-004)

## D12 — A step whose selector matches several elements attaches to the first

This is Driver.js's own behaviour and the least surprising reading.

**ADR:** none — Driver.js's own behaviour, recorded in the specification's edge cases

## D13 — A page with no tour loads nothing of the package

A site that installs the package for one page should not pay for it on every other page, and
Article XIII asks that a page without a tour be the same as without the package.

**ADR:** none — a behaviour fixed by the specification (FR-007)

## D14 — Browser installation in CI is set up outside this branch

The browser tests need the shared tests workflow called with `install-playwright: true`. That
change lands on main as its own pull request, and this branch is rebased onto it before it is
marked ready for review, so no workflow file changes here.

**ADR:** none — a one-off arrangement of this pull request

## D15 — A tour plays only on the page its own view renders, never on an error page shown in its place

A view with a tour that raises `Http404` or `PermissionDenied` is followed by a 404 or 403 page
rendered with the same request. Looking the tour up from the URL's view would play it there,
including to a visitor refused the page. The tag reads the class-based view from the context,
and `with_tour` marks the request only while its view runs without error.

**ADR:** docs/adr/0001-a-tour-is-found-from-the-page-its-own-view-renders.md

## D16 — Driver.js's step count stays off

It counts skipped steps, so a tour with a missing element would count steps the visitor never
sees.

**ADR:** none — a configuration detail local to the starter script

## D17 — The demo's text field submits by GET

The demo page is a `TemplateView`, which answers GET only.

**ADR:** none — local to the demo project

## D18 — No fallback for browsers without `Element.checkVisibility()`

Every current browser has it, and the browser tests run in Chromium only.

**ADR:** none — local to the starter script, revisited only if older browsers become a target

## D19 — A step has no required fields

A step mirrors a Driver.js step, whose title and description are both optional, so `TourStep`
checks nothing (FR-004).

**ADR:** none — a reading of FR-004, local to TourStep

## D20 — Spec change, approved at the specification gate: what works while a step shows

SC-005 and User Story 2's independent test said every control on the page works "during" the
tour. Driver.js, which FR-008 makes the tour's drawing library, covers the page with an overlay
while a step shows, and a click on the overlay closes the tour, so only the element the step is
attached to can be used during it. Both now read: while a step shows, its attached element works
and the rest of the page is reached by closing the tour in one action; after the tour ends or
fails, every control works. This keeps Article XIII, which allows a change to the page only
while a step is showing.

**ADR:** none — the change is recorded in the specification itself

## D21 — No formatting hook touches the vendored Driver.js files

The end-of-file and trailing-whitespace hooks rewrote them, and Article XII asks for the
published release as it is. Their directory is excluded from pre-commit.

**ADR:** none — local to the hook configuration, explained in a comment there
