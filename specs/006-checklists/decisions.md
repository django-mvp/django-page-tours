# Decisions — FS-006 A checklist

Readings taken where issue #39 was silent, while specifying. Issue #39 is one line, so the reading
comes from the prototype on branch `prototype-hints-and-checklists` (issue #45), whose checklist
screens and recorded decisions are agreed. Each reading is integrated into `spec.md` and can be
overruled.

## D1 — The feature, as specified

A developer declares a checklist in Python, `Checklist(name=…, items=[ChecklistItem(…)], …)`, puts
it in the template context of the pages it belongs on, and the base template outputs it with
`{{ checklist }}`. Each item starts a tour, follows a link, or is done in the app, which the
developer's own code reports per request. A visitor works through it in any order, and their
ticks are kept in the browser under the checklist's name and version. Hints (issue #40) and the
shared base classes, what the browser remembers and the entry point that plays every kind of
guide are FS-005's, and this feature uses them.

**ADR:** none — the agreed reading of the issue

## D2 — Two stories, one per person

What the developer declares and what the visitor does are separate stories. Every option, item
kind, the toggle control, overrides, styling and the system check are scenarios of the developer's
story, because nobody sets out to do any of them on their own.

**ADR:** none — a reading of the issue

## D3 — What the app knows is reported on the checklist, per request

Driver.js decides an item from the app with `completeWhen`, a JavaScript function, and functions
are not available. In its place the developer sets the checklist's completed items for each
request from what the app knows, as the prototype's demo does with `dataclasses.replace`. The app's
report wins over the browser: an item it reports is ticked on every request it is reported on
(clarification 2).

**ADR:** none — the prototype's decision, recorded on issue #45

## D4 — A tour started from a checklist counts as seen; only finishing it ticks the item

The package's rule for seen is that a tour is seen once it has played, finished or not. The
checklist keeps that rule, so one tour has one record wherever it plays. Finishing is what ticks
the item, which is Driver.js's own behaviour.

**ADR:** none — follows from the existing definition of seen

## D5 — Overrides reach a checklist and an item's tour

The prototype did not look an item's tour up in `PAGE_TOURS_OVERRIDES`, and its hand-over lists
that as faked. A project that changes an app's tour expects the change wherever the tour plays, so
an item's tour is looked up under its name. An item whose tour the project turned off is left out,
since it would start nothing. A checklist itself is replaced or turned off under its name, through
the shared base FS-005 builds.

**ADR:** none — the hand-over names this as the checklist's to do properly

## D6 — Raising the version forgets the browser's ticks only

A raised version is the developer saying visitors should work through the checklist again. What
the app reports is still true of the visitor, so those items stay ticked.

**ADR:** none — follows from the tour version rule (ADR 0003)

## D7 — The README's scope changes

The README's "What it deliberately is not" lists "not a getting-started checklist". Issue #39,
filed by the maintainer, reverses that, so FR-017 has the scope include checklists. The rest of
that section, no store of progress per account and no tours across several pages, holds for
checklists too.

**ADR:** none — the README follows the accepted issue

## D8 — No roadmap item

`docs/ROADMAP.md` has no item for checklists, and GOALS.md names none. The specification cites
the tour goals a checklist is held to (G1, G4, G6 to G9). Adding a roadmap entry is left to the
roadmap's own revision.

**ADR:** none

## D9 — New terms for CONTEXT.md

The feature adds four terms to the glossary: *checklist*, *checklist item* and *ticked*, as
defined in the specification's Key Entities, and *toggle control* (D16). They go into `CONTEXT.md` in the build.

**ADR:** none

## D10 — The override lookup moves into `Declaration.playing()`

`Declaration.__html__` looks a declaration up in `PAGE_TOURS_OVERRIDES` inline. A checklist item's
tour needs the same lookup without rendering the tour, so the lookup moves, unchanged, into
`playing()`, which returns the declaration that plays under the name and its version, or `None`
when turned off. `__html__` calls it, and so does the checklist for each item's tour.

**ADR:** none — a method extracted from ADR 0004's rule, which it does not change

## D11 — An item's tour reaches the browser as a tour's own payload

`ChecklistItem.tour` is a package field. `Checklist.as_driver()` puts the played tour's
`payload(name, version)` in its place, so the script builds an item's tour from exactly what it
builds a page's own tour from, under the tour's own name and version. An item whose tour is turned
off is left out of the items.

**ADR:** none — follows from D5 and the shared tour builder (D15)

## D12 — The browser keeps its own ticks, never the app's

The script stores the ticked ids the app did not report for this request, plus the ids already
stored that are still ticked, and shows the app's report followed by the stored ticks. Keeping
what was already stored means a tick the visitor made before the app reported the item survives
a later tick (design review SPEC-001). An item the app stops reporting is then unticked unless
the visitor ticked it in the browser, as the Edge Cases say, and unticking an item the app reports
lasts only until the next request, as clarification 2 says.

**ADR:** none — local to the checklist's script

## D13 — `completed` is the field the app reports through

Driver.js takes the items already done as `completed`, so the field has that name and reaches
Driver.js as it is. W005 compares a checklist's items, never `completed`, so a checklist made per
request with what the app knows is the same checklist as the one declared.

**ADR:** none — the design rule applied to one option

## D14 — The checklist's part classes are added once, after it is shown

Driver.js's checklist build makes its whole widget in `show()` and afterwards only changes text and
classes inside it, so classes added once stay. No event hook is needed, unlike the prototype's.

**ADR:** none — local to the checklist's script

## D15 — One function builds a tour in the browser, wherever it is started

`buildTour(payload, driver)` is cut out of `playTour` and returns `start()` and `instance()`.
The Driver.js instance is made on first use, after the showable check, so a tour with nothing to
show never asks Driver.js for anything (design review ARCH-001); its `drive` is the package's
start. The page's own tour and a checklist item's tour are built by it,
so a tour finds its elements, carries its part classes, cleans up and is recorded as seen the same
way wherever it plays (SC-003). Driver.js's checklist drives the instance it is given.

**ADR:** decided at converge

## D16 — The toggle control follows the replay and restore controls

A control carrying `data-page-checklist-toggle` is the developer's own element, written `hidden`,
and the script shows it and makes it open and close the checklist when a checklist plays. It
works with or without a launcher.

**ADR:** none — the existing control pattern

## D17 — A replaced checklist plays with its own `completed`

`PAGE_TOURS_OVERRIDES` swaps the whole declaration, so a replacement checklist plays with the
`completed` it was declared with, and what the app reported for the original does not carry
over. The specification is silent on it. A project that replaces an app's checklist and wants
the app's report sets `completed` on its own replacement in its own context processor. Carrying
the report across would be a change to the specification. Pinned by a test in T002.

**ADR:** none — follows from ADR 0004's rule that a replacement takes the declaration's place

## D18 — An item tour with nothing to show leaves the checklist closed

Driver.js closes the panel before it drives an item's tour, and reopens it only when the tour
ends. A tour with nothing to show does not start, so the panel stays closed and the item stays
unticked, as the Edge Cases ask. Reopening it would be one call to the checklist's `open()`;
it is not built, since the specification does not ask for it. Watch item for the build
(design review ARCH-003).

**ADR:** none — local to the checklist's script

## D19 — The design review

One review of the plan, three lenses. One verified high finding, applied as a plan edit: the
tour's Driver.js instance is made on first use (ARCH-001, D15). Medium findings applied: the tick
storage keeps earlier ticks (SPEC-001, D12), a replaced checklist's `completed` recorded and
pinned (SPEC-002, D17), the demo's borrow form carries the CSRF token and its test enforces it
(SEC-001). Low findings applied: `isSeen()` dropped (ARCH-002), "any order" tested (SPEC-003),
and the closed panel recorded (ARCH-003, D18). US2 is built after US1, on its result, because both
edit `playChecklist`.

**ADR:** none — a record of the review
