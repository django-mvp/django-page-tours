# Feature Specification: A site's own look for its tours

**Feature Branch**: `003-a-sites-own-look`

**Created**: 2026-11-10

**Status**: Draft

**Serves**: G7 (a site gives tours its own look, and a design system can style them for every site
built on it). Roadmap: R5.

**Input**: Issue #22, "Give a site's tours its own look". A site with a design of its own wants
its tours to look like the rest of it: its colours, type, spacing and buttons, not Driver.js's
defaults. Today the only ways to get there are to override the package's template or to write CSS
against Driver.js's internal class names, which can change with any Driver.js release. A developer
should be able to give a site's tours its own look with the site's own CSS. A design system built
on Django should be able to style tours once, so that every site built on it gets that look
without each site doing the work again. The package itself still ships no design of its own.

**Builds on**: issue #5 (a tour declared in Python and played when its page opens) and issue #6
(seen tours and the replay control). The replay control already takes the site's own content and
classes, so it is not part of this feature.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A developer styles a site's tours with the site's own CSS (Priority: P1)

A developer whose site has its own design makes its tours match it. Every part of a step as it is
shown has a name the package documents: the box the step is shown in, its title, its text, its
progress, its previous, next and done controls, its close control, and the highlight around the
step's element. The developer writes rules against those names in the site's own stylesheet, or
gives the parts the site's own classes in the project's configuration, for example the classes the
site's buttons already use. The documented names do not change when the package moves to a new
Driver.js release. The developer overrides none of the package's templates and writes nothing
against Driver.js's own class names.

**Why this priority**: it is the reason the feature exists. Without it, a site's tours look like
Driver.js's demo, or stay styled only until the next Driver.js release.

**Independent Test**: on a page with a tour, add a rule against one documented name to the site's
stylesheet and give one part a class through configuration; play the tour and confirm both take
effect on the parts they name and on no other part.

**Acceptance Scenarios**:

1. **Given** a page with a tour, **When** a step is shown, **Then** each part of the step listed
   above carries its documented name.
2. **Given** a rule in the site's stylesheet against a documented name, with selector specificity
   no higher than the default rule it replaces, **When** a step is shown, **Then** the site's rule
   takes effect, whether the site links its stylesheet before or after the package's.
3. **Given** a developer gives a part one or more classes in the project's configuration, **When**
   a step is shown, **Then** that part carries those classes on every step of every tour on the
   site, and no other part carries them.
4. **Given** a step attached to no element, shown in the middle of the page, **When** it is shown,
   **Then** its parts carry the same names and configured classes as a step attached to an
   element.
5. **Given** the first step, the last step, or a step in between, each of which offers a
   different set of controls, **When** it is shown, **Then** every control on it carries its
   documented name and configured classes, including a control shown as unavailable.
6. **Given** a developer gives the controls their own classes, **When** a visitor steps through
   the tour, **Then** the controls keep their accessible names and work with the keyboard exactly
   as they did without the classes.
7. **Given** no configuration, **When** a page with a tour renders, **Then** the package's only
   stylesheet is Driver.js's, the markup carries no class from any CSS framework, and the tour
   plays as it does today.
8. **Given** a configured class value containing characters that are special in HTML, **When** a
   step is shown, **Then** the value cannot change the markup it is written into.
9. **Given** the configuration names a part the package does not have, or gives a part something
   other than class names, **When** the project starts, **Then** Django's system checks report it,
   naming the part, and pages with a tour still render.
10. **Given** a page with no tour, **When** it renders, **Then** nothing this feature adds appears
    on it.

---

### User Story 2 - A design-system author styles tours once for every site built on it (Priority: P2)

The author of a design system built on Django, distributed as a reusable app, gives tours that
design system's look in the design system itself: rules against the documented names in its own
stylesheet, and classes for the parts supplied as the design system's defaults. A site built on
the design system installs it and its tours look like the rest of that site, with no tour styling
of its own to write or configure. A site that wants something different for one part changes just
that part in its own configuration, and the design system's choices for the other parts stay.

**Why this priority**: it multiplies the first story across every site on one design system. It
depends on the first story's names and classes, so it comes second.

**Independent Test**: install a reusable app that supplies classes for the parts and a stylesheet
against the documented names into a project with no tour styling of its own; play a tour and
confirm the parts carry the app's classes and the app's rules take effect. Then give one part a
class in the project's configuration and confirm that part takes the project's classes while the
others keep the app's.

**Acceptance Scenarios**:

1. **Given** an installed design system that supplies classes for the parts, and a project that
   configures none, **When** a step is shown, **Then** the parts carry the design system's
   classes.
2. **Given** an installed design system whose stylesheet has rules against the documented names,
   loaded by the design system's own base template, **When** a step is shown, **Then** those rules
   take effect with nothing configured in the project.
3. **Given** a design system supplies classes for a part and the project configures classes for
   the same part, **When** a step is shown, **Then** that part carries the project's classes in
   place of the design system's, and every other part keeps the design system's.
4. **Given** a project that configures nothing and installs no design system, **When** a step is
   shown, **Then** the tour is exactly as User Story 1 scenario 7 describes.
5. **Given** a design system supplies a part the package does not have, **When** the project
   starts, **Then** Django's system checks report it, naming the part and the app that supplied
   it.

---

### Edge Cases

- A step's element sits inside a region with its own stacking or overflow, so the highlight is
  drawn around it: the highlight carries its documented name and classes like any other part.
- A tour restarted from the replay control is shown with the same names and classes as when it
  played by itself.
- A failure while giving a part its classes ends the tour and leaves the page as it was, as any
  other failure in the tour does (Article XIII).
- Two installed apps both supply classes for the parts: the one listed first in the project's
  installed apps wins for each part it supplies, as Django resolves templates and static files.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Each part of a shown step (the box, title, text, progress, previous control, next
  control, done control, close control) and the highlight around the step's element MUST carry a
  name the package documents. (US1)
- **FR-002**: The documented names MUST be part of the package's public surface under Article XI:
  they do not change when the package moves to a new Driver.js release, and renaming or removing
  one is a major version. (US1)
- **FR-003**: A rule in a site's stylesheet against a documented name, with specificity no higher
  than the default rule it replaces, MUST take effect over Driver.js's default styling, whichever
  order the stylesheets are linked in. (US1, US2)
- **FR-004**: A developer MUST be able to give each part its own classes in the project's
  configuration, applied to that part on every step of every tour on the site, without overriding
  any of the package's templates. (US1)
- **FR-005**: Classes given to a part MUST NOT change the accessible names, focus order or
  keyboard behaviour of the tour's controls. (US1)
- **FR-006**: With no configuration and no design system installed, the package's only stylesheet
  MUST remain Driver.js's, and the markup it emits MUST carry no class from any CSS framework
  (Article XIV). (US1, US2)
- **FR-007**: Configured class values MUST be written into the page so that they cannot change the
  markup around them (Article V). (US1)
- **FR-008**: A configured or supplied part the package does not have, or a value that is not
  class names, MUST be reported by Django's system checks, naming the part and where it came from,
  and MUST NOT stop a page with a tour from rendering. (US1, US2)
- **FR-009**: A reusable app MUST be able to supply classes for the parts as defaults, which apply
  in every project that installs it with nothing configured in the project. (US2)
- **FR-010**: Classes the project configures for a part MUST replace those an installed app
  supplies for the same part, and leave the app's classes for every other part in place. When
  several installed apps supply the same part, the first in the project's installed apps MUST win.
  (US2)
- **FR-011**: The names and classes MUST apply the same way to a step attached to an element, a
  step attached to none, and a tour started from the replay control. (US1)
- **FR-012**: The documentation site MUST list the documented names and describe how to style
  tours from a site's stylesheet, how to give parts classes in configuration, and how a design
  system supplies its defaults. The demo project MUST show a tour given a look of its own. (US1,
  US2)

### Key Entities

- **Part of a step**: one named piece of a step as it is shown — the box, title, text, progress,
  a control, or the highlight. Each has a documented name.
- **Tour styling configuration**: the classes given to each part, from the project's settings or
  supplied as defaults by an installed app.

## Clarifications

### Session 2026-11-10

- Q: Is the look of a tour set for the whole site, or per tour or per step? → A: For the whole
  site. A site's tours share its design, and the issue asks for nothing finer. Integrated into
  FR-004 and US1 scenario 3.
- Q: Does a site's CSS have to out-rank Driver.js's rules with heavier selectors? → A: No. A rule
  as specific as the default it replaces wins, wherever the site's stylesheet is linked, so a
  site's ordinary CSS works without tricks. Integrated into FR-003 and US1 scenario 2.
- Q: Can a site turn off Driver.js's stylesheet altogether? → A: No. It also places the step and
  draws the highlight, so it always loads, and the site's rules sit on top of it. Recorded under
  Assumptions.
- Q: How does a design system reach every site built on it? → A: By being installed. Its
  stylesheet is already loaded by its own base template, so its rules against the documented names
  need nothing more, and its classes for the parts are defaults that a project's own configuration
  replaces part by part. Integrated into FR-009, FR-010 and US2.
- Q: What happens when the configuration is wrong? → A: Django's system checks report it at start,
  and pages still render, so a mistake in styling never breaks a page. Integrated into FR-008.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A developer gives every part of a tour the site's own look with no override of the
  package's templates and no selector against Driver.js's class names.
- **SC-002**: A site styled against the documented names keeps its look across a move of the
  package to a new Driver.js release within the same major version of the package.
- **SC-003**: A site built on a design system that styles tours carries no tour-styling CSS or
  configuration of its own, and its tours take the design system's look.
- **SC-004**: With nothing configured and no design system installed, the package's emitted markup
  carries no CSS-framework class and its only stylesheet is Driver.js's.
- **SC-005**: No styling mistake in configuration stops a page with a tour from rendering.

## Assumptions

- The replay control is out of scope: it already takes the site's own content and classes (issue
  #6).
- Driver.js's stylesheet always loads, because it places the step and draws the highlight. A
  site's look is laid over it, never instead of it.
- The text of a step and its controls is not part of this feature. What a step says is declared
  with the tour, and the controls' labels are translated by the package.
- Styling a single tour or a single step differently from the rest of the site is out of scope.
- A design system is a reusable Django app that the project installs. Tours shipped by reusable
  apps for their own pages are issue #23, and changing when a tour plays again after it changes is
  issue #21. Neither is part of this feature.
- The package ships no design of its own. The demo's restyled tour demonstrates the feature and is
  not a design the package offers.
