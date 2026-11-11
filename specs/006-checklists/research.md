# Research — FS-006 A checklist

## Assumptions checked

Run before the specification was written. `main` has no checklist and still ships Driver.js
1.10.2, so the surfaces the specification hands something new to were read from Driver.js
1.11.0's checklist build as vendored on the prototype branch
(`page_tours/static/page_tours/vendor/driver.js-1.11.0/checklist.iife.js`).

- **The checklist build takes the completed items as a plain option.** It seeds its done set from
  `completed` and reports every change through `onProgress` with the full list. Holds, so the app's
  report (FR-005) and the browser's ticks (FR-008) can both be handed to it as one list.
- **It keeps nothing between page loads.** The build never touches `localStorage`. Holds, so the
  package keeps the ticks itself (FR-008), through the shared browser memory FS-005 builds.
- **An item's tour may be a Driver.js instance.** The build drives an item's `tour` as given when
  it is already a driver, and calls the instance's own `onDestroyed` before deciding the item from
  how the tour ended. Holds, so a tour built by the package's shared tour builder keeps its
  element lookup, part classes and seen record when a checklist starts it (FR-003, FR-009), as
  long as the tour's cleanup is in `onDestroyed` (issue #46).
- **A link item is ticked when followed.** An item with an `href` and no tour is an anchor, and
  the build ticks it on activation. Holds (FR-007).
- **Per-item and checklist-wide manual ticking.** `allowManualComplete` is read on the item first,
  then on the checklist. Holds (US1 scenario 5).
- **Opening and closing from the page.** The instance exposes `toggle`, and `launcher` can be
  turned off. Holds (FR-010).
- **The prototype's screens.** The checklist on every page of the demo and the book page's
  borrow action that ticks an item from the app are served from the prototype branch. Both pages
  return 200 and carry the checklist's payload element. Holds.

Not checked here, because they do not exist on `main` yet: the shared bases, browser memory and
entry point FS-005 builds, and the `Tour` fields of pull request #43. The build checks them on the
main it starts from.
