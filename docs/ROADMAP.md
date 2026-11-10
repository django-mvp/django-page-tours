# Roadmap — django-page-tours

**Date:** 2026-11-06

This document was designed against [GOALS.md](../GOALS.md). See also [CONTEXT.md](../CONTEXT.md) for domain terminology and [CONSTITUTION.md](../CONSTITUTION.md) for project standards.

## Versioning

| Version | Gate |
|---|---|
| `0.0.x` | Building toward the Essential goals. Pre-viable, expect churn, nothing published |
| **`0.1.0`** | **All Essential goals delivered.** The minimum usable release, and the first published to PyPI |
| `0.1.x` → `0.x` | Advancing the Expected goals, at whatever granularity the work takes. Patches are fixes |
| **`1.0.0`** | **All Expected goals delivered.** The complete, dependable release |
| `1.x` | Stable line: non-breaking fixes and additive features only |
| `2.0` | Next major: breaking changes |

A goal is not one minor release: some take several, and one minor release can move two. Once `1.0` ships, a breaking change never goes out as `1.x`. It waits for the next major.

*Aspirational goals may be developed against v2 or v1 as required.*

## Essential goals: v0.1.0

Everything needed for a site to give one of its pages a working tour.

### R1 — A tour on a page

*delivered in [#5](https://github.com/django-mvp/django-page-tours/issues/5) · advances G1, G3, G4*

The core of the package: a developer declares a tour for a page in Python, next to the view that renders the page, and the tour plays when the page opens. Each step has a title and a short text, and either points at one element of the page or stands on its own as a card in the middle, which suits a welcome. Driver.js draws the tour and arrives with the package, so a site needs no front-end tooling and loads nothing from another origin. Everything later in this roadmap builds on it.

**Deliverables:**
- A tour declared in Python for a page, as an ordered list of steps, with no JavaScript written by the developer.
- Steps attached to an element, and steps attached to nothing.
- The visitor can move forward and back through the steps, and close the tour at any point.
- A step whose element is not on the page is skipped, and a failing tour leaves the page as it was.
- A page with JavaScript off renders as if it had no tour.
- Driver.js and its stylesheet shipped as static files, with their licence.

Serves G1, G3 and G4. Out of scope: remembering who has seen a tour (R2), styling beyond Driver.js's own (R5), tours that span several pages.

### R2 — Seen tours and replay

*delivered in [#6](https://github.com/django-mvp/django-page-tours/issues/6) · advances G2*

A tour that plays on every visit becomes something people learn to close without reading. Once R1 can play a tour, the next need is for it to play once for each visitor and then stay quiet, while leaving a way to see it again. Whether a tour has been seen is kept in the visitor's browser, so the package still adds no database tables.

**Deliverables:**
- A tour plays on its own the first time a page is opened in a browser, and not again once it has been seen, whether it was finished, skipped or closed.
- A replay control a site can place anywhere on the page, shown only where the page has a tour.
- A developer can make a tour play only from the replay control, never on its own.

Serves G2. Out of scope: seen state that follows a signed-in person across browsers, and showing a changed tour again (R7).

## Expected goals: v1.0.0

What a complete, dependable tour package is expected to offer once the core works.

### R3 — Tours for keyboard and screen-reader users

*delivered in [#16](https://github.com/django-mvp/django-page-tours/issues/16) · advances G5*

A tour can be started, followed and closed from the keyboard alone, focus moves into each step and back to where it was when the tour ends, and a screen reader announces each step's title and text. Serves G5.

### R4 — Tours in the visitor's language

*delivered in [#18](https://github.com/django-mvp/django-page-tours/issues/18) · advances G6*

Step text and the tour's own controls (next, back, close, the step count) are shown in the language the page is served in, with a base English catalogue shipped for projects to translate. Serves G6.

### R5 — A site's own look for its tours

*delivered in [#22](https://github.com/django-mvp/django-page-tours/issues/22) · advances G7*

A site restyles its tours with its own CSS, and a design system built on Django can style tours once for every site that uses it, without editing the package's templates. Serves G7. Out of scope: a design shipped by this package.

### R6 — Tours shipped by reusable apps

*delivered in [#23](https://github.com/django-mvp/django-page-tours/issues/23) · advances G8*

A reusable Django app declares tours for its own pages, and a project that installs it can change those tours or turn them off without editing the app. Serves G8.

### R7 — Showing a changed tour again

*delivered in [#21](https://github.com/django-mvp/django-page-tours/issues/21) · advances G9*

A developer gives a changed tour a new version where they declare it, and a browser that saw another version plays it by itself once more. A small edit that keeps the version brings it back to nobody. Serves G9.
