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

The feature adds three terms to the glossary: *checklist*, *checklist item* and *ticked*, as
defined in the specification's Key Entities. They go into `CONTEXT.md` in the build.

**ADR:** none
