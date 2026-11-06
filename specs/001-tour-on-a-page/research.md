# Research — FS-001: A tour on a page

## Assumptions checked

The specification assumes these already work. Each was run or read on 2026-11-06.

- **The demo project is served.** Its overview page answers 200 from `main`. Its base
  template has a `head` block and a `content` block, so the one-time setup and the demo page's
  tour have a place to go.
- **Driver.js can ship as a static file with no build step.** The published `driver.js` package at
  1.10.2 is MIT-licensed and its archive carries ready-built files: `dist/driver.js.iife.js` (a
  browser script that needs no bundler), `dist/driver.css` and `license`. FR-008 needs nothing
  more.
- **No feature code exists yet.** `page_tours/` holds only its app configuration, so nothing in
  this feature extends an existing surface.
