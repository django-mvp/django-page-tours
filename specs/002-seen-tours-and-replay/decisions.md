# Decisions — FS-002 Seen tours and replay

Readings taken where issue #6 and the specification were silent. D1 to D13 were taken while
specifying and are integrated into `spec.md`. D14 onward were taken while planning and building.
Each can be overruled.

## D1 — Seen lives in the browser only

No database tables, nothing about visitors on the server, so a new browser or device sees the
tour again. Stated by the issue and by the README's scope; recorded here because it rules out
seen state per account (FR-005).

**ADR:** none — a behaviour fixed by the specification (FR-005)

## D2 — A tour counts as seen once it has played

Whether finished, skipped or closed, as `CONTEXT.md` defines Seen (FR-002, FR-003).

**ADR:** none — the glossary's definition, fixed by the specification

## D3 — A developer can make a tour play only from the replay control

Playing once by itself is the default, so a developer who only declares a tour gets the main
benefit with no setting (FR-012).

**ADR:** none — a behaviour fixed by the specification (FR-012)

## D4 — The replay control is something the site places on its own page

It is shown only where the page has a tour. Where it goes in a particular design system is that
design system's choice; a design system built on this package can put it in its navigation bar
(FR-007, FR-008).

**ADR:** none — a behaviour fixed by the specification

## D5 — Out of scope: changed tours and seen state across browsers

Showing a changed tour again is R7 (tour versions). Seen state that follows a signed-in person
across browsers is not built.

**ADR:** none — a scope boundary recorded in the specification's assumptions

## D6 — No sketch

The control carries no look of its own (Article XIV), and the feature adds no page or form that
needs a design judgement.

**ADR:** none — a choice about this feature's process

## D7 — Seen is recorded when the tour starts, not when it ends

"Once it has played" could mean once it started or once it ended. A visitor who navigates away
mid-tour has been shown it, and recording at the start leaves no path (a closed tab, a link
followed from inside a step) where the tour plays again. It also means nothing depends on the
tour reporting how it ended.

**ADR:** none — a behaviour fixed by the specification (FR-002)

## D8 — Seen belongs to the tour, not the address

The issue speaks of "a page's tour", and a tour belongs to a page in the sense of the view that
renders it (`CONTEXT.md`, Tour). Playing it again for every record would recreate the problem
the feature exists to fix.

**ADR:** none — a behaviour fixed by the specification (FR-004); how a tour is identified is D14

## D9 — Blocked or full storage: the tour plays as it would without this feature

The alternative, never playing, leaves that visitor with no tour at all unless the site has
placed a replay control. Article XIII requires the page to stay usable either way.

**ADR:** none — a behaviour fixed by the specification (FR-006)

## D10 — A tour that never started is not seen

Seen means it played (`CONTEXT.md`). A visitor who never saw it should see it once its elements
are there.

**ADR:** none — a behaviour fixed by the specification (US1 scenario 9)

## D11 — The replay control takes the site's own content and classes

Article XIV (no look of its own) and goal G7 (a site gives tours its own look). A control fixed
by the package could not sit in another design's navigation bar.

**ADR:** none — the constitution's Article XIV applied

## D12 — Replay restarts a playing tour

Two copies of a tour drawn over each other would make the page unusable (Article XIII).

**ADR:** none — a behaviour fixed by the specification (FR-009)

## D13 — One tour per page

A page has at most one tour, as issue #5 describes it, so the control starts that one. Nothing
in the issues or the roadmap asks for several tours on one page.

**ADR:** none — already stated in CONTEXT.md and the README

## D14 — A tour is identified by the view that declares it

Seen is kept in the browser under the dotted path of the view that declares the tour: the class
whose own body sets `tour`, or the function `@with_tour` decorates. A hash of the steps would
make an edited tour play again, which is R7's behaviour, and a name per tour would need a
setting the specification rules out. The cost: renaming or moving the view makes its tour unseen
again. Per-URL tours on one class (`as_view(tour=...)`) share that class's seen state.

**ADR:** docs/adr/0002-a-tour-is-seen-per-declaring-view.md

## D15 — Replay while a tour plays is reachable only through a step that points at the control

FS-001 D20: while a step shows, Driver.js's overlay covers the page and holds keyboard focus in
the popover and the step's element. The edge case "replay while playing restarts" is therefore
reachable only when a step points at the control, and the plan tests that case. Read against
FS-001 at the start of the build; not a change to the specification.

**ADR:** none — a consequence of FS-001 D20, recorded in research.md

## D16 — The replay control is an inert `<template>` turned into a button by the script

*Superseded by D19.*

`<template>` content is never shown and never in the accessibility tree, whatever the site's CSS
says, so with JavaScript off no control appears. The `hidden` attribute was turned down because
a site class such as `display: inline-flex` overrides it.

**ADR:** none — local to the control's markup, explained in research.md

## D17 — Argument names with `_` become attributes with `-`

*Superseded by D19: there are no tag arguments left.*

Template tag argument names cannot carry a hyphen, so `aria_label="…"` renders `aria-label` and
`data_x` renders `data-x`. Found at the design review.

**ADR:** none — local to the replay tag, documented in the developer guide

## D18 — FS-001's specification is edited to current state

Its FR-010 and its clarification on how often a tour plays said a tour plays every time its page
opens. This feature changes that, so both now read as they are.

**ADR:** none — a documentation edit carried with the behaviour change

## D19 — The replay control is the developer's own button

Issue #32. The `{% page_tour_replay %}` tag is removed. A replay control is a button the
developer writes with `data-page-tour-replay`, and placing it on the pages that have a tour is
the developer's job. On a page with a tour, the starter script gives each one a click handler
that calls `start()`, before autoplay, so a step can still point at it, and removes `hidden` if
the button carries it. A button in a template shared with pages that have no tour is written with
`hidden`: on those pages the script is not loaded, and with JavaScript off it does not run, so the
button stays hidden. `hidden` is that optional convenience, not part of what the package
requires. The package ships no CSS and writes no inline style for the control.

Content, classes, `aria-label`, `id`, `type` and several controls on one page become plain HTML
the developer writes, with nothing for the package to translate between.

**ADR:** none — local to the control's markup, recorded on issue #32
