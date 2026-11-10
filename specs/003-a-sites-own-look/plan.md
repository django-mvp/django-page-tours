# Implementation Plan: A site's own look for its tours

**Branch**: `003-a-sites-own-look` | **Date**: 2026-11-10 | **Spec**: [spec.md](spec.md)

**Input**: [spec.md](spec.md), [research.md](research.md), [planning-notes.md](planning-notes.md)

## Summary

Every part of a shown step gets a class the package documents, `page-tour-<part>`, added by the
starter script from Driver.js's `onPopoverRender` hook. The same hook adds the classes a project
configures for each part in one setting, `PAGE_TOURS_CLASSES`, or that an installed app supplies
as defaults on its `AppConfig`. Driver.js's stylesheet, unchanged, is imported into a cascade
layer that the starter script keeps first in the document, so any rule a site writes outside a
layer, and any layered framework rule, beats Driver.js's defaults wherever it is linked. A wrong
configuration is reported by system checks as warnings and ignored at render time.

## Technical Context

**Language/Version**: Python 3.12+, Django 5.2, 6.0, 6.1; plain ES5-style JavaScript in the
starter script, as today.

**Primary Dependencies**: Driver.js 1.10.2 (shipped, unchanged). No new dependency.

**Storage**: none.

**Testing**: pytest with pytest-django; rendered-HTML tests for the payload and the tag;
Playwright browser tests (`tests/test_static/test_page_tours_js.py`) for what the starter script
does and for the cascade.

**Target Platform**: any Django project; evergreen browsers (cascade layers are supported in every
browser Driver.js 1.10.2 supports).

**Project Type**: reusable Django app (library).

**Constraints**: a strict content security policy (`style-src 'self'`, `script-src 'self'`) keeps
working, so no inline style or script is added. A tour never breaks its page (Article XIII).

**Scale/Scope**: nine parts, one setting, one `AppConfig` attribute, two new check ids.

## Constitution Check

| Article | How the plan meets it |
|---|---|
| I Testing | every behaviour task is test-first; the cascade is tested in a browser because a contract (FR-003) decides it |
| II Simplicity, III Anti-abstraction, X Cohesion | one class, `TourParts`, groups the parts and the lookup of their classes, with no base class, registry or hierarchy; the app defaults are an attribute Django's own registry already orders |
| V Security | class values travel in the existing `json_script` payload and are added with `classList`, never written as HTML (FR-007) |
| VI Documentation | a developer page, README public surface, CHANGELOG, glossary, all in this pull request |
| VIII i18n | check messages are translatable, as `W001` is |
| XI Compatibility | the part names, the setting, the `AppConfig` attribute and the check ids become public surface, listed in the README |
| XII Stack norms | `driver.css` and `driver.js.iife.js` stay byte-identical; nothing is loaded from another origin |
| XIII Never breaks its page | bad configuration is skipped at render; a failure while naming the parts ends the tour through the existing `endTour` |
| XIV No look of its own | `page-tours.css` holds one `@import` and no rules; the package emits no framework class |

No violations. Complexity tracking: none.

## Project Structure

### Documentation (this feature)

```text
specs/003-a-sites-own-look/
├── spec.md
├── decisions.md
├── planning-notes.md
├── research.md
├── plan.md
└── tasks.md
```

### Source Code

```text
page_tours/
├── parts.py                         # new: TourParts, the parts, their names and their classes
├── checks.py                        # + W003, W004
├── templatetags/page_tours.py       # payload gains "parts"
├── templates/page_tours/page_tour.html   # links page-tours.css instead of driver.css
└── static/page_tours/
    ├── page-tours.css               # new: @import of driver.css into layer page-tours
    └── page-tours.js                # moves the stylesheet first, names and classes the parts

tests/
├── test_parts.py                    # new
├── test_checks.py
├── test_templatetags/test_page_tours.py
├── test_static/test_page_tours_js.py
├── design_system/                   # new: a test app supplying defaults (US2)
├── other_design_system/             # new: a second one, for precedence (US2)
├── templates/                       # test pages with a site stylesheet before and after the tag
├── views.py, urls.py
└── test_demo.py

demo/                                # an "own look" page, settings with classes
docs/developer/styling-tours.md      # new
README.md, CHANGELOG.md, CONTEXT.md
```

## Design

### The parts

`page_tours/parts.py` holds one class, `TourParts` (Article X: the parts, their names and the
lookup of their classes share one subject). Its class attribute `parts` is the one list of parts,
in this order: `("box", "title", "text", "progress", "previous", "next", "done", "close",
"highlight")`. `TourParts.name(part)` gives the documented name.
Each part's documented name is `page-tour-<part>`: `page-tour-box`, `page-tour-title`,
`page-tour-text`, `page-tour-progress`, `page-tour-previous`, `page-tour-next`, `page-tour-done`,
`page-tour-close`, `page-tour-highlight`. The names are built in Python only and sent to the
browser, so the list exists once. The starter script holds only the mapping from each element
Driver.js hands it to a part key, which is Driver.js's shape, not a second list of names.

### Classes for the parts

`TourParts.classes()` returns a dict with every part as a key and, as its value, the list of class
tokens that part carries: its documented name first, then its configured classes split on
whitespace. For each part the classes come from the first source below that has a valid entry for
it:

1. the project setting `PAGE_TOURS_CLASSES`, a dict from part to a string of class names;
2. each installed app's `AppConfig.page_tour_classes`, the same shape, in the order
   `django.apps.apps.get_app_configs()` returns them, which is `INSTALLED_APPS` order.

A valid entry is a known part whose value is a `str`. An empty string is valid and means "no
classes": a project can clear an app's classes for one part. Anything else is skipped at render
and reported by the checks: an unknown part, a value that is not a `str`, a setting or an
attribute that is not a dict. `TourParts.classes()` never raises.

`TourParts.sources()` yields `(source, mapping)` in that precedence order, where `source` names where
the mapping came from for messages ("the PAGE_TOURS_CLASSES setting", "the app 'label'"). Both
`TourParts.classes()` and the checks read it, so the two can never disagree about precedence.
Computed on every render, never cached, so `override_settings` and app changes in tests apply.

### The tag's payload

`page_tour` adds `"parts": TourParts.classes()` to the payload it already sends through
`json_script`. A page with no tour still carries nothing (US1-10).

### The stylesheet layer

`page_tours/static/page_tours/page-tours.css` contains exactly:

```css
@import url("vendor/driver.js-1.10.2/driver.css") layer(page-tours);
```

`page_tour.html` links it in place of `driver.css`, with a `data-page-tour-stylesheet` attribute
the starter script finds it by. The relative URL resolves beside the file, so it works under any
`STATIC_URL` and with `ManifestStaticFilesStorage`, which rewrites `@import` URLs.

### The starter script

Three additions to `page-tours.js`, inside its existing guards:

1. **The layer goes first.** Before anything else, find `link[data-page-tour-stylesheet]` and, if
   it is not already the first child of `<head>`, `document.head.prepend()` it. The `page-tours`
   layer is then declared before any layer of the site's and is the lowest of all.
2. **Naming the parts.** An `onPopoverRender(popover, opts)` option on the `driver({...})` call
   adds `payload.parts[part]` with `classList.add(...)` to: `popover.wrapper` (box),
   `popover.title`, `popover.description` (text), `popover.progress`, `popover.previousButton`,
   `popover.nextButton` (as `done` when `opts.driver.isLastStep()`, as `next` otherwise),
   `popover.closeButton`, and the overlay `document.querySelector("svg.driver-overlay")`
   (highlight). Only classes are added: no attribute, text, role or tabindex is touched (FR-005).
   Driver.js builds a new box per step, so this runs on every step, the first, the last, an
   unattached one and a replayed one alike (FR-011).
3. **The highlight gives way to site rules.** A `MutationObserver` on `document.body`, started
   with the tour, names the overlay when Driver.js adds it (D18), because Driver.js draws the
   first step's box before it creates the overlay. When the overlay's `path` carries inline
   `fill` or `opacity`, those move onto the `svg` as the `fill` and `fill-opacity` attributes
   and leave the path's inline style. `fill-opacity` rather than `opacity`, because Driver.js's
   fade-in animates the `svg`'s own opacity and the dimming has to multiply into it. With no
   site rule the overlay looks as before.

The popover hook and the overlay watcher each run inside a guard. On any error the guard ends the
tour from a microtask with the existing `endTour()`, so whatever Driver.js adds after the failing
call is removed too, and focus is restored (edge case, Article XIII).

### System checks

Two warnings in `page_tours/checks.py`, registered as `W001` is, both from `TourParts.sources()`:

- `page_tours.W003` — an entry names a part the package does not have. The message names the
  part and the source, and the hint lists the parts.
- `page_tours.W004` — a value is not a string of class names, or the setting or attribute is not
  a dict. The message names the part (when there is one) and the source.

Warnings, never errors: an error stops `runserver`, and FR-008 says a styling mistake never stops
a page with a tour from rendering.

### Design-system defaults (US2)

An app supplies defaults by declaring, on its `AppConfig`:

```python
class MyDesignConfig(AppConfig):
    name = "my_design"
    page_tour_classes = {"box": "card", "next": "btn btn-primary"}
```

Its rules against the documented names live in its own stylesheet, loaded by its own base
template, and need nothing from the package (US2-2). Tests use two apps under `tests/`,
installed with `override_settings(INSTALLED_APPS=...)`.

### Documentation and demo

- `docs/developer/styling-tours.md`, in the developer toctree: the table of parts and names;
  styling from the site's stylesheet, with the cascade layer explained in one paragraph (rules
  outside a layer win; a framework's layered rules win too); giving parts classes with
  `PAGE_TOURS_CLASSES`, including the empty string; how a design system supplies defaults on its
  `AppConfig`, and the precedence; the check ids.
- README: the names, the setting, the `AppConfig` attribute and `W003`/`W004` listed as public
  surface; a short "Styling" pointer to the page.
- CHANGELOG `[Unreleased]`: Added (names, setting, app defaults, checks); Changed (Driver.js's
  stylesheet now sits in the `page-tours` cascade layer, so a site's element rules such as
  `button { … }`, and a framework's layered reset, now reach the tour's parts as they reach the
  rest of the page; the site styles the documented names to settle any of it).
- `CONTEXT.md`: "Part of a step" and "Highlight" under Tour step (D10).
- Demo: `demo/settings.py` sets `PAGE_TOURS_CLASSES` for a few parts with `demo-` classes; a new
  "Own look" page (`demo/templates/demo/own_look.html`, view, URL, nav link) whose `head` block
  styles the documented names and the `demo-` classes, and whose tour has an attached and an
  unattached step. `tests/test_demo.py` covers the page as it covers the others.

## Watch items

- If the cascade assertions are flaky on the first step, start the tour from the moved link's
  `load` event when `prepend()` actually moved it, and at once when it was already first.
- If ending the tour from inside the render hook raises a page error, end it from a
  `queueMicrotask` in the `catch` instead.
- The pull request description says, in one line, that the package now links a one-line
  stylesheet whose only content is the import of Driver.js's (D11), so the merge gate sees the
  reading of FR-006.

- No leading-underscore names anywhere; line length 88; no compatibility aliases.
- No test of wording or design preference. The cascade tests assert that a site's rule takes
  effect on the part it names (a contract), never what the default looks like.
- Existing tests that select Driver.js's own classes keep working; the new names are added beside
  them, never in place of them.
- A parallel change to `page-tours.js`, the template tags and `tours.py` is being built for issue
  #21. Keep edits to those files local to the hook, the payload key and the link.
