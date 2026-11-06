# Research — FS-002 Seen tours and replay

Read against `main` after the tour on a page (issue #5) merged.

## What this feature extends

- `Tour` (`page_tours/tours.py`) is a frozen dataclass holding `steps`. `Tour.for_page(context)`
  finds the page's tour: a class-based view's `tour` attribute through `context["view"]`, or the
  tour `@with_tour` put on `request.page_tour` (ADR 0001).
- `{% page_tour %}` renders `page_tours/page_tour.html`: when the page has a tour, Driver.js's
  stylesheet and script, the starter script `page-tours.js`, and the steps as JSON in
  `<script id="page-tour-steps">`. A page with no tour gets nothing.
- `page-tours.js` builds the Driver.js steps, plays the tour when at least one step is showable,
  and on any error tears down everything Driver.js added. Step titles and texts arrive escaped,
  because Driver.js writes them as HTML (FS-001 D8). This stays as it is.
- Seen is recorded when the tour starts (FR-002), so nothing depends on Driver.js reporting how
  a tour ended.

## Decisions for the build

### Where seen is kept: `localStorage`, one key per tour

The browser's `localStorage` keeps a value per origin with no expiry, which is what "seen in this
browser" means. `sessionStorage` would forget at the end of the tab, and a cookie would be sent to
the server on every request, against FR-005. Every call to it is wrapped in `try`/`catch`: a
blocked-storage setting throws on access, and a full store throws on write. A read that throws
counts as not seen, so the tour plays (FR-006).

Key: `page-tours:seen:<tour id>`, value `"1"`.

### What identifies a tour: the view that declares it

FR-004 needs an identity for a tour that is the same on every address its view renders, and the
edge cases need it unchanged when the tour's steps change (showing a changed tour again is R7).

- **A hash of the steps** changes when a step is edited, so an edited tour would play again.
  That is R7's behaviour, which this feature must not have. Not adopted.
- **A name the developer gives each tour** contradicts FR-012 and US3 scenario 7: playing once
  must need no setting. Not adopted.
- **The view that declares the tour**, as its dotted path. Adopted. For a class-based view it is
  the class whose own body sets `tour`, found along the method resolution order, so a subclass
  that inherits its parent's tour shares the parent's seen state, and one that sets its own tour
  has its own. For a function-based view it is the decorated function, recorded by `@with_tour`.
  The same view on many addresses is one tour (FR-004). A class-based view whose tour no class
  body holds (set on the instance or through `as_view(tour=...)`) takes its own class's path. Renaming or moving the view makes the
  tour unseen again, which is the one cost, documented in the developer guide.

The identity travels to the browser in the JSON the tag already emits. Nothing is stored on the
server (FR-005).

### Playing only on request: `Tour(..., autoplay=False)`

A boolean field on `Tour`, default `True`, so a tour declared as today plays once by itself
(FR-012, SC-005: the declaration alone changes it). `autoplay` is the word HTML uses for media
that starts by itself.

### The replay control: a block tag that renders an inert `<template>`

`{% page_tour_replay class="…" %}…{% endpage_tour_replay %}`, placed anywhere in the developer's
templates (FR-007).

- On a page with no tour it renders nothing (FR-008, US2 scenario 4).
- On a page with a tour it renders `<template data-page-tour-replay>` holding
  `<button type="button" …>` with the developer's content and attributes. The starter script
  puts a copy of that button in place of each `<template>`. A `<template>`'s content is never
  shown and never in the accessibility tree, whatever the site's CSS says, so with JavaScript off
  no control appears (FR-008, US2 scenario 5). The `hidden` attribute was considered and turned
  down: a site class such as `display: inline-flex` overrides it, and the control would show with
  JavaScript off.
- A native `<button>` is reachable and operable by keyboard (FR-010). Its accessible name is its
  content. A developer whose content is an icon gives `aria_label="…"`, which the tag renders as
  `aria-label` (template tag argument names cannot carry a hyphen, so every `_` in a name
  becomes `-`).
- The tag is Django's `Library.simple_block_tag`, which parses the keyword arguments, passes
  the rendered block as `content` and refuses positional arguments. Attributes are rendered with
  `django.forms.utils.flatatt`, which escapes them. The package adds no class and no style (FR-011). An empty block renders the
  translatable text "Show the tour" (Article VIII).
- Placed several times, each copy starts the tour (edge case).

### Replaying

The control calls the same start function as autoplay, from the first step (FR-009). When a tour
is already playing (`isActive()`) it is destroyed first and started again, so two copies never
draw over each other. A replay records seen like any play, and does not change whether the tour
plays by itself later (FR-013). If no step is showable when the control is used, nothing happens
(US2 scenario 7).

While a step is showing, Driver.js's overlay covers the page and holds keyboard focus in the
popover (FS-001 D20), so a visitor can use the control during a tour only when a step points at
it. The edge case "replay while playing restarts" holds wherever the control can be reached.

Driver.js calls checked in the vendored `driver.js.iife.js` 1.10.2: `isActive()` returns
`isInitialized`; `destroy()` skips `onDestroyStarted` and still calls `onDestroyed`; `drive(0)`
initialises and shows the first step; a second `driver()` replaces a previous instance; the Tab
handler cycles focus only between the popover and the active element.

### Recording seen when the tour starts

Seen is written immediately after `drive()` returns without throwing, and only when some step
was showable, so a tour that never started is not seen (US1 scenario 9). Recording at the start
covers leaving the page mid-tour (FR-002).

### The earlier specification

FS-001's FR-010 and its clarification on how often a tour plays describe a tour playing every
time its page opens. This feature changes that, so both are edited in this pull request to read
as they now are.

## Planning notes

The spec directory has no `planning-notes.md`.

## What already exists

| Piece | Where the search stopped |
|---|---|
| Remembering seen in the browser | the browser: `localStorage` |
| Hiding the control without JavaScript | the browser: `<template>` |
| Keyboard operation and accessible name | the browser: `<button type="button">` |
| Rendering the developer's attributes, escaped | Django: `django.forms.utils.flatatt` |
| Finding the page's tour for the control tag | this repo: `Tour.for_page` |
| Starting, stopping and restarting the tour | an installed package: Driver.js `drive()`, `isActive()`, `destroy()` |
| Tour identity from the declaring view | new code: a few lines in `Tour.for_page` and `with_tour` |
| Parsing the block tag's arguments and content | Django: `Library.simple_block_tag` |
| Autoplay check, seen record and replay wiring | new code, in the existing `page-tours.js` |
