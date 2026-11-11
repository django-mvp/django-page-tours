# ADR 0009 — A tour plays the same wherever it starts

**Status:** accepted. Extends ADR 0008.

## Decision

A tour is one thing however a visitor reaches it. Wherever it starts, it starts from the same
payload and through the same code.

- In Python, anything that starts a tour carries the tour's own payload, the one
  `Declaration.payload()` returns, under the tour's own name and at the version
  `Declaration.playing()` gives it. A checklist item's tour reaches the browser in the exact shape
  of a page's own tour. `PAGE_TOURS_OVERRIDES` reaches it by the tour's name, and a tour turned off
  takes with it whatever would have started it.
- In the browser, `buildTour(payload, driver)` in the package's script builds every tour. It
  returns `start()` and `instance()`. The Driver.js instance is made on its first use, after the
  check that any step can show, and its `drive` is the package's start: the element lookup, the
  part classes, the overlay naming, the error guard, focus put back and the seen record. A page's
  own tour calls `start()`. A checklist hands `instance()` to Driver.js, which drives it.
- A tour has one seen record, `page-tours:seen:<name>`, whichever of these played it.
- A checklist keeps its ticks as `page-tours:ticked:<name>`, in the record shape ADR 0008 sets.
  What the app reports for a request is never stored.

## Why

Driver.js 1.11.0's checklist can start a tour from an item, and the specification asks that a
tour reached from a checklist behaves, looks and is remembered exactly as the same tour on its
page. The code that plays a page's tour carries every workaround the package needs for Driver.js:
finding elements that can be seen, skipping missing ones, naming the parts, cleaning up after an
error, putting focus back. A second copy for the checklist would drift from the first with the
next fix. One builder means a fix lands everywhere a tour plays.

Making the instance on first use keeps a promise the page's tour already made: a page's own tour
with nothing to show never asks Driver.js for anything. A checklist item's tour is handed to
Driver.js already made, because Driver.js starts it; with nothing to show, the package's start
declines and the item stays unticked.

## Revisit if

- Something starts a tour that cannot hand Driver.js an instance, or needs a tour to behave
  differently from a page's own.
- Driver.js stops driving a tour instance it is given and wants a plain configuration instead.
