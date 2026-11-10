# Decisions — FS-004 Tours shipped by reusable apps

Readings taken where issue #23 was silent, while specifying. Each is integrated into `spec.md`
and can be overruled.

## D1 — An app author's side needs nothing new

A reusable app already declares tours on its views the way a project does, and they play in any
project that places the tour tag in the template the app's pages render through. That was run on
this repository before specifying (`research.md`, "Assumptions checked"). So the feature has one
story, for the developer of the installing project, and the app author's part is a requirement
(FR-001, FR-007) and a documentation page (FR-011), not a story of its own.

**ADR:** none — a reading of the issue, fixed by the specification

## D2 — A project replaces a whole tour, never one step

Steps have no names, and giving them names would be a setting every app author has to keep
stable. A replacement may reuse the app's steps, which are ordinary Python values, so rewording
one step costs one line more than a step-level change would (FR-004).

**ADR:** none — a behaviour fixed by the specification

## D3 — A project names an app's tour by the view that declares it

That is already the tour's name for remembering that it was seen (ADR 0002), and the documentation
already tells developers that renaming or moving the view makes it a different tour. Using it
means the app author gives no name and the app needs no change (FR-007). The cost is that an app
release that moves the view orphans the project's change, which is why FR-009 reports it.

**ADR:** docs/adr/0004-a-project-changes-an-installed-apps-tour-by-its-name.md

## D4 — A replacement keeps the tour's identity

A visitor who has seen the app's tour does not see the project's replacement play by itself, and
turning a tour off and on again does not reset anyone (FR-008). This matches an edited tour on the
developer's own view, which also does not play again (ADR 0002). A project that wants its
replacement shown again uses whatever the tour version feature provides.

**Meeting point with issue #21.** Issue #21 lets a developer mark a tour as a new version so that
people who saw the old one see it again, and is being built as a story in specification 002. This
feature takes none of that scope. It requires only that a replacement can carry anything a tour on
the developer's own view can carry (FR-004), so a version marker that #21 puts on a tour can be
put on a replacement. How an app's version and the project's replacement interact (for example, an
app release that marks its own tour as a new version while the project has replaced it) is settled
when this feature is planned against what #21 delivers. The reading to start from: the project's
replacement stands, and only a version on the replacement brings it back.

**ADR:** none — the behaviour is fixed by the specification; the version interaction is planning

## D5 — A change names one tour

Turning off every tour of one app at once was considered and left out: it is a convenience over
naming each tour, and the package keeps its settings few (README, "When a choice is close").
Nothing here stops it being added later (FR-006).

**ADR:** none — a scope decision

## D6 — A stale change is reported by Django's `check`

An app release that renames a view would otherwise turn the project's choice back into the app's
tour with no sign. The package already reports a missing setup through `check`
(`page_tours.W001`), so a stale change is reported the same way (FR-009).

**ADR:** none — a behaviour fixed by the specification

## D7 — A mistaken replacement fails at start-up

A tour with no steps or a step with no title already raises when it is declared, so a mistake
never reaches a visitor. A replacement is held to the same rule (FR-010).

**ADR:** none — follows the existing rule

## D8 — The change lives in the project, by code or settings

The issue requires no edit to the app's code. Whether the project's change is a setting or a call
in its own code is left to planning, which weighs it against the README's "fewer settings beat
more" (FR-002).

**ADR:** none — settled by D11, which graduated

## D9 — Meeting point with issue #22

Issue #22 gives a site's tours its own look. A replacement is an ordinary tour, so it gets the
site's look exactly as any other tour does. This feature changes nothing about how tours look.

**ADR:** none — a scope boundary, nothing is built for it

## D10 — Glossary

`CONTEXT.md` has no word for the name a tour is known by, or for a project's change to an app's
tour. The build adds the terms it ends up using; the specification uses "an app's tour" and "a
project's change" in the meaning given under Key Entities. The build added **Tour name** and
**Tour override** to `CONTEXT.md`.

**ADR:** none — vocabulary, recorded in `CONTEXT.md`

## Sketch gate

`none`: the feature puts nothing new in front of a visitor. A replaced tour is drawn exactly as
any tour is.

## D11 — The project's change is one setting, `PAGE_TOURS_OVERRIDES`

It maps a tour's name to the dotted path of a replacement, or to `None` to turn the tour off,
the same shape as Django's `MIGRATION_MODULES`. A registry filled from the project's code was
weighed and left out: it needs a place and an order to be called from, and a test has to reset
it. The replacement is named by a path because a replacement that reuses the app's steps imports
the app's views, which settings cannot (`research.md`, "Where the project's change lives").
Settles D8.

**ADR:** docs/adr/0004-a-project-changes-an-installed-apps-tour-by-its-name.md

## D12 — A replacement's version counts on from the app tour's

A replaced tour plays at the app tour's version plus the replacement's, less one. A replacement
left at version 1 therefore plays at the app tour's version, so nobody who saw the app's tour
sees it by itself (FR-008, scenario 9), and raising the replacement's version shows it again.
Emitting the replacement's own version was the first reading and was dropped at design review: an
app tour at version 2 stores `"2"`, so a replacement at 1 would play once for everyone who saw it,
against FR-008. Emitting only the app's version was dropped too: a project could never show its
own replacement again, against FR-004. The cost is D4's starting reading: an app release that
raises its own tour's version shows the project's replacement again once. The app's author said
the page changed enough, so that is the safer side to err on. Settles D4's open question.

**ADR:** docs/adr/0004-a-project-changes-an-installed-apps-tour-by-its-name.md

## D15 — The naming rule is stated once

`tour_id` and the check both name a class-based view's tour through `declaring_view_name`, so the
check cannot disagree with what the browser is sent. Design review found the plan's restatement
named `Sub.as_view(tour=...)` differently from `tour_id` when a parent class sets `tour = None`.

**ADR:** none — local to this feature, nothing downstream inherits it

## D13 — Every replacement is imported when the project starts

`PageToursConfig.ready` resolves every path in the setting, so a path that does not import, a
path that names something other than a tour, and a replacement that is not a valid tour all fail
when the project starts, never on a visitor's page (FR-010). The lookup on each page reads the
setting again, so a test that changes it sees the change at once.

**ADR:** none — follows D7 and the existing rule

## D14 — The stale-change check walks the URLconf

`page_tours.W002` lists the tour names of every view the root URLconf routes, by the rule
`tour_id` applies, and warns once per name in the setting that is not among them. A tour declared
on a view no URL routes cannot play, so a change naming it is stale in the same sense. `with_tour`
records its name on the wrapper so a function-based view's tour is found without calling it.

**ADR:** none — local to this feature, nothing downstream inherits it
