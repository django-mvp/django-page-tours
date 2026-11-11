# Decisions — FS-005 Hints on a page

Readings taken where issue #40 was silent, while specifying. The feature comes from the prototype
recorded on issue #45; where the prototype or its hand-over (`PROTOTYPE.md` on branch
`prototype-hints-and-checklists`) settled a point, the reading follows it. Each is integrated into
`spec.md` and can be overruled.

## D1 — The issue's one paragraph is read as the prototype's hints page

Issue #40 says only that Driver.js has a hints API and the package should support it. The reading
is the hints page of the agreed prototype (`/hints/`): hints declared in Python, rendered with
`{{ hints }}`, dismissed for good in a browser, with a restore control. Nothing beyond what the
prototype shows is added.

**ADR:** none — a reading of the issue, fixed by the specification

## D2 — Three stories

Declaring hints (a developer), reading and dismissing them (a visitor) and styling them (a
developer or a design system) are three things people set out to do. Options, overrides from a
reusable app, version and the restore control's placement are scenarios of the first. Bringing
dismissed hints back is a scenario of the second: the visitor does it with the same hints, on the
same page. Styling is its own story because the person doing it is often a design system author
who never places a hint.

**ADR:** none — a reading of the issue, fixed by the specification

## D3 — The design rule from pull request #43 applies unchanged

Every class mirrors a Driver.js object, with fields named as Driver.js names them. The hints
configuration defaults to Driver.js's defaults. A hint and a beacon override it, so their fields
default to unset and are left out. No option values are checked. Function options are not
available. Text is passed as it is (FR-002 to FR-007). This is the maintainer's rule in the
hand-over, not a reading, and it is recorded here so the build does not reopen it.

**ADR:** none — follows the decision already taken for tours on pull request #43

## D4 — A hint without an identifier is remembered by its element

As in the prototype. The consequence, that two hints on one element share their dismissal, is an
edge case the documentation names (FR-011).

**ADR:** none — a behaviour fixed by the specification

## D5 — One namespace of names for tours and hints

A name is how `PAGE_TOURS_OVERRIDES` reaches a declaration, so a tour and hints under one name
would make an entry ambiguous. The system checks warn about it as one name declared twice, and an
override whose replacement is the wrong kind is refused (FR-009, FR-010). The name and the
replacement's kind are the package's own fields, so checking them is not a check of a Driver.js
option value.

**ADR:** none — a behaviour fixed by the specification

## D6 — Storage blocked shows the hints

As FS-002 decided for tours: a visitor who never gets a hint is worse off than one who sees it
again. A dismissal then lasts for the page view (FR-017).

**ADR:** none — follows FS-002's reading for tours

## D7 — Tours seen before this release are seen once more

What the browser remembers moves to one shape for every kind of declaration: a version and a list
of identifiers, under the declaration's name. Browsers holding the old shape for a tour see it
once more. The prototype took this and the hand-over asks for a changelog entry rather than a
conversion of the old records (FR-021). A tour seen once more is the gentlest failure the
package has, and the package is before 0.1.0, where nothing is stable (Article XI).

**ADR:** none — a behaviour fixed by the specification, stated in the changelog

## D8 — The beacon is a new part, the popover reuses the step's parts

As in the prototype. A hint's popover is the same Driver.js popover a step uses, so its parts are
the same parts. The beacon is new, and its configured classes come before the hint's own
`className` (FR-019).

**ADR:** none — a behaviour fixed by the specification

## D9 — A hint cannot start a tour

That needs Driver.js's `onButtonClick`, a function option, which the design rule leaves out. The
documentation states the limit (FR-007, US1 scenario 14).

**ADR:** none — follows the decision already taken for tours on pull request #43

## D10 — Goals and roadmap

No goal or roadmap item names hints. G1, G2 and G4 are worded for tours, and hints serve each of
them on the same terms, so the specification cites them. The roadmap has no item for hints, which
is a gap for the roadmap to close, not a reason to hold the feature.

**ADR:** none — traceability note

## D11 — The common base of what a page renders is not called "Guide"

CONTEXT.md lists "guide" as a word to avoid for a tour, and the prototype names the base that a
tour, hints and a checklist share `Guide`. The base takes another name. Research picks one from
CONTEXT.md's vocabulary, or adds a term to CONTEXT.md for the thing a page renders, and the
specification's text stays as it is because it never uses the word.

**ADR:** none — passed to research

## D12 — Whether Driver.js hides the beacons during a tour is settled from its code

FR-015 asks that no beacon shows over a playing tour. Research verifies against the vendored
Driver.js 1.11.0 hints build whether it hides the beacons itself or only closes an open hint. If it
only closes the hint, the package meets FR-015 itself.

**ADR:** none — passed to research

## D13 — Every declaration class is keyword-only

`Declaration` gives `version` a default ahead of the subclass fields that have none (`steps`,
`hints`), which a dataclass allows only when the fields are keyword-only. Every class is
keyword-only, as in the prototype. Every tour in the docs, the demo and the tests is declared with
keywords, so FR-021 holds for them. A step or tour written with positional arguments stops
working, and the changelog says so. Taken at research.

**ADR:** none — follows from the shared base, stated in the changelog

## D14 — Tours and hints share one base, one namespace of names and one browser record

`Declaration` is what a page renders. It owns the name, the version, the registry of declared
names, `PAGE_TOURS_OVERRIDES`, the payload and its element `page-tours-<kind>`. In the browser one
function keeps what a visitor did as a version and a list of ids under the declaration's name.
The checklist (FS-006) is its third kind. Taken at research, from the hand-over.

**ADR:** to graduate at converge — it binds every later kind of declaration

## D15 — The base is named `Declaration` (answers D11)

`CONTEXT.md` already says a tour is declared when it is made, and the specification calls a tour
or a set of hints a declaration (FR-009, D5, D7). The word is the repo's own and avoids "guide".
`CONTEXT.md` gains the term. Taken at research.

**ADR:** none — a name, recorded in `CONTEXT.md`

## D16 — Driver.js hides the beacons during a tour (answers D12)

`hints.css` hides `.driver-hint` under `.driver-active`, the class Driver.js puts on the body while
a tour plays. The package imports `hints.css` into its stylesheet's lowest layer and adds no code
for FR-015. A browser test asserts it. Taken at research.

**ADR:** none — Driver.js's behaviour, asserted by a test

## D17 — An override's replacement must be of the original's class

At start-up a replacement must be a declaration, because the original may not be imported yet.
When the original renders, the replacement must be of its class, or rendering raises
`ImproperlyConfigured` naming the entry (FR-010). Taken at research.

**ADR:** none — a behaviour fixed by the specification

## D18 — A beacon keeps the hints' class when the hint sets none

The prototype put the beacon part's classes and the hint's own class on each hint's beacon, which
replaced the hints' beacon class for a hint that set none. The rebuild writes the part's classes,
then the hint's class, else the hints' class (FR-019). Taken at research.

**ADR:** none — a defect of the prototype, not a design change

## D19 — A tour step points at a hint's element, not at its beacon (US1 scenario 11)

The approved scenario said a tour step can point at an element the hints have drawn. Driver.js
hides every beacon while a tour plays, which FR-015 requires, so a step pointing at a beacon finds
it hidden and is skipped. The two cannot both hold. The scenario now reads "an element a hint is
about", which keeps FR-015 and what the prototype's tour does (its step points at the figures
table a hint is about). Found at the design review; the specification is edited, and the edit is
put to the specification gate.

**ADR:** none — a correction of the specification, re-gated

## D20 — Design review outcome

One review, verdict request changes: one high, five medium, two low, each verified against the
cited code.

- A step's empty `element` reached Driver.js, which throws on it: the script drops a falsy
  `element` (plan.md, the tour; T004).
- A step with no popover fields lost its `popover`, which Driver.js needs: `as_driver()` always
  creates the inner objects (plan.md, the shared bases; T001).
- The build draws one beacon per id, so a key of the element would hide the second of two hints on
  one element: the key is worked out in the script, and the build's id is left alone (plan.md,
  the hints; T012).
- US1 scenario 11 contradicted FR-015: corrected in the specification (D19).
- `page-tours.css` holds the import and nothing else (plan.md).
- The two seen-record tests replaced under FR-021 are named in T004, and ADR 0006's stored value
  is marked superseded by the new ADR.
- Dismissal and the restore click move from T009 to T012, so they are built test-first with their
  tests.
- Not adopted: a test that no function option is a field (US1 scenario 14). It could fail only if
  someone added such a field on purpose, which makes it a change detector under the testing
  standard. The hints page documents the options left out (T011).

**ADR:** none — review outcome, recorded

D19 was passed at the specification gate on 2026-11-11.

## D21 — A declaration's payload takes the name it plays under

`Declaration.payload(name, version)` takes the name as well as the version, so a replacement from
`PAGE_TOURS_OVERRIDES` renders under the original's name without a second declaration being made
(which would record itself under that name). Taken while building the shared bases.

**ADR:** none — a signature inside the base, covered by D14's ADR
