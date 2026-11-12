# Feature Specification: Hints on a page

**Feature Branch**: `005-hints`

**Created**: 2026-11-11

**Status**: Draft

**Serves**: G1 (a developer declares what a page shows a visitor in Python, beside the view that
renders it, without writing JavaScript), G2 (it stays out of a visitor's way once they are done
with it), G4 (it never makes its page less usable). It carries G5, G6, G7, G8 and G9 over from
tours to hints. Roadmap: none yet (see `decisions.md`, D10).

**Input**: Issue #40, "Support hints". Driver.js 1.11.0 adds hints (https://driverjs.com/docs/hints):
small pulsing beacons on elements of a page, each opening a popover about its element. Unlike a
tour, hints do not take over the page. A visitor opens them in any order, or not at all, and goes
on using the page while one is open. Pressing a hint's button dismisses it, and it stays dismissed
in that browser. A developer declares a page's hints in Python, the way they declare its tour, and
the page renders them with `{{ hints }}`. Every option Driver.js gives hints that takes a plain
value is available to the developer under Driver.js's own name and with Driver.js's own default.

This specification describes the hints page of the prototype the maintainer agreed (issue #45,
branch `prototype-hints-and-checklists`, demo page `/hints/`).

**Builds on**: pull request #43 (a tour and its steps declare Driver.js's options as fields, named
and defaulted as Driver.js names and defaults them) and issue #46 (the package ships Driver.js
1.11.0, which has the hints build). Both come before this feature.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A developer puts hints on a page (Priority: P1)

A developer wants to point out a few things on a page without stopping anyone to do it: the export
button, the summary paragraph, the figures table. Beside the view that renders the page, they
declare the page's hints in Python, with a name: for each hint, the element it is about, a title
and a description. They put the hints in the template context and write `{{ hints }}` in the page's
template. Where the defaults do not suit, they set Driver.js's own options: where a beacon sits on
its element and whether it pulses, where a popover sits, the text of the button that dismisses a
hint, whether the page is dimmed while a hint is open. Options set for all of a page's hints apply
to each hint unless that hint sets its own. When they rewrite the hints enough that visitors should
read them again, they raise the hints' version. They can place a control of their own that brings
dismissed hints back. A page can carry hints and a tour at once.

A reusable app ships hints for its own pages the same way, and a project that installs the app
replaces those hints or turns them off by name, without editing the app, as it does with an app's
tour.

**Why this priority**: nothing reaches a visitor until a developer has declared it.

**Independent Test**: declare hints with three hints on a demo page, render it, and confirm three
beacons appear on their elements; set an option on the hints and override it on one hint, and
confirm that hint alone differs.

**Acceptance Scenarios**:

1. **Given** a developer declares hints with a name and a list of hints, each naming an element, a
   title and a description, **When** the view puts them in the context and the template renders
   `{{ hints }}`, **Then** each hint shows a beacon on its element.
2. **Given** hints declared with no options beyond the hints themselves, **When** the page is
   rendered, **Then** every option takes Driver.js's own default, and the button that dismisses a
   hint carries the package's translated default text in the active language.
3. **Given** the developer sets an option of Driver.js's hints configuration under Driver.js's
   name (the beacon's side, alignment, pulsing, class or offset; the popover's class or distance
   from its beacon; the button text; the page overlay, its colour and opacity), **When** the page is
   rendered, **Then** Driver.js receives that option with that value.
4. **Given** an option set for all of a page's hints and the same option set differently on one
   hint (its beacon, its button text, its popover's class), **When** the page is rendered, **Then**
   that hint uses its own value and every other hint uses the shared one.
5. **Given** a hint leaves an option unset, **When** the page is rendered, **Then** the option is
   not sent for that hint, so the value set for all the hints, or else Driver.js's default,
   applies.
6. **Given** a hint's popover fields (title, description, side, alignment, class), **When** the
   developer declares the hint, **Then** they set them directly on the hint, as they set them on a
   tour step.
7. **Given** a hint's title or description contains HTML, **When** the popover opens, **Then** the
   HTML renders as written: text is passed to Driver.js as it is, as a tour step's is.
8. **Given** a hint declared without an identifier of its own, **When** the visitor dismisses it,
   **Then** it is remembered under its element; **Given** a hint declared with one, **Then** it is
   remembered under that identifier, so moving the hint to another element keeps it dismissed.
9. **Given** hints declared without a version, **When** the page is rendered, **Then** they are at
   version 1; **Given** the developer raises the version, **When** a visitor who dismissed hints at
   the earlier version opens the page, **Then** every hint shows its beacon again.
10. **Given** a developer places a control of their own, marked to restore hints and `hidden`, on a
    page with hints, **When** the page loads, **Then** the control is shown; **Given** the same
    control on a page with no hints, or with JavaScript off, **Then** it stays hidden.
11. **Given** a page that renders both `{{ hints }}` and `{{ tour }}`, **When** the page loads,
    **Then** both play, and a tour step can point at an element a hint is about.
12. **Given** a reusable app declares hints under a name, **When** a project names them in
    `PAGE_TOURS_OVERRIDES` with a replacement, **Then** the replacement renders in their place,
    remembered under the app's name; **Given** the entry turns them off, **Then** the page renders
    no hints.
13. **Given** two different sets of hints declared under one name, **When** the system checks run,
    **Then** they warn about the name, as they do for two different tours under one name.
14. **Given** an option whose value Driver.js would take as a JavaScript function, **When** the
    developer looks for it, **Then** it is not available, and the documentation says which ones are
    left out and what that means (a hint's button cannot start a tour).
15. **Given** a hint names an element that is not on the page, **When** the page loads, **Then**
    that hint shows no beacon and the others are shown as declared.

---

### User Story 2 - A visitor reads a page's hints and dismisses them (Priority: P1)

A visitor opens a page with hints and sees small beacons on a few of its elements. They open
whichever interests them, in any order, read the popover, and carry on using the page: the page
behind an open hint still takes clicks and typing. When they have read a hint, they press its
button and that beacon goes, for good in this browser. Hints they have not dismissed are still
there next time. If they want them back, they use the control the site has placed for it. While a
tour plays on the same page, the beacons step aside, and they come back when it ends.

**Why this priority**: it is what the hints are for. A hint that comes back after it was dismissed
is a hint people learn to ignore.

**Independent Test**: open the demo hints page in a fresh browser, open two hints in the reverse
of their declared order while clicking a button on the page, dismiss one, reload and confirm only
that beacon is gone; use the restore control and confirm it is back.

**Acceptance Scenarios**:

1. **Given** a page with hints, **When** the visitor opens one hint and then another, in any
   order, **Then** each opens its own popover about its own element.
2. **Given** a hint is open, **When** the visitor clicks, types or scrolls on the rest of the page,
   **Then** the page responds as it would with no hint open, unless the developer turned the
   overlay on.
3. **Given** the visitor presses a hint's button, **When** they open the page again in the same
   browser, **Then** that hint shows no beacon, and the hints they did not dismiss still do.
4. **Given** a hint dismissed on one page, **When** the same hints are rendered on another address
   (for example every record's detail page), **Then** that hint stays dismissed there too.
5. **Given** the visitor has dismissed hints in one browser, **When** they open the page in a
   different browser or on a different device, **Then** every hint shows its beacon.
6. **Given** dismissed hints and a restore control on the page, **When** the visitor uses the
   control, **Then** every hint shows its beacon again at once, without reloading the page.
7. **Given** a tour starts on a page with hints, **When** it plays, **Then** no beacon is shown
   over it; **When** the tour ends, **Then** the beacons that were showing are back.
8. **Given** a page with hints, **When** the visitor uses the keyboard alone, **Then** they can
   reach each beacon in the declared order, open it, press its button and close the popover.
9. **Given** a visitor whose system asks for reduced motion, **When** they open a page with hints,
   **Then** no beacon pulses.
10. **Given** the browser refuses to let the page remember anything (storage blocked or full),
    **When** the visitor dismisses a hint, **Then** it goes for that page view, comes back on the
    next one, and the page shows no error.
11. **Given** JavaScript is off, or the package's script fails, **When** the visitor opens a page
    with hints, **Then** no beacon is shown and the page is exactly as it would be without hints.

---

### User Story 3 - A developer gives hints their site's look (Priority: P2)

A developer, or a design system that serves many sites, styles hints with the classes it already
uses for tours. A hint's popover is a popover, so its parts carry the same classes as a tour step's
parts. The beacon is a new part, with its own documented class name and classes the developer
configures, in the same setting and from the same places as the parts of a tour step.

**Why this priority**: hints work and are usable with Driver.js's own styling. A site's own look
comes once they are on a page.

**Independent Test**: configure classes for the box, title, text and beacon parts in
`PAGE_TOURS_CLASSES`, render the demo hints page, open a hint, and confirm the popover's parts and
the beacon carry them.

**Acceptance Scenarios**:

1. **Given** classes configured for the parts of a tour step, **When** a hint's popover opens,
   **Then** each part it shows carries the documented class name and the classes configured for
   that part, as a tour step's would.
2. **Given** classes configured for the beacon part, **When** a page with hints is rendered,
   **Then** every beacon carries the documented class name of the beacon part and those classes,
   ahead of any class the hint itself gives its beacon.
3. **Given** an installed app (such as a design system) declares classes for the beacon part,
   **When** the project's setting does not, **Then** the beacons carry the app's classes, in the
   same order of precedence as for the parts of a tour step.
4. **Given** the beacon part configured wrongly (an unknown part name, a value that is not classes),
   **When** the system checks run, **Then** they report it as they report a wrongly configured
   part of a tour step.

---

### Edge Cases

- Two hints name the same element and neither has an identifier: they share what is remembered,
  so dismissing one dismisses both. The documentation says to give such hints identifiers.
- A dismissed hint's identifier is no longer declared (the developer removed or renamed it): the
  record of it is ignored, and nothing breaks.
- A hint is added to hints a visitor has partly dismissed, at the same version: the new hint shows
  its beacon, and the dismissed ones stay dismissed.
- The developer lowers the version: the browser holds a different version from the one declared,
  so every hint shows again, as for a tour.
- The restore control is placed more than once on a page: each one brings the hints back.
- Hints declared with an empty list of hints: the page renders, and nothing is shown.
- A hint's element is shown after the page loads (an expanding panel): Driver.js's own behaviour
  applies, and the package adds no watching of its own.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: A developer MUST be able to declare a page's hints in Python, with a name and a list
  of hints, and render them in a template with `{{ hints }}`, with no JavaScript of their own.
  (US1)
- **FR-002**: Each class a developer declares hints with MUST mirror a Driver.js object: the hints
  configuration, one hint, and a beacon. Every option of that object that takes a plain value MUST
  be a field, named exactly as Driver.js names it. (US1)
- **FR-003**: The hints' own fields MUST default to Driver.js's defaults. A hint's fields, and a
  beacon's, MUST default to unset, and an unset field MUST be left out of what Driver.js receives,
  so the value for all the hints, or Driver.js's default, applies. (US1)
- **FR-004**: A hint's popover fields MUST be fields of the hint itself, shared with a tour step:
  the title, description, side, alignment and class, alongside the hint's own button options.
  (US1)
- **FR-005**: The default text of a hint's button MUST be translatable, and render in the active
  language. A site can give it other text for every set of hints with `PAGE_TOURS_TEXT`
  (specification 001, FR-019). (US1)
- **FR-006**: A hint's title, description and button text MUST be passed to Driver.js as they are,
  with no escaping and no checks of their content. (US1)
- **FR-007**: The package MUST NOT check the values of Driver.js's options beyond what it depends
  on itself. Options whose value is a JavaScript function MUST NOT be available, and the
  documentation MUST name them. (US1)
- **FR-008**: Hints MUST carry a name and a version on the same terms as a tour: every set of hints
  has a name, the version is a whole number of 1 or more defaulting to 1, and a name or version
  that breaks these terms MUST be refused where the hints are declared with `ImproperlyConfigured`.
  (US1)
- **FR-009**: A name MUST belong to one declaration whatever its kind: a tour and a set of hints
  given the same name are warned about by the system checks as one name declared twice. (US1)
- **FR-010**: `PAGE_TOURS_OVERRIDES` MUST replace or turn off a set of hints by name, as it does a
  tour, with the same version rule. An entry whose replacement is not a set of hints MUST be
  refused with `ImproperlyConfigured`, naming the entry. (US1)
- **FR-011**: A dismissed hint MUST be remembered in the visitor's browser only, under the hints'
  name and version, by the hint's identifier, or by its element when it has none. The package MUST
  add no database tables. (US2)
- **FR-012**: A hint remembered as dismissed MUST NOT show its beacon in that browser until the
  hints are declared with a new version or the visitor brings them back. (US1, US2)
- **FR-013**: A developer MUST be able to make an element of their own into a control that brings
  dismissed hints back, placed anywhere in their templates. It MUST stay hidden, when marked
  `hidden`, on a page without hints and when JavaScript is off, and MUST be shown on a page with
  hints. Using it MUST show every hint's beacon again without reloading the page. (US1, US2)
- **FR-014**: Hints MUST leave the page usable while one is open, unless the developer turns
  Driver.js's overlay on. (US2)
- **FR-015**: While a tour plays on a page with hints, the beacons MUST NOT be shown over it, and
  MUST return when it ends. (US2)
- **FR-016**: Every beacon, the popover it opens and the popover's button MUST be operable with the
  keyboard alone, reached in the declared order of the hints. (US2)
- **FR-017**: When the browser cannot store or read what was dismissed, hints MUST show as if
  nothing was, and the page MUST show no error. (US2)
- **FR-018**: A failure of the hints, their script or their remembering MUST leave the page exactly
  as usable as it would be without hints, and with JavaScript off nothing of the hints is shown.
  (US2)
- **FR-019**: A hint's popover MUST carry the part classes a tour step's popover carries, for each
  part it shows. The beacon MUST be a new part with its own documented class name, configured in
  `PAGE_TOURS_CLASSES` and by installed apps exactly as the parts of a tour step are, and carried
  ahead of the hint's own beacon class. (US3)
- **FR-020**: The system checks that report a wrongly configured part MUST cover the beacon part.
  (US3)
- **FR-021**: A tour, its steps, its seen record, its replay control and its overrides MUST keep
  behaving as their specifications describe, declared exactly as they are after pull request #43
  and issue #46. The one change a visitor may see is stated in the changelog: a browser that saw a
  tour before this release sees it once more. (US1)
- **FR-022**: The documentation site MUST describe declaring hints, their options and which are
  left out, dismissal and version, the restore control, overrides from a reusable app and the
  beacon part, and the demo MUST show a page with hints and a tour on it. (US1, US2, US3)

### Key Entities

- **Hints**: what a page renders with `{{ hints }}`: a name, a version, the page's hints, and the
  options of Driver.js's hints configuration that apply to every hint. A page has at most one.
- **Hint**: one hint: the element it is about, an optional identifier, its popover's content and
  position, and the options it sets in place of the hints' own.
- **Beacon**: where a hint's marker sits on its element and how it looks. Its side and alignment
  are the edge of the element, not the popover's position, which is why it is its own object.
- **Dismissed hint**: the browser's record that a visitor pressed a hint's button, kept under the
  hints' name and version, by the hint's identifier or element. Nothing is kept on the server.
- **Restore control**: an element of the developer's own, marked `data-page-hints-restore`, that
  brings dismissed hints back.

## Clarifications

### Session 2026-11-11

- Q: Does a hint come back on the next visit after it is dismissed? → A: No. It stays dismissed in
  that browser until the version is raised or the visitor uses the restore control. That is what
  the prototype does, and what the maintainer agreed on issue #45. Integrated into FR-012 and US2
  scenario 3.
- Q: What is a hint remembered by when the developer gives it no identifier? → A: Its element, the
  prototype's reading. A developer who moves a hint gives it an identifier to keep it dismissed.
  Integrated into FR-011 and US1 scenario 8.
- Q: Do a tour and hints share one namespace of names? → A: Yes. A name is how a project reaches
  a declaration in `PAGE_TOURS_OVERRIDES`, so one name must reach one thing. Integrated into FR-009
  and FR-010.
- Q: What does a visitor see when storage is blocked? → A: The hints, as on a first visit. A
  dismissal lasts for that page view. A visitor who never gets a hint is worse off than one who
  sees it again, the reading FS-002 took for tours. Integrated into FR-017 and US2 scenario 10.
- Q: Does a project see any change in its tours? → A: Only one: browsers that saw a tour see it
  once more, because what the browser remembers is kept in one shape for tours and hints alike.
  The prototype accepted this and the hand-over asks for it in the changelog. Integrated into
  FR-021.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A developer puts hints on a page by declaring them in Python and adding `{{ hints }}`
  to its template, with no JavaScript and no new settings.
- **SC-002**: Every option of Driver.js 1.11.0's hints configuration, its hint and its beacon that
  takes a plain value is available under Driver.js's name, and none that takes a function is.
- **SC-003**: In one browser, a dismissed hint shows its beacon again only after the version is
  raised or the visitor asks for it, across any number of visits and addresses.
- **SC-004**: With a hint open, every control on the page responds to a click or a key as it does
  with none open, unless the overlay is turned on.
- **SC-005**: With storage blocked, JavaScript off or the hints' script failing, every page with
  hints is as usable as the same page without them.
- **SC-006**: A site that already styles tours through `PAGE_TOURS_CLASSES` styles a hint's popover
  with no new configuration, and its beacon with one new entry.
- **SC-007**: The feature adds no database tables and no server-side record of any visitor.

## Assumptions

- A page has at most one set of hints, as it has at most one tour.
- The Driver.js release is 1.11.0, shipped by issue #46. Its hints options are the ones this
  feature mirrors.
- A checklist (issue #39) is a separate feature. It reuses what this feature builds for
  remembering, part classes and playing a page's declarations, and owns everything of its own.
- Hints that follow a signed-in person across browsers are out of scope, as seen tours are.
- Starting a tour from a hint's button would need a function option, and is out of scope.
