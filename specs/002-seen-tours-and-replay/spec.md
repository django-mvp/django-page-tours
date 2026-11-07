# Feature Specification: Seen tours and replay

**Feature Branch**: `002-seen-tours-and-replay`

**Created**: 2026-11-06

**Status**: Draft

**Serves**: G2 (a tour plays once for each visitor and then stays out of their way, until they ask
to see it again). Roadmap: R2.

**Input**: Issue #6, "Play a tour once per visitor, with a way to replay it". A visitor who has
been shown a page's tour should not be shown it again on every visit, or they learn to close it
without reading. The tour plays by itself the first time someone opens the page in their browser,
and stays quiet after that, whether they finished it, skipped it or closed it. A visitor who wants
to see it again starts it from a replay control the site puts on the page, which appears only
where the page has a tour. A developer can also make a tour play only from that control, never by
itself. Whether a tour has been seen is remembered in the visitor's browser, so the site keeps
nothing about it.

**Builds on**: issue #5, a tour declared in Python for a page and played when the page opens.
This feature changes when that tour plays by itself and adds a second way to start it.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A returning visitor is not shown a tour they have already seen (Priority: P1)

A visitor opens a page that has a tour. The first time they open it in their browser, the tour
plays by itself, as it does today. From then on, that tour has been seen in this browser, and it
does not play by itself again on any later visit, however the first one ended: finished, skipped,
closed part way, or left by navigating away. Tours on other pages are unaffected: each tour is
seen on its own.

**Why this priority**: it is the reason the feature exists. A tour that plays on every visit is
one people learn to dismiss unread.

**Independent Test**: open a page with a tour in a fresh browser and confirm it plays; reload and
confirm it does not; open a second page with a different tour and confirm that one plays.

**Acceptance Scenarios**:

1. **Given** a page with a tour that this browser has not seen, **When** the visitor opens the
   page, **Then** the tour plays by itself.
2. **Given** the visitor has stepped through a tour to its end, **When** they open the page again
   in the same browser, **Then** the tour does not play by itself.
3. **Given** the visitor closed a tour before its last step, **When** they open the page again,
   **Then** the tour does not play by itself.
4. **Given** a tour started playing and the visitor left the page without closing it, **When**
   they open the page again, **Then** the tour does not play by itself.
5. **Given** the visitor has seen the tour of one page, **When** they open a different page that
   has a different tour, **Then** that page's tour plays by itself.
6. **Given** one tour is shown on several addresses (for example every record's detail page),
   **When** the visitor has seen it on one of them and opens another, **Then** it does not play by
   itself.
7. **Given** the visitor has seen a tour in one browser, **When** they open the same page in a
   different browser or on a different device, **Then** the tour plays by itself there.
8. **Given** the browser refuses to let the page remember anything (storage blocked or full),
   **When** the visitor opens a page with a tour, **Then** the tour plays as it would without this
   feature, and the page shows no error and stays fully usable.
9. **Given** a page with a tour whose steps all point at elements missing from the page, so the
   tour does not play, **When** the visitor opens the page again after the elements appear,
   **Then** the tour plays by itself, because it was never seen.

---

### User Story 2 - A visitor replays a page's tour (Priority: P1)

A visitor who skipped a tour, or wants a reminder, starts it again from the replay control the
site has put on the page. The tour plays from its first step, whether or not it has been seen.
The control is there only on pages that have a tour.

**Why this priority**: without it, a tour that is seen once is gone for good, and a visitor who
closed it by mistake has no way back. Remembering a tour only makes sense with a way to see it
again.

**Independent Test**: on a page whose tour has been seen, use the replay control and confirm the
tour plays from its first step; open a page with no tour and confirm no control is shown.

**Acceptance Scenarios**:

1. **Given** a page whose tour this browser has seen, **When** the visitor uses the replay
   control, **Then** the tour plays from its first step.
2. **Given** a tour is playing, **When** the visitor reaches its end or closes it, **Then** the
   page is as it was before the replay, and the control can start the tour again.
3. **Given** the visitor has replayed a tour, **When** they open the page again, **Then** the tour
   does not play by itself.
4. **Given** a page with no tour, **When** it is rendered with the replay control placed in its
   template, **Then** no replay control is shown.
5. **Given** JavaScript is off in the visitor's browser, **When** they open a page with a tour,
   **Then** no replay control is shown, and the page is exactly as it would be without a tour.
6. **Given** a page with a tour, **When** the visitor reaches the replay control with the keyboard
   alone, **Then** they can start the tour from it.
7. **Given** a tour whose steps all point at elements missing from the page, **When** the visitor
   uses the replay control, **Then** nothing breaks and the page stays fully usable.

---

### User Story 3 - A developer chooses how a page's tour is started (Priority: P2)

A developer puts the replay control into their own templates, wherever it suits their design: next
to the page heading, in a help menu, or once in the base template that every page shares, where it
appears only on the pages that have a tour. They can give it their own content and classes, so it
looks like the rest of their site. For a tour that should never interrupt anyone, they mark it to
play only from the replay control, never by itself.

**Why this priority**: the control has to be placed before a visitor can use it, but a site
gets the main benefit of User Story 1 without placing it at all.

**Independent Test**: place the control once in a base template shared by a page with a tour and
a page without one, and confirm it appears only on the first; mark a tour to play only from the
control, open its page in a fresh browser, and confirm it waits for the control.

**Acceptance Scenarios**:

1. **Given** a developer places the replay control in a base template shared by every page,
   **When** pages with and without tours are rendered, **Then** the control appears only on the
   pages that have a tour.
2. **Given** a developer gives the replay control their own content and classes, **When** the page
   is rendered, **Then** the control carries that content and those classes, and the package adds
   no styling of its own to it.
3. **Given** a developer places no replay control, **When** a visitor opens a page with a tour,
   **Then** the tour still plays once by itself, as in User Story 1.
4. **Given** a tour marked to play only from the replay control, **When** a visitor opens its
   page in a browser that has never seen it, **Then** the tour does not play by itself.
5. **Given** a tour marked to play only from the replay control, **When** the visitor uses the
   control, **Then** the tour plays from its first step.
6. **Given** a tour marked to play only from the replay control and a page with no replay control
   placed on it, **When** the page is rendered, **Then** the tour never plays and the page is as it
   would be without a tour.
7. **Given** a developer who does nothing beyond declaring a tour, **When** a visitor opens its
   page, **Then** the tour plays once by itself: playing once is the default, and needs no setting.

---

### Edge Cases

- The visitor clears their browser's site data: the tour has not been seen, so it plays by itself
  again. This is expected and needs no handling.
- The same page is open in two tabs at once and the tour has not been seen: it may play in both.
  It is seen in both afterwards.
- The replay control is placed more than once on one page: each one starts the page's tour.
- The visitor uses the replay control while the tour is already playing: the tour starts again
  from its first step rather than playing twice over itself.
- A tour is changed after a visitor has seen it: it stays seen. Showing a changed tour again is
  roadmap item R7, not this feature.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: A tour MUST play by itself the first time its page is opened in a browser that has
  not seen it, unless the developer has marked it to play only from the replay control. (US1, US3)
- **FR-002**: A tour MUST be recorded as seen in the browser as soon as it starts playing, so it
  counts as seen however it ends: finished, skipped, closed, or left by navigating away. (US1)
- **FR-003**: A tour that has been seen in a browser MUST NOT play by itself again in that browser.
  (US1)
- **FR-004**: Seen MUST be recorded for each tour separately, and belong to the tour rather than
  to the page's address, so one tour shown on many addresses is seen once. (US1)
- **FR-005**: Seen MUST be kept in the visitor's browser only. The package MUST add no database
  tables and keep nothing about visitors on the server. (US1)
- **FR-006**: When the browser cannot store or read whether a tour has been seen, the tour MUST
  play as it would without this feature, and the page MUST show no error and stay fully usable.
  (US1)
- **FR-007**: The package MUST provide a replay control that a developer places in their own
  templates, anywhere on the page, including in a base template shared by many pages. (US3)
- **FR-008**: The replay control MUST be shown only on a page that has a tour, and MUST NOT be
  shown when JavaScript is off. (US2, US3)
- **FR-009**: Using the replay control MUST play the page's tour from its first step, whether or
  not it has been seen, and whether or not the tour plays by itself. Using it while the tour is
  playing MUST restart the tour, not play a second copy. (US2, US3)
- **FR-010**: The replay control MUST be operable with the keyboard alone and have an accessible
  name. (US2)
- **FR-011**: The replay control MUST carry no look of its own: the package adds no CSS classes or
  styling to it, and the developer can give it their own content and classes. (US3)
- **FR-012**: A developer MUST be able to mark a tour, where they declare it, to play only from
  the replay control and never by itself. Playing once by itself is the default and needs no
  setting. (US3)
- **FR-013**: A replay MUST NOT change whether a tour plays by itself on later visits. (US2)
- **FR-014**: A failure in the replay control or in remembering seen tours MUST leave the page
  exactly as usable as it would be without a tour (Article XIII). (US1, US2)
- **FR-015**: The documentation site MUST describe how a tour plays once, how to place the replay
  control, and how to make a tour play only from it, and the demo project MUST show a page whose
  tour plays once with a replay control and a page whose tour plays only from the control. (US3)

### Key Entities

- **Seen tour**: the browser's record that one tour has played there. Identified by the tour,
  held only in that browser, with nothing on the server.
- **Replay control**: an element the developer places on the page that starts the page's tour on
  request.

## Clarifications

### Session 2026-11-06

- Q: When exactly does a tour count as seen: when it starts, or only when it ends? → A: When it
  starts playing. A visitor who leaves the page mid-tour has seen it, and nothing depends on the
  tour reporting how it ended. Integrated into FR-002 and US1 scenario 4.
- Q: Is seen recorded per page address or per tour? → A: Per tour. A tour shown on every record's
  detail page is seen once, not once per record. Integrated into FR-004 and US1 scenario 6.
- Q: What happens when the browser will not store anything? → A: The tour plays as it would
  without this feature, and the page stays usable. A visitor who never gets the tour is worse off
  than one who sees it again. Integrated into FR-006 and US1 scenario 8.
- Q: Does a tour that never started, because none of its elements were on the page, count as
  seen? → A: No. Seen means it played. Integrated into US1 scenario 9.
- Q: Can a developer make the replay control match their site? → A: Yes. It has no look of its
  own (Article XIV), and the developer gives it its own content and classes. Integrated into FR-011
  and US3 scenario 2.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In one browser, a tour that plays by itself does so at most once, across any number
  of visits to its page and to other pages showing the same tour.
- **SC-002**: On every page with a tour and a placed replay control, a visitor starts the tour with
  one action, and on every page without a tour no replay control is shown.
- **SC-003**: The feature adds no database tables and no server-side record of any visitor.
- **SC-004**: With storage blocked, or JavaScript off, every page with a tour is as usable as the
  same page without one.
- **SC-005**: A developer makes a tour play only on request by changing its declaration alone, and
  places the replay control by editing only their own templates.

## Assumptions

- A page has at most one tour, as issue #5 has it, so "the page's tour" is unambiguous for the
  replay control.
- The tour being extended is the one issue #5 describes. Its declaration in Python is where a tour
  is marked to play only from the replay control.
- Seen state that follows a signed-in person across browsers is out of scope. A new browser or
  device sees the tour again.
- Showing a changed tour again to people who saw the old one is roadmap item R7, out of scope.
- Where the replay control sits in a particular design system's layout is that design system's
  choice, not this package's.
- Translating the control's own text is roadmap item R4. The control's text is translatable from
  the start, per Article VIII.
