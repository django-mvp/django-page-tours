# Decisions — FS-002 Seen tours and replay

Decisions taken while specifying, where the issue was silent. Each one is integrated into
`spec.md`; this file records why.

## Readings of the issue

1. **Seen lives in the browser only.** No database tables, nothing about visitors on the server,
   so a new browser or device sees the tour again. Stated by the issue and by the README's scope;
   recorded here because it rules out seen state per account (FR-005).
2. **A tour counts as seen once it has played**, whether finished, skipped or closed, as
   `CONTEXT.md` defines Seen (FR-002, FR-003).
3. **A developer can make a tour play only from the replay control.** Playing once by itself is
   the default, so a developer who only declares a tour gets the main benefit with no setting
   (FR-012).
4. **The replay control is something the site places on its own page**, shown only where the page
   has a tour. Where it goes in a particular design system is that design system's choice; a
   design system built on this package can put it in its navigation bar (FR-007, FR-008).
5. **Out of scope:** showing a changed tour again (R7, tour versions) and seen state that follows
   a signed-in person across browsers.
6. **No sketch.** The control carries no look of its own (Article XIV), and the feature adds no
   page or form that needs a design judgement.

## Ambiguities resolved

### Seen is recorded when the tour starts, not when it ends

*Ambiguous:* "once it has played" could mean once it started or once it ended.
*Chosen:* when it starts playing.
*Why:* a visitor who navigates away mid-tour has been shown it, and recording at the start leaves
no path (a closed tab, a link followed from inside a step) where the tour plays again. It also
means nothing depends on the tour reporting how it ended.

### Seen belongs to the tour, not the address

*Ambiguous:* a tour declared for a view shown on many addresses (every record's detail page).
*Chosen:* seen once per tour.
*Why:* the issue speaks of "a page's tour", and a tour belongs to a page in the sense of the view
that renders it (`CONTEXT.md`, Tour). Playing it again for every record would recreate the
problem the feature exists to fix.

### Blocked or full storage: the tour plays as it would without this feature

*Ambiguous:* what happens when the browser refuses to remember anything.
*Chosen:* the tour plays by itself each visit, with no error.
*Why:* the alternative, never playing, leaves that visitor with no tour at all unless the site has
placed a replay control. Article XIII requires the page to stay usable either way.

### A tour that never started is not seen

*Ambiguous:* a tour whose elements are all missing does not play (issue #5). Does it count?
*Chosen:* no.
*Why:* seen means it played (`CONTEXT.md`). A visitor who never saw it should see it once its
elements are there.

### The replay control takes the site's own content and classes

*Ambiguous:* the issue says the site puts the control on the page, but not whether the site can
make it look like its own.
*Chosen:* the developer gives it their own content and classes, and the package adds none.
*Why:* Article XIV (no look of its own) and goal G7 (a site gives tours its own look). A control
fixed by the package could not sit in another design's navigation bar.

### Replay restarts a playing tour

*Ambiguous:* using the control while the tour is already playing.
*Chosen:* the tour restarts from its first step.
*Why:* two copies of a tour drawn over each other would make the page unusable (Article XIII).

### One tour per page

*Ambiguous:* which tour the control starts if a page had several.
*Chosen:* a page has at most one tour, as issue #5 describes it, so the control starts that one.
*Why:* nothing in the issues or the roadmap asks for several tours on one page.
