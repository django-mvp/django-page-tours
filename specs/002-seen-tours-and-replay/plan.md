# Implementation Plan: Seen tours and replay

**Branch**: `002-seen-tours-and-replay` | **Spec**: [spec.md](spec.md) |
**Research**: [research.md](research.md)

## Summary

A tour plays by itself once per browser and is then seen. The starter script records seen in
`localStorage` under the identity of the view that declares the tour, the moment the tour starts.
A tour declared with `autoplay=False` plays only on request. A new block tag,
`{% page_tour_replay %}`, renders the developer's own button inside an inert `<template>` on
pages that have a tour, and the starter script turns each one into a working button that plays
the tour from its first step.

## Technical Context

- **Language**: Python 3.12+, Django 5.2, 6.0 and 6.1; plain JavaScript (ES5 style, as the
  existing starter script) in the browser.
- **Dependencies**: none added. Driver.js 1.10.2 stays as vendored.
- **Storage**: the visitor's `localStorage` only. No models, no migrations.
- **Testing**: pytest-django for Python and rendered HTML; pytest-playwright (Chromium) for
  browser behaviour, as FS-001's `tests/test_static/test_page_tours_js.py`.

## Constitution Check

- **Article V (escaping)**: step text stays pre-escaped by `Tour.as_driver_steps()`. The
  control's attributes go through `flatatt`, its content through the template engine.
- **Article VIII (translation)**: the control's fallback text is `gettext_lazy`.
- **Article XIII (the page stays usable)**: every storage call and every replay path is inside
  `try`/`catch`, and a failure tears the tour down with the existing `endTour()`.
- **Article XIV (no look of its own)**: the control carries only the developer's attributes.
  No CSS is added.
- No database tables (FR-005, SC-003).

## Design

### Tour identity (`page_tours/tours.py`)

- `with_tour(tour)` sets `request.page_tour_view` to the decorated view's dotted path,
  `f"{view.__module__}.{view.__qualname__}"`, alongside `request.page_tour`, and removes both
  if the view raises.
- New module-level function `tour_id(context) -> str`, called only for a page whose
  `Tour.for_page(context)` is not `None`:
  - a class-based view: walk `type(context["view"]).__mro__` and return the dotted path of the
    first class whose own `__dict__` holds `tour`;
  - a class-based view where no class in the MRO holds `tour` (set on the instance, or through
    `as_view(tour=...)`): the dotted path of `type(view)`. Per-URL tours on one class therefore
    share that class's seen state;
  - otherwise `request.page_tour_view`.
- `Tour.for_page` is unchanged (ADR 0001 stands).

### Playing only on request (`page_tours/tours.py`)

`Tour` gains `autoplay: bool = True` after `steps`. Nothing else changes in the dataclass.

### The tag's payload (`page_tours/templatetags/page_tours.py`, `page_tour.html`)

`{% page_tour %}` emits one JSON object in `#page-tour-steps`, replacing the bare list:

```json
{"id": "demo.views.TourView", "autoplay": true, "steps": [...]}
```

The script element keeps its id. `steps` is `as_driver_steps()` as today. A page with no tour
still emits nothing.

### The replay control (`page_tours/templatetags/page_tours.py`)

`{% page_tour_replay [name=value ...] %}content{% endpage_tour_replay %}`, declared with Django's
`@register.simple_block_tag(takes_context=True)` as
`def page_tour_replay(context, content, **attrs)` (Django 5.2 and later, the package's floor).
Django parses the `name=value` arguments, resolves them against the context, passes the rendered
block as `content`, and raises `TemplateSyntaxError` on a positional argument.

- Returns `""` when `Tour.for_page(context)` is `None`.
- Otherwise returns, with `format_html`:

  ```html
  <template data-page-tour-replay><button type="button"{attrs}>{content}</button></template>
  ```

  `attrs` is `flatatt` of the arguments with every `_` in a name turned into `-`, so
  `aria_label="…"` renders `aria-label` and `data_x` renders `data-x`. `content` is the block, or
  `gettext_lazy("Show the tour")` when the block is only whitespace. A `type` given by the
  developer is dropped (the button is always `type="button"`, so it never submits a form).

### The starter script (`page_tours/static/page_tours/page-tours.js`)

Kept: step building, `visibleElement`, `endTour()`, the error listener. Changed:

- Parse the payload object. Nothing to do if it has no steps.
- `isSeen()` and `markSeen()` wrap `localStorage.getItem` / `setItem` on
  `"page-tours:seen:" + payload.id` in `try`/`catch`. A throwing read returns `false`; a
  throwing write is ignored.
- `start()`:
  1. return when no step is showable (checked now, not at load, so elements that appeared later
     count);
  2. if a tour is active, destroy it. This happens before the new driver is created and before
     `window.addEventListener("error", endTour)`: the old driver's `onDestroyed` removes that
     listener, so destroying it later would strip the new tour's listener;
  3. create the driver as today and `drive()`;
  4. `markSeen()`.
  Any throw → `endTour()`.
- At load, first: for each `template[data-page-tour-replay]`, insert a deep clone of its
  content's first element before it, add a `click` listener that calls `start()`, and remove the
  `<template>`. This comes before autoplay, so a step that points at the control finds it.
- At load, then: when `payload.autoplay` and not `isSeen()`, `start()`.

### FS-001's specification (`specs/001-tour-on-a-page/spec.md`)

FR-010 and the clarification "How often does the tour play" are rewritten to read as they now
are: a tour plays by itself the first time its page opens in a browser that has not seen it,
as FS-002 describes. Nothing else in that file changes.

### Demo (`demo/`)

- `base.html`: `{% page_tour_replay %}Show the tour{% endpage_tour_replay %}` in the header
  nav, once, so it shows on every page that has a tour and on no other.
- Two new pages, each a `TemplateView` with its own template, linked from the header nav:
  - `/plays-once/` — a tour that plays once, with the replay control from the base template;
  - `/on-request/` — a tour declared with `autoplay=False`, with a second replay control placed
    in the page body next to its heading, carrying a class of the demo's own.
- `overview.html` names the two pages.
- `seed_demo` needs nothing new.

### Documentation (`docs/developer/`)

A new guide page, `replaying-a-tour.md`, in the Guides toctree after `tours`: a tour plays once
per browser, what counts as seen, that seen is keyed by the declaring view (renaming it shows the
tour again), placing `{% page_tour_replay %}` with your own content and attributes, `aria-label`
for an icon-only control, and `autoplay=False`. `tours.md` loses or corrects any sentence that
says a tour plays every time its page opens. CHANGELOG `[Unreleased]` gains the feature.

### Tests

- `tests/test_tours.py`: `tour_id` for a class-based view, a subclass inheriting the tour, a
  subclass declaring its own, a view whose tour no class holds, and a function-based view; `with_tour` cleans up
  `page_tour_view` on raise; `autoplay` defaults to `True`.
- `tests/test_templatetags/test_page_tours.py`: the payload carries `id`, `autoplay` and
  `steps`; two URLs of one view carry the same id; the replay tag renders nothing on a page
  with no tour, renders a `<template data-page-tour-replay>` holding a `<button type="button">`
  with the given attributes and content and no other class on a page with a tour, escapes
  attribute values, renders `aria_label` as `aria-label`, falls back to the translatable text when empty, and raises
  `TemplateSyntaxError` on a positional argument.
- `tests/test_static/test_page_tours_js.py` (browser): plays on first open, not after reload;
  not after closing mid-tour; not after leaving mid-tour; a different tour still plays; one view
  on two URLs is seen once; storage blocked (an init script that makes `localStorage` throw)
  plays every visit with no page error; a nothing-showable tour is not seen; replay plays from
  step one on a seen tour; replay after the end works again; replay does not change autoplay on
  the next visit; the control shows only on pages with a tour; with JavaScript off no control is
  visible; the control is reached and pressed with the keyboard; replay on a nothing-showable
  tour leaves no Driver.js markup and no page error; `autoplay=False` does not play on first open
  and plays from the control; two controls on one page both start it; replay while a step points
  at the control restarts from step one.
- `tests/test_apps.py`: the app has no models, and a page with a tour sets no cookie
  (FR-005, SC-003).
- Tests never assert on wording or layout (`docs/contributing/standards/testing.md`).

## Project Structure

```text
page_tours/
├── tours.py                         # autoplay, tour_id, with_tour records the view
├── templatetags/page_tours.py       # payload object, page_tour_replay block tag
├── templates/page_tours/page_tour.html
└── static/page_tours/page-tours.js  # seen, autoplay, replay
demo/  views.py  urls.py  templates/base.html  templates/demo/{overview,plays_once,on_request}.html
docs/developer/  index.md  tours.md  replaying-a-tour.md
docs/adr/  NNNN-a-tour-is-seen-per-declaring-view.md
specs/001-tour-on-a-page/spec.md     # FR-010 and one clarification, current state
tests/  views.py  urls.py  templates/  test_tours.py  test_templatetags/  test_static/  test_demo.py
```

## Complexity Tracking

None. No new dependency, no model, no setting.
