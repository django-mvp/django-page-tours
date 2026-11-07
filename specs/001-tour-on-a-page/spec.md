# Feature Specification: A tour on a page

**Feature Branch**: `001-tour-on-a-page`

**Created**: 2026-11-06

**Status**: Draft

**Serves**: G1, G3, G4 (roadmap item R1)

**Input**: Issue #5, "Give a page a guided tour declared in Python".

## Summary

A developer gives one page of their site a short guided tour by declaring it in Python, beside
the view that renders the page, as an ordered list of tour steps. Each step has a title and a
short text, and is either attached to one element of the page or attached to nothing, which suits
an opening welcome. When a visitor opens the page, the tour plays: they can move forward and back
through the steps and close it at any point. The tour never makes the page less usable. A step
whose element is not on the page is skipped, a tour that fails leaves the page as it was, and with
JavaScript off the page renders as if it had no tour. Driver.js draws the tour and ships inside
the package, so nothing is loaded from another origin and no front-end build step is needed.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A developer gives a page a tour (Priority: P1)

A developer adds the package to their project once, then gives any page a tour by declaring it in
Python beside the view that renders that page. The tour is an ordered list of steps. Each step has
a title and a short text, and either names the element of the page it is attached to or is
attached to nothing. The developer writes no JavaScript and runs no front-end tooling. Step titles
and texts can be marked for translation like any other string in their project.

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
   tour and loads none of the package's scripts or stylesheets.
5. **Given** a page with a tour, **When** it renders, **Then** every script and stylesheet the tour
   needs is served by the site itself, and none comes from another origin.
6. **Given** a step whose title and text are marked for translation, **When** the page is served
   in a language the project has a translation for, **Then** the step carries the translated title
   and text.
7. **Given** a step whose title or text contains markup characters, **When** the page renders,
   **Then** the step carries them as text and they are never interpreted as markup.
8. **Given** a tour declared with no steps, or a step with no title or no text, **When** the
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
    as a dialog named by the step's title and described by its text.

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
- A step's text is long: it is shown in full; the package does not cut it short.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: A developer MUST be able to declare a tour for a page in Python, attached to the
  view that renders the page, as an ordered list of tour steps, without writing JavaScript.
  (US1)
- **FR-002**: The package MUST support tours on both class-based and function-based views. (US1)
- **FR-003**: Each tour step MUST have a title and a text, and MAY name one element of the page it
  is attached to. A step that names no element MUST be shown on its own, attached to nothing.
  (US1)
- **FR-004**: A tour with no steps, or a step missing its title or its text, MUST be reported to
  the developer as an error before any visitor is shown the page. (US1)
- **FR-005**: Step titles and texts MUST accept strings marked for translation, and MUST be shown
  in the language the page is served in when a translation exists. (US1)
- **FR-006**: Step titles and texts MUST reach the visitor as text, escaped, and never be
  interpreted as markup. (US1)
- **FR-007**: A page whose view declares no tour MUST render exactly as it does without the
  package, loading none of the package's scripts or stylesheets. (US1)
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
- **FR-012**: A step whose element is not on the page, or is hidden, MUST be skipped silently. A
  tour with no showable step MUST NOT play. (US2)
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
  was before the tour started. A screen reader MUST announce each step's title and text. (US2)

### Key Entities

- **Tour**: A short, guided walk through one page, made of an ordered list of tour steps. It
  belongs to the view that renders the page.
- **Tour step**: One stop in a tour. A title and a text, and optionally the element of the page it
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
- Q: Can step text carry markup such as links or bold? → A: No. Titles and texts are text and
  reach the visitor escaped. (FR-006)
- Q: Which views can have a tour? → A: Class-based and function-based views alike. (FR-002)
- Q: What does a developer do once, before declaring tours? → A: Install the app and add the
  package's one-time setup to their base template. After that, each tour is declared in Python
  only. (Assumptions)

## Assumptions

- A site does a one-time setup when it installs the package: adding the app and placing the
  package's setup once in its base template. Tours themselves need nothing more than Python.
- Tours look as Driver.js draws them by default (CONSTITUTION Article XIV). Giving tours a site's
  own look is a later feature (roadmap R5).
- The tour's own controls (next, back, close, the step count) are Driver.js's. Translating them,
  and shipping a translation catalogue, belongs to roadmap R4. Step titles and texts are
  translatable here because they are the developer's own strings.
- A tour belongs to one page. Tours across several pages are out of scope.
- Tours shipped by reusable apps (R6) and tour versions (R7) are later features. This feature
  declares tours in a way that does not block either.
