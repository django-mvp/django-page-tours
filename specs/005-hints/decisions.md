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
