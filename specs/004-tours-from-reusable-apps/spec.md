# Feature Specification: Tours shipped by reusable apps

**Feature Branch**: `004-tours-from-reusable-apps`

**Created**: 2026-11-10

**Status**: Draft

**Serves**: G8 (a reusable app ships tours for its own pages, which a project can change or turn
off without editing the app). Roadmap: R6.

**Input**: Issue #23, "Tours shipped by reusable apps". The author of a reusable Django app wants
to ship tours for the app's own pages, so that every project installing the app gets them. The
project installing it then needs a say. It may want to reword a step to match its own vocabulary,
point a step at a different element because it overrode one of the app's templates, or turn a
tour off because it does not suit its users. Today a tour is an attribute of the view, so the only
way to change one is to subclass or edit the app's view and route to that instead. A project
should be able to change or turn off a tour shipped by an installed app without touching the
app's code.

**Builds on**: issue #5 (a tour declared in Python on the view that renders its page) and issue #6
(a tour is seen once per browser, remembered under the view that declares it).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A project developer changes or turns off a tour shipped by an installed app (Priority: P1)

A developer builds a project on a reusable app that declares tours for its own pages, the way any
developer declares a tour today. Those tours play in the project with nothing more than the setup
every project already does for its own tours. The developer decides one of them does not fit
their project. They give it a replacement of their own, with their own wording, steps or elements,
or they turn it off. They do this in their own project, without editing the app, subclassing its
view or routing a page to a view of their own. Every page the app's view renders then shows the
project's choice. If a later release of the app stops declaring that tour, the project is told
rather than left with a change that quietly no longer applies.

**Why this priority**: it is the whole feature. An app author can already declare tours on the
app's views; what is missing is the installing project's say over them.

**Independent Test**: in a project that installs an app whose view declares a tour, open the
app's page and see the app's tour; give the project a replacement and see the replacement there
instead; turn the tour off and see the page with no tour and no replay control; confirm the app's
files are unchanged throughout.

**Acceptance Scenarios**:

1. **Given** an installed app whose view declares a tour, and a project that has made no change to
   it, **When** a visitor opens the app's page, **Then** the app's tour plays as it would on one
   of the project's own pages.
2. **Given** the project has given the app's tour a replacement, **When** a visitor opens the
   app's page, **Then** the replacement plays and the app's own tour does not.
3. **Given** the project's replacement reuses the app's steps with one of them reworded or
   pointed at a different element, **When** a visitor opens the app's page, **Then** the tour
   plays the app's steps in order with that one step as the project wrote it.
4. **Given** the project has turned the app's tour off, **When** a visitor opens the app's page,
   **Then** the page renders as a page with no tour: no tour plays, nothing of the tour is
   emitted, and a replay control placed on the page is not shown.
5. **Given** the app's view serves many addresses, **When** the project changes or turns off its
   tour, **Then** the change holds on every address the view serves.
6. **Given** the project routes a page to its own subclass of the app's view, and the subclass
   does not set a tour of its own, **When** a visitor opens that page, **Then** the project's
   change to the app's tour applies there too.
7. **Given** the app's tour is declared on a function-based view, **When** the project changes or
   turns it off, **Then** the change applies exactly as it does for a class-based view.
8. **Given** the project's replacement marks the tour to play only from the replay control,
   **When** a visitor opens the app's page, **Then** the tour does not play by itself and the
   replay control plays it.
9. **Given** a visitor has already seen the app's tour in their browser, **When** the project
   gives it a replacement, or turns it off and later on again, **Then** the tour does not play by
   itself for that visitor, and the replay control still plays it.
10. **Given** the project has changed or turned off a tour, **When** a later release of the app no
    longer declares any tour under that name and Django's `check` command runs, **Then** the check
    reports that the project's change names no tour, saying which one.
11. **Given** the project changes one of an app's tours, **When** a visitor opens the app's other
    pages, **Then** their tours play as the app declared them.

### Edge Cases

- The app renames or moves the view that declares a tour. The tour has a new name, so the
  project's change no longer applies to it, the app's tour plays again once to everyone who saw
  it (as ADR 0002 already records for a renamed view), and the check in scenario 10 reports the
  stale change.
- The project subclasses the app's view and sets a tour on the subclass. That tour is the
  project's own, declared on the project's own view, and a change to the app's tour does not
  touch it.
- The project's replacement is not a valid tour (no steps, a step with no title). It is refused
  with the same error a developer gets for that mistake on their own view, when the project
  starts, never on a visitor's page.
- The app's page does not render the project's base template, or a template with the tour tag in
  it. Then no tour of the app plays in the project, with or without a change. That is the existing
  setup requirement, not something this feature changes.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: A tour declared on a view of any installed app MUST play in a project that has done
  the tour setup it already does for its own pages, with no setting for that app. (US1)
- **FR-002**: A project developer MUST be able to replace the tour declared on an installed app's
  view with a tour of their own, from the project's own code or settings, without editing the
  app, subclassing its view or routing to a different view. (US1)
- **FR-003**: A project developer MUST be able to turn off the tour declared on an installed app's
  view, from the same place. A page whose tour is turned off MUST render as a page with no tour.
  (US1)
- **FR-004**: A replacement MUST be able to carry anything a tour the developer declares on their
  own view can carry, and MUST be able to reuse the app's own steps. (US1)
- **FR-005**: A change MUST apply wherever the app's tour would have played: every address its
  view serves, and every subclass of that view that does not set a tour of its own. (US1)
- **FR-006**: A change MUST apply to one tour only, named by the project. Every other tour MUST
  play as declared. (US1)
- **FR-007**: The app MUST need no change to have its tours changed or turned off: the project
  names a tour without the app author having given it any name beyond the view that declares it.
  (US1)
- **FR-008**: A replacement MUST keep the identity of the tour it replaces, so a visitor who has
  seen the app's tour does not see the replacement play by itself, and turning a tour off and on
  again does not make it play again for anyone. (US1)
- **FR-009**: Django's `check` command MUST report a project's change that names no tour declared
  in the project, identifying the change. (US1)
- **FR-010**: A replacement that is not a valid tour MUST be refused when the project starts, with
  the error the same mistake on the developer's own view gives. (US1)
- **FR-011**: The documentation site MUST describe how an app author ships tours for the app's
  pages and how a project changes or turns them off, and the demo project MUST show a page whose
  app tour the project has changed and a page whose app tour the project has turned off. (US1)

### Key Entities

- **An app's tour**: a tour declared on a view of an installed reusable app. Named by the view
  that declares it, as every tour already is for remembering that it was seen.
- **A project's change**: the installing project's replacement for an app's tour, or its choice to
  turn that tour off. Made in the project, applied wherever the app's tour would play.

## Clarifications

### Session 2026-11-10

- Q: Does a project change a single step of an app's tour, or replace the whole tour? → A: It
  replaces the whole tour. Its replacement may reuse the app's steps, so rewording one step means
  a replacement made of the app's steps with that one changed. Steps have no names of their own to
  change them by. Integrated into FR-004 and scenario 3.
- Q: When a project replaces an app's tour, do visitors who saw the app's original see the
  replacement? → A: No, not by itself. The replacement keeps the tour's identity, in line with an
  edited tour on the developer's own view, which also does not play again. Showing a changed tour
  again on purpose belongs to tour versions (issue #21). Integrated into FR-008 and scenario 9.
- Q: Can a project turn off all of one app's tours at once? → A: No. A change names one tour.
  Turning off several is one change each. Integrated into FR-006.
- Q: What happens to a project's change when an app release renames the view it names? → A: The
  change stops applying and Django's `check` reports it, so it does not go unnoticed. Integrated
  into FR-009, scenario 10 and the edge cases.
- Q: Does a mistaken replacement fail on a visitor's page? → A: No, it is refused when the project
  starts, as a mistaken tour on the developer's own view already is. Integrated into FR-010.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A project changes or turns off a tour shipped by an installed app with no edit to
  any of the app's files, no subclass of its view and no change to the project's routing.
- **SC-002**: On every page an app's view renders, the project's change is what a visitor gets,
  and every tour the project did not change plays as the app declared it.
- **SC-003**: A project change that names no declared tour is reported by Django's `check`, before
  the project is deployed.
- **SC-004**: No visitor who has seen an app's tour is shown it by itself again because the project
  replaced it or turned it off and on.
- **SC-005**: An app author ships tours for the app's pages with no code beyond the tour
  declarations they would write in a project of their own.

## Assumptions

- A page has at most one tour, and a tour belongs to the view that declares it (ADR 0001).
- A tour is named by the view that declares it (ADR 0002). This feature uses that name for a
  project's change and adds no other.
- The project has placed the tour tag in the template the app's pages render through. The app's
  tours depend on the same setup as the project's own.
- Showing a changed tour again to people who saw the old one is issue #21 and out of scope.
  Whatever a tour declared on the developer's own view can carry for that, a replacement can
  carry too.
- A site's own look for its tours is issue #22 and out of scope. A replacement looks like any
  other tour on the site.
