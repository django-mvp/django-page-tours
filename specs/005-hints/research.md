# Research — FS-005 Hints on a page

The full research is written when the feature is planned. This file holds only what was run
before the specification gate.

## Assumptions checked

- **Driver.js 1.11.0's hints build takes the options the specification mirrors.** Read the
  shipped `hints.iife.js` from `driver.js@1.11.0` (on the prototype branch until issue #46 lands
  it): `onDismiss`, `setHints`, `buttonText`, `showButton`, the beacon's `animate`, `className`,
  `offsetX` and `offsetY`, `popoverOffset`, `overlayColor` and `overlayOpacity` are all read.
  Confirmed.
- **Beacons are keyboard reachable.** Each beacon is a `<button type="button">` with
  `aria-haspopup="dialog"` and `aria-expanded`, and the popover is a dialog labelled by its title.
  Confirmed by reading the build. A beacon whose hint has no title is named with Driver.js's own
  English text, which the package does not translate. Passed to research (`planning-notes.md`).
- **No beacon pulses under reduced motion.** `hints.css` turns the pulse animation off under
  `prefers-reduced-motion: reduce`. Confirmed.
- **A tour on the page puts hints aside.** The hints build watches for the class Driver.js puts on
  the page while a tour plays and closes an open hint. Whether the beacons are hidden too is not
  settled by reading the build. To confirm in the browser at planning; if they stay visible, FR-015
  is a requirement the package meets itself.
- **The prototype's hints page renders.** `http://devserver:8037/hints/` returns 200 with the
  hints payload element, the restore control and the hints build. Confirmed.
