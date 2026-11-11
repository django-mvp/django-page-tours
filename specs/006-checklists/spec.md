# Feature Specification: A checklist

**Feature Branch**: `006-checklists`

**Created**: 2026-11-11

**Status**: Draft

**Serves**: G1 (declared in Python, without writing JavaScript), G4 (never makes its page less
usable), G6 (the visitor's language), G7 (a site's own look), G8 (shipped by reusable apps and
changed by the project) and G9 (shown afresh when it changes enough to matter). The goals are
written about tours; a checklist is held to each of them in the same way. Roadmap: none.

**Input**: Issue #39, "Support checklist". Driver.js provides a checklist API
(https://driverjs.com/docs/checklists) and the package should support it. A checklist is a
"get started" list that sits in a corner of every page of a site. Each item is one thing a
visitor is asked to do: take a tour, follow a link, or do something in the app. The visitor
works through the items in any order, sees how far they have got, and the list remembers what
they have done.

**Comes from**: the prototype on branch `prototype-hints-and-checklists` (issue #45), section
"3. A checklist" of its hand-over. Its screens are agreed: the checklist on every page of the
demo project, and the book page `/library/book/`, where borrowing a book ticks an item from the
app.

**Builds on**: pull request #43 (a tour and its steps declare Driver.js's options as fields, named
as Driver.js names them), issue #46 (the package ships Driver.js 1.11.0, which has a checklist
build) and FS-005, hints on a page (issue #40), which builds the shared base for every Driver.js
object, the shared base for what a page renders, what the browser remembers, and the one entry
point that plays every kind of guide on a page. This specification describes the checklist
against that work.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A developer adds a checklist to a site's pages (Priority: P1)

A developer wants new visitors to try the handful of things that make the site worth using. They
declare a checklist in Python, with a name and its items, the same way they declare a tour. Each
item asks the visitor to do one thing: take a tour, which is an ordinary tour declared like any
page's; follow a link; or do something in the app, which the developer's own code reports as done
on each request from what the app knows. The developer can let the visitor tick items
themselves, for the whole checklist or one item. They set the checklist's options under the names
Driver.js gives them, such as its heading, its text once everything is done, its progress text,
the corner it sits in and whether it shows its own launcher. A checklist with no launcher opens
from a control the developer places on the page. They put the checklist in the template context
of the pages it should appear on, often all of them through a context processor, and the base
template outputs it. When the checklist changes enough that visitors should work through it
again, the developer raises its version. A reusable app can ship a checklist the way it ships a
tour, and a project can replace it or turn it off.

**Why this priority**: it is the feature. Without a declaration there is nothing for a visitor to
work through.

**Independent Test**: declare a checklist with one item of each kind, put it in a page's context
and output it in the template; open the page and see the checklist with every item, in order;
report one item as done from the view and see it ticked on the next request; render the page with
JavaScript off and see the page as it is without a checklist.

**Acceptance Scenarios**:

1. **Given** a checklist declared in Python and put in a page's template context, **When** the
   page's template outputs it, **Then** the page shows the checklist with its items in the
   declared order, and the developer has written no JavaScript.
2. **Given** a checklist item that names a tour, **When** a visitor starts the item, **Then** that
   tour plays exactly as it would as a page's own tour: its steps, its options, its part classes,
   its language and its handling of missing elements.
3. **Given** a checklist item that names a link, **When** a visitor starts the item, **Then** the
   browser follows the link.
4. **Given** an item with neither a tour nor a link, and a view or context processor that reports
   that item as done for the current request, **When** the page renders, **Then** the item is
   ticked.
5. **Given** the developer allows the visitor to tick items, for the whole checklist or for one
   item, **When** the page renders, **Then** the visitor can tick and untick those items, and no
   others.
6. **Given** a checklist declared with no launcher, and a control on the page that the developer
   marks as the checklist's toggle, **When** the visitor presses the control, **Then** the
   checklist opens, and pressing it again closes it.
7. **Given** a toggle control on a page with no checklist, or with JavaScript off, **When** the
   page renders, **Then** the control is not shown.
8. **Given** a checklist option the developer sets under its Driver.js name, **When** the page
   renders, **Then** Driver.js receives it unchanged, and an option the developer leaves unset
   takes Driver.js's own default.
9. **Given** the developer sets none of the checklist's own labels, **When** the page is served in
   a language the package has translations for, **Then** the checklist's default labels are in
   that language.
10. **Given** a site that gives the package's parts their classes, **When** the checklist is
    shown, **Then** its panel, title, description, progress and close control carry the classes
    of the matching parts of a tour step, and its launcher and items carry classes of their own.
11. **Given** a checklist shipped by an installed reusable app, **When** the project replaces it
    or turns it off under its name, **Then** every page shows the project's choice, as for a tour.
12. **Given** an item's tour shipped by an installed reusable app, **When** the project replaces
    or turns off that tour under its name, **Then** the item plays the project's replacement, or
    is left out of the checklist when the tour is turned off.
13. **Given** two checklists with different items declared under one name, **When** Django's
    `check` command runs, **Then** it reports the name.
14. **Given** a page that outputs the checklist and JavaScript is off, or the checklist's script
    fails, **When** the page renders, **Then** the page is exactly as usable as it is without a
    checklist.
15. **Given** a page that also has its own tour, its own hints or both, **When** the page renders,
    **Then** each plays as it does on its own, beside the checklist.

### User Story 2 - A visitor works through a site's checklist (Priority: P2)

A visitor new to the site sees the checklist in a corner of the page, with how many of its items
they have done. They open it and pick an item in any order. An item with a tour plays the tour;
when they finish it, the item is ticked and the checklist shows it ticked. An item with a link
takes them to it and is ticked. An item about something done in the app ticks itself once they
have done it. Where the site allows it, they tick an item themselves, and untick it again. They
close the checklist and carry on using the page. Coming back to the site in the same browser,
they find their ticks where they left them. Once every item is done, the checklist says so.

**Why this priority**: it is what the developer's checklist is for, and it is only possible once
story 1 exists.

**Independent Test**: on a page with a checklist of one item of each kind, open the checklist,
finish the item's tour, follow the link item, do the app's action and tick the manual item; see
the progress rise at each; reload the page and see every tick kept; finish the last item and see
the checklist report it is complete.

**Acceptance Scenarios**:

1. **Given** a page with a checklist, **When** the visitor opens it, **Then** they see every item,
   which items are done, and how many are done out of how many.
2. **Given** an item with a tour, **When** the visitor finishes the tour, **Then** the item is
   ticked and the checklist shows it ticked.
3. **Given** an item with a tour, **When** the visitor closes the tour before its last step,
   **Then** the item is not ticked.
4. **Given** an item's tour that the visitor has started from the checklist, **When** the same
   tour is a page's own tour, **Then** it counts as seen and does not play again by itself, as if
   it had played on that page.
5. **Given** an item with a link, **When** the visitor follows it from the checklist, **Then** the
   item is ticked.
6. **Given** an item the visitor may tick, **When** they tick it and later untick it, **Then** the
   checklist and its progress follow each change.
7. **Given** the visitor has ticked items, or finished their tours or followed their links,
   **When** they come back to any page with the checklist in the same browser, **Then** those
   items are still ticked.
8. **Given** the app reports an item as done, **When** the visitor has also ticked other items in
   the browser, **Then** the checklist shows both as ticked.
9. **Given** the developer has raised the checklist's version since the visitor's ticks were
   kept, **When** the visitor opens a page with it, **Then** none of the earlier ticks are kept,
   and the items the app reports as done are still ticked.
10. **Given** every item is ticked, **When** the visitor opens the checklist, **Then** it shows
    its completed state, with the text the developer gave for it where they gave any.
11. **Given** the checklist is shown, **When** the visitor uses the page around it, **Then** the
    page stays usable: the checklist covers nothing the visitor cannot reach by closing it.
12. **Given** a visitor using only the keyboard, **When** they open the checklist, start an item
    and close it, **Then** each of these can be done from the keyboard, as Driver.js provides.

### Edge Cases

- An item's tour has no step whose element is on the page. Driver.js plays what it can as for a
  page's own tour: steps with missing elements are skipped, and a tour with nothing left to show
  does not start, so the item stays unticked.
- An item's tour is also the page's own tour. It is one tour, with one record of being seen,
  whichever of the two plays it.
- The app stops reporting an item as done. The item is unticked unless the visitor's browser
  holds a tick for it.
- An item is removed from the declaration. A tick the browser kept for it no longer counts
  towards progress.
- An item is reworded or moved. Its tick is kept, because ticks are kept against the item's id,
  never its text or position.
- The browser cannot store anything (storage disabled or full). The checklist still works for the
  page view, and nothing is remembered.
- A checklist option that takes a JavaScript function in Driver.js (`completeWhen`, an item's
  `action`, the event hooks). It is not available, and the documentation says so. What the app
  knows is reported through the checklist's completed items instead.
- A checklist is put in a page's context but the page's template does not output it. Nothing is
  shown, as for a tour.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: A developer MUST be able to declare a checklist in Python with a name and an ordered
  list of items, and output it in a template from the page's context, with no JavaScript. (US1)
- **FR-002**: A checklist item MUST have an id, which its tick is kept under, and a title, and MAY
  have a description, a tour, a link, and its own setting for whether the visitor may tick it.
  (US1)
- **FR-003**: An item's tour MUST be an ordinary tour, declared as a page's own tour is, and MUST
  play as a page's own tour does. (US1, US2)
- **FR-004**: Every checklist option Driver.js 1.11.0 takes as a plain value MUST be declarable on
  the checklist under the name Driver.js gives it, MUST default to Driver.js's own default, and
  MUST reach Driver.js unchanged. Options that take a JavaScript function MUST NOT be available.
  (US1)
- **FR-005**: A view or context processor MUST be able to report, for the current request, which
  items are done, from what the app knows. (US1)
- **FR-006**: A visitor MUST see a checklist's items, which are done and the progress, and MUST be
  able to start any item in any order. (US2)
- **FR-007**: An item MUST be ticked when the visitor finishes its tour, follows its link from the
  checklist, ticks it where allowed, or when the app reports it as done. Closing an item's tour
  before its end MUST NOT tick it. (US2)
- **FR-008**: The visitor's ticks MUST be remembered in their browser under the checklist's name
  and version, MUST be shown together with the items the app reports as done, and MUST be
  forgotten when the developer raises the checklist's version. Nothing MUST be stored in the
  database. (US2)
- **FR-009**: A tour started from a checklist item MUST count as seen, at its version, exactly as
  a tour played as a page's own tour does. (US2)
- **FR-010**: A checklist declared with no launcher MUST open and close from a control the
  developer marks as its toggle, and that control MUST stay hidden where there is no checklist or
  no JavaScript. (US1)
- **FR-011**: The checklist's default labels MUST be translatable and shown in the language the
  page is served in. Text the developer sets MUST reach Driver.js as it is. (US1)
- **FR-012**: The checklist's panel, title, description, progress and close control MUST carry
  the classes a site gives the matching parts of a tour step, and its launcher and items MUST
  carry classes a site can give them under parts of their own. (US1)
- **FR-013**: A project MUST be able to replace or turn off an installed app's checklist under its
  name, and an installed app's tour used by a checklist item, in the way it does for an app's tour.
  An item whose tour is turned off MUST be left out of the checklist. (US1)
- **FR-014**: Django's `check` command MUST report two different checklists declared under one
  name, as it does for tours. (US1)
- **FR-015**: A page with a checklist MUST stay as usable as it is without one: with JavaScript
  off, when the checklist's script fails, and while the checklist is shown. (US1, US2)
- **FR-016**: A page MUST be able to carry a checklist beside its own tour and its own hints, each
  playing as it does on its own. (US1)
- **FR-017**: The documentation site MUST describe how to declare a checklist, its items and
  options, how to report items as done from the app, the toggle control, its part classes, and
  which Driver.js options are not available; the README's scope MUST include checklists; and the
  demo project MUST show a checklist whose items start a tour, follow a link, are ticked by the
  app and are ticked by the visitor. (US1, US2)

### Key Entities

- **Checklist**: a named, versioned list of items a visitor works through, declared in Python and
  shown by Driver.js in a corner of the page. Its name is Driver.js's id. A page carries at most
  one.
- **Checklist item**: one thing a visitor is asked to do, kept by its id. It starts a tour, follows
  a link, or is done in the app.
- **Ticked**: an item is ticked once it is done, by any of the four ways in FR-007. Ticks are kept
  in the visitor's browser, together with what the app reports.

## Clarifications

### Session 2026-11-11

- Q: Does a tour started from a checklist count as seen, even when it was not finished? → A: Yes.
  A tour is seen once it has played, whether finished, skipped or closed, wherever it played. Only
  finishing it ticks the item. Integrated into FR-007, FR-009 and story 2 scenarios 2 to 4.
- Q: What happens when a visitor unticks an item the app reports as done? → A: The app's report
  wins. What the app reports is a fact about the visitor, so the item is ticked again on every
  request the app reports it, whatever the browser kept. Integrated into FR-008 and story 2
  scenario 8.
- Q: What does raising a checklist's version do to what the app reports? → A: Nothing. It forgets
  only the ticks the browser kept. Integrated into story 2 scenario 9.
- Q: Does `PAGE_TOURS_OVERRIDES` reach the tour of a checklist item? → A: Yes, under the tour's
  name, so a project that changes an app's tour changes it wherever it plays. A turned-off tour
  takes its item with it, since the item has nothing left to start. Integrated into FR-013 and
  story 1 scenario 12.
- Q: How many checklists can one page carry? → A: One, as a page carries one tour. Integrated into
  Key Entities.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A developer adds a checklist whose items start a tour, follow a link, are ticked by
  the app and are ticked by the visitor, writing only Python and one template output, and no
  JavaScript.
- **SC-002**: A visitor's ticks survive every reload and every page of the site in the same
  browser, until the developer raises the checklist's version.
- **SC-003**: A tour reached from a checklist behaves, looks and is remembered exactly as the same
  tour played on its page.
- **SC-004**: Every page with a checklist is as usable with JavaScript off, or with the checklist's
  script failing, as the same page without one.
- **SC-005**: A project changes or turns off a checklist shipped by an installed app without
  editing the app.

## Assumptions

- Driver.js 1.11.0's checklist build is shipped by issue #46 and does the drawing: the panel, the
  launcher, the progress, opening an item's tour and reopening afterwards, keyboard use. It keeps
  no record of its own between page loads, so the package keeps the ticks.
- FS-005 builds the shared base classes for a Driver.js object and for what a page renders (name,
  version, the record of declared names, `PAGE_TOURS_OVERRIDES`, rendering with `{{ … }}`), what
  the browser remembers, and the entry point that plays every kind of guide on a page. A
  checklist is declared and played through them.
- The part classes are the ones a site sets for tours today (FS-003, issue #22). The checklist
  adds two parts and reuses five.
- What the app knows about a visitor is the developer's to compute. The package gives it a place
  on the checklist and does not store it.
- A checklist across devices for a signed-in person is out of scope, as seen tours are: everything
  remembered is in the browser.
