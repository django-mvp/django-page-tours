# Feature Specification: A tour on a page

**Feature Branch**: `001-tour-on-a-page`

**Created**: 2026-11-06

**Status**: Draft

**Serves**: G1, G3, G4 (roadmap item R1)

**Input**: Issue #5, "Give a page a guided tour declared in Python".

## Summary

A developer gives one page of their site a short guided tour by declaring it in Python, beside
the view that renders the page, as an ordered list of tour steps. Each step has a title and a
short description, and is either attached to one element of the page or attached to nothing, which suits
an opening welcome. When a visitor opens the page, the tour plays: they can move forward and back
through the steps and close it at any point. The tour never makes the page less usable. A step
whose element is not on the page is skipped, a tour that fails leaves the page as it was, and with
JavaScript off the page renders as if it had no tour. Driver.js draws the tour and ships inside
the package, so nothing is loaded from another origin and no front-end build step is needed.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A developer gives a page a tour (Priority: P1)

A developer adds the package to their project once, then gives any page a tour by declaring it in
Python beside the view that renders that page. The tour is an ordered list of steps. Each step has
a title and a short description, and either names the element of the page it is attached to or is
attached to nothing. The developer writes no JavaScript and runs no front-end tooling. Step titles
and descriptions can be marked for translation like any other string in their project.

**Why this priority**: Without a way to declare a tour, there is nothing for a visitor to see.
This is the package's reason to exist (G1).

**Independent Test**: In a project with the package installed, declare a tour of three steps for
one view, open the page, and confirm the page carries that tour with its steps in the declared
order, with no JavaScript written by hand and no request to another origin.

**Acceptance Scenarios**:

1. **Given** a project with the package installed and set up, **When** a developer declares a
   tour for a view as an ordered list of steps, **Then** the page that view renders carries that
   tour, with the steps in the order declared.
2. **Given** a tour step that names an element of the page, **When** the page renders, **Then**
   the step is attached to that element.
3. **Given** a tour step that names no element, **When** the page renders, **Then** the step is
   attached to nothing and stands on its own.
4. **Given** a page whose view declares no tour, **When** the page renders, **Then** it carries no
   tour, and the package's scripts and stylesheet, which the base template includes on every
   page, change nothing on it.
5. **Given** a page with a tour, **When** it renders, **Then** every script and stylesheet the tour
   needs is served by the site itself, and none comes from another origin.
6. **Given** a step whose title and text are marked for translation, **When** the page is served
   in a language the project has a translation for, **Then** the step carries the translated title
   and description.
7. **Given** a step whose title or description contains HTML, **When** the page renders,
   **Then** the step carries it unchanged, and Driver.js shows it as HTML.
8. **Given** a tour declared with no name or no steps, **When** the
   project starts or the tour is declared, **Then** the developer is told what is wrong, before
   any visitor sees the page.
9. **Given** a view with a tour, **When** the page is opened by a signed-in visitor and by an
   anonymous one, **Then** both are given the same tour.

---

### User Story 2 - A visitor follows a page's tour (Priority: P1)

A visitor opens a page that has a tour, and the tour starts. Each step is shown in turn, the
element it is attached to highlighted beside it. The visitor moves forward and back through the
steps and can close the tour at any step. However the tour goes, the page underneath works exactly
as it would without one.

**Why this priority**: A declared tour is only worth anything when a visitor can follow it, and
G4 makes a page that still works the condition for showing one at all.

**Independent Test**: Open the demo page with a tour in a browser, step forward to the last step
and back to the first, close the tour part-way, and confirm that the element a step is attached
to works while that step shows, that the rest of the page is reached by closing the tour in one
action, and that every control the page offers works afterwards.

**Acceptance Scenarios**:

1. **Given** a page with a tour, **When** a visitor opens it, **Then** the tour plays from its
   first step.
2. **Given** a tour that is playing, **When** the visitor moves forward or back, **Then** the next
   or previous step is shown, in the declared order.
3. **Given** a tour that is playing, **When** the visitor closes it at any step, **Then** the tour
   ends and the page is as it was before the tour started.
4. **Given** a tour that is playing, **When** the visitor moves forward from the last step,
   **Then** the tour ends and the page is as it was before the tour started.
5. **Given** a step whose element is not on the page, **When** the tour reaches it, **Then** the
   step is skipped with no error shown, and the tour goes on to the next step it can show.
6. **Given** a tour none of whose steps can be shown, **When** the visitor opens the page,
   **Then** no tour plays and the page is unchanged.
7. **Given** a tour whose script fails while it is playing or starting, **When** the failure
   happens, **Then** the tour ends and the page is left usable, with nothing of the tour left in
   the way.
8. **Given** a page with a tour, **When** a visitor opens it with JavaScript turned off, **Then**
   the page renders as it would with no tour: nothing of the tour is visible and nothing on the
   page is hidden or moved.
9. **Given** a tour that is playing, **When** a visitor uses only the keyboard, **Then** they can
   move forward and back and close it, focus is inside each step as it shows, and when the tour
   ends, at any step and however it ends, focus is back where it was before the tour started.
10. **Given** a tour that is playing, **When** a step shows, **Then** a screen reader announces it
    as a dialog named by the step's title and described by its description.
11. **Given** a page served in a language the project has a translation for, **When** its tour
    plays, **Then** the tour's own controls (next, previous, done and the close button's name)
    are in that language.

---

### User Story 3 - A developer sets Driver.js options on the tour (Priority: P3)

A developer wants a tour to use something Driver.js already does, such as showing the step
count, turning the animation off or wording a button differently. The tour has a field for each
Driver.js configuration option that takes a plain value, named exactly as the option is,
and the package hands the values to Driver.js as they are. The fields default to
Driver.js's own defaults. Options that take a JavaScript function are not available.

**Why this priority**: The package leans on Driver.js for what it already does, so moving between
Driver.js's documentation and a tour is one to one, and a developer gets type hints and linting
for each option (G1).

**Independent Test**: Declare a tour with `showProgress=True`, open its page, and confirm the
step count shows.

**Acceptance Scenarios**:

1. **Given** a tour with a Driver.js option set as a field, **When** the tour plays, **Then**
   Driver.js plays it with that option.
2. **Given** a tour that sets no option, **When** the tour plays, **Then** Driver.js plays it
   with its own defaults, and the control labels are in the language the page is served in.
3. **Given** a tour that sets a control's label, **When** the tour plays, **Then** the control
   shows that label.
4. **Given** a tour replaced through `PAGE_TOURS_OVERRIDES`, **When** it plays, **Then** it plays
   with the replacement's options.
5. **Given** a step that sets `skipMissingElement=False` and whose element is not on the page,
   **When** the tour reaches it, **Then** the step is shown attached to nothing.

---

### User Story 4 - A developer words every tour, hint and checklist on the site at once (Priority: P3)

A developer wants the buttons and progress text of every tour, set of hints and checklist on the
site to say what the site's voice says, such as "Continue" instead of "Next", without setting the
text on each one. The `PAGE_TOURS_TEXT` setting gives the text for a kind of declaration: tours,
hints or checklists. The text the developer leaves at the package's own is taken from the
setting, and text the developer sets on a declaration or a step is left alone.

**Why this priority**: Wording is a property of a site, and a site with dozens of tours should
not have to repeat it on each one. It is a convenience, so the tours work without it.

**Independent Test**: Set `PAGE_TOURS_TEXT = {"tour": {"nextBtnText": "Continue"}}`, open a page
whose tour sets no button text, and confirm the next button says "Continue".

**Acceptance Scenarios**:

1. **Given** `PAGE_TOURS_TEXT` gives a text for tours, hints or checklists, **When** a tour, set
   of hints or checklist that does not set that text plays, **Then** it shows the text from the
   setting.
2. **Given** a tour, set of hints or checklist that sets one of those texts itself, **When** it
   plays, **Then** it shows its own text.
3. **Given** a step or hint that sets its own text, **When** it shows, **Then** it shows its own
   text, and the rest of its tour or hints show the text from the setting.
4. **Given** a text in the setting that is translated lazily, **When** a page is served in
   another language, **Then** the text is shown in that language.
5. **Given** a setting with a kind or text that does not exist, or a text that is not a string,
   **When** the project's checks run, **Then** each is reported.
6. **Given** a tour, set of hints or checklist that replaces another through
   `PAGE_TOURS_OVERRIDES`, **When** it plays, **Then** it shows the text from the setting like
   any other that sets none.

---

### Edge Cases

- A step names an element that matches several elements on the page: the step is attached to the
  first one in the page.
- An element a step is attached to exists but is hidden when the tour reaches it: the step is
  treated like a missing element and skipped.
- Every step is skipped: no tour plays (User Story 2, scenario 6).
- The same view renders on two URLs: both pages carry its tour, because the tour belongs to the
  view that renders the page.
- The package's static files are not collected: the tour does not play and the page renders as if
  it had no tour (FR-009).
- A step's description is long: it is shown in full; the package does not cut it short.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: A developer MUST be able to declare a tour for a page in Python, attached to the
  view that renders the page, as an ordered list of tour steps, without writing JavaScript.
  (US1)
- **FR-002**: The package MUST support tours on both class-based and function-based views. Either
  kind puts its tour in the page's template context under `tour`, like any other value, and the
  page's template outputs it with `{{ tour }}` (ADR 0007). Neither needs a decorator, a tag
  library or a setting beyond the one-time setup. (US1)
- **FR-003**: Each tour step MAY have a title and a description, and MAY name one element of the page it
  is attached to. A step that names no element MUST be shown on its own, attached to nothing.
  (US1)
- **FR-004**: A tour with no name or no steps MUST be
  reported to the developer as an error before any visitor is shown the page. (US1)
- **FR-005**: Step titles and descriptions MUST accept strings marked for translation, and MUST be shown
  in the language the page is served in when a translation exists. (US1)
- **FR-006**: Step titles and descriptions MUST reach Driver.js as the developer wrote them,
  unescaped. (US1)
- **FR-007**: A page whose view declares no tour MUST render and behave exactly as it does
  without the package. The package's scripts and stylesheet MAY be loaded on it, and MUST then
  do nothing. (US1)
- **FR-008**: The package MUST ship Driver.js and its stylesheet as static files, at one recorded
  release, with Driver.js's licence beside them. A page with a tour MUST NOT load any script or
  stylesheet from another origin, and MUST need no front-end build step. (US1)
- **FR-009**: With JavaScript off, or with the tour's script unable to load, a page with a tour
  MUST render as it would with no tour: nothing of the tour visible, nothing of the page hidden or
  moved. (US2)
- **FR-010**: A tour MUST start playing from its first showable step by itself the first time a
  browser opens the page, as the Seen tours and replay specification describes. (US2)
- **FR-011**: The visitor MUST be able to move forward and back through the steps in the declared
  order, and close the tour at any step. Finishing the last step MUST end the tour. (US2)
- **FR-012**: A step whose element is not on the page, or is hidden, MUST be skipped silently,
  unless the step sets `skipMissingElement=False`, when it MUST be shown attached to nothing. A
  tour with no showable step MUST NOT play. (US2, US3)
- **FR-013**: A failure inside the tour's script MUST end the tour and leave the page as usable as
  it was without the tour. The package MUST NOT hide, move or change any element of the page
  except while a step attached to it is showing. (US2)
- **FR-014**: A tour MUST be given to signed-in and anonymous visitors alike, and the package MUST
  store nothing about visitors or tours in the database. (US1, US2)
- **FR-015**: The feature MUST ship its documentation page and a page in the demo project whose
  tour shows each kind of step the package supports: a step attached to an element, a step
  attached to nothing, and a step whose element is missing. (US1, US2)
- **FR-016**: A visitor MUST be able to start, follow and close a tour from the keyboard alone.
  Focus MUST move into each step as it shows and, when the tour ends, MUST go back to where it
  was before the tour started. A screen reader MUST announce each step's title and description. (US2)
- **FR-017**: The tour's own controls and progress text MUST be shown in the language the page is
  served in when a translation exists, and in English otherwise, unless the tour sets its own
  labels or `PAGE_TOURS_TEXT` gives them. The package MUST ship an English catalogue of its own
  strings. (US2)
- **FR-018**: A tour MUST have a field for each Driver.js configuration option that takes a
  plain value, named exactly as the option is and defaulting to Driver.js's own default,
  and the option MUST reach the Driver.js constructor under that name. A step MUST have a field
  for each Driver.js step and popover option that takes a plain value, defaulting to the tour's
  value. The options the package sets itself (the steps, the tour's skipping of missing elements
  and the hooks the package uses) are not fields of the tour. Options that take a JavaScript
  function are not available, and `allowedElements` takes selector strings only. The package
  MUST NOT check what an option does. (US3)
- **FR-019**: A `PAGE_TOURS_TEXT` setting, keyed by `"tour"`, `"hint"` or `"checklist"` and then
  by a text's field name, MUST give the text of every tour, set of hints or checklist that has
  not been given its own. For a tour the texts are `progressText`, `nextBtnText`, `prevBtnText`,
  `doneBtnText` and `closeBtnLabel`; for hints, `buttonText`; for a checklist, `title`,
  `progressText` and `launcherProgressText`. Text set on a step or hint wins over text set on a
  tour, hints or checklist, which wins over the setting, which wins over the package's own. A value
  may be a string or a lazy translation, and the setting MUST be read each time a declaration
  renders. The package's checks MUST report a kind or text that does not exist and a value that
  is not a string. A project that does not set it MUST see no change. (US4)

### Key Entities

- **Tour**: A short, guided walk through one page, made of an ordered list of tour steps, with a
  name the developer gives it (ADR 0006) and Driver.js options as fields. It belongs to the
  view that renders the page.
- **Tour step**: One stop in a tour. A title and a description, and optionally the element of the page it
  is attached to.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A developer gives a page a working tour by writing Python only: zero lines of
  JavaScript, and no front-end tooling run.
- **SC-002**: On the demo page, a visitor reaches every showable step going forward, returns to the
  first going back, and can close the tour from any step.
- **SC-003**: A page with a tour makes zero requests to another origin.
- **SC-004**: With JavaScript off, the visible content of a page with a tour is identical to the
  same page with its tour removed.
- **SC-005**: On a page whose tour has a missing element and on a page whose tour script fails,
  the element a step is attached to works while that step shows, the rest of the page is reached
  by closing the tour in one action, and every control the page offers works after the tour ends
  or fails.

## Clarifications

### Session 2026-11-06

- Q: What happens when a step's element is not on the page? → A: The step is skipped silently and
  the tour goes on. A hidden element counts as missing. If no step can be shown, no tour plays.
  (FR-012)
- Q: How often does the tour play? → A: By itself the first time a browser opens the page. The
  browser remembers that it was seen, as the Seen tours and replay specification describes.
  (FR-010)
- Q: Can a step description carry markup such as links or bold? → A: Yes. Titles and
  descriptions reach Driver.js unchanged and are shown as HTML. (FR-006)
- Q: Which views can have a tour? → A: Class-based and function-based views alike. (FR-002)
- Q: What does a developer do once, before declaring tours? → A: Install the app and include the
  package's stylesheet and two scripts in their base template. After that, each tour is declared
  in Python, put in its view's context and output with `{{ tour }}` in its page's template.
  (Assumptions)

## Assumptions

- A site does a one-time setup when it installs the package: adding the app and including the
  package's stylesheet and two scripts in its base template. A tour then needs its declaration
  in Python, its view's context and `{{ tour }}` in its page's template.
- Tours look as Driver.js draws them by default (CONSTITUTION Article XIV). Giving tours a site's
  own look is a later feature (roadmap R5).
- The tour's own controls are drawn by Driver.js, with labels from the package's own catalogue
  unless the tour sets its own (FR-017). Driver.js's step count is not shown unless the tour turns it on (User Story 3).
- A tour belongs to one page. Tours across several pages are out of scope.
- Tours shipped by reusable apps (R6) and tour versions (R7) are later features. This feature
  declares tours in a way that does not block either.
