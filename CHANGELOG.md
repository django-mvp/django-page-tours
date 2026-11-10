# Changelog

All notable changes to this project are documented in this file. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- **Breaking:** a tour is named where it is declared, and the name is required:
  `Tour(name="dashboard", steps=[...])`. The name is what a browser remembers a seen tour by and
  what `PAGE_TOURS_OVERRIDES` is keyed by, in place of the dotted path of the view that declared
  the tour. Renaming or moving a view no longer brings its tour back, and the view's path is no
  longer in the page source. A reusable app names its tours `"<app_label>.<tour>"`.
- **Breaking:** every tour plays once more after upgrading, in every browser that had seen it,
  because what a browser remembered was stored under the old, view-based names.
- **Breaking:** the keys of `PAGE_TOURS_OVERRIDES` are tour names now. Replace each view path
  with the name the app gives its tour, such as `{"library.book": "myproject.tours.book_tour"}`.
  A replacement tour needs a name of its own too, and still plays under the name of the tour it
  replaces.
- `page_tours.W002` now warns about an override key that names no declared tour, rather than one
  that no routed view declares a tour under.

### Added

- System check `page_tours.W005` warns when tours with different steps are declared with one
  name, since they would share what a browser remembers.
- A demo page, "Function view", shows a tour passed in a function-based view's context.

### Removed

- **Breaking:** `with_tour`. A function-based view passes its tour in the template context
  instead: `render(request, "dashboard.html", {"tour": DASHBOARD_TOUR})`.
- **Breaking:** `page_tours.tours.tour_id` and `page_tours.tours.declaring_view_name`, along with
  the rule that named a tour after the first class along a view's method resolution order to set
  `tour`.
- The system check `page_tours.W001`. The package no longer needs
  `django.template.context_processors.request`.

## [v0.2.0] - 2026-11-10

### Added

- A tour can be given a version, `Tour(version=2)`. A browser that saw another version of the tour
  plays it by itself once more, and is then quiet again. A tour without a version is at version 1,
  and tours seen before this release count as seen at version 1. Editing a tour without changing
  its version brings it back to nobody. The demo project has a page for a tour at a new version.
- A project can replace the tour of an installed app, or turn it off, with the
  `PAGE_TOURS_OVERRIDES` setting, which maps a tour's name to the dotted path of a `Tour` or to
  `None`. A mistake in the setting is refused when the project starts, and `page_tours.W002`
  warns about a key that names no tour. The demo project has a small library app whose tours
  it changes.
- Every part of a shown tour step has a documented class name, from `page-tour-box` to
  `page-tour-highlight`, so a site can style the tour from its own stylesheet.
- The `PAGE_TOURS_CLASSES` setting gives parts classes of your own, for every step of every tour.
  An empty string gives a part none.
- System checks `page_tours.W003`, for a part that does not exist, and `page_tours.W004`, for a
  value that is not a string of class names. A wrong entry is ignored when the page renders.
- A design system installed as an app can supply classes for the parts as defaults, with
  `page_tour_classes` on its `AppConfig`. The project's `PAGE_TOURS_CLASSES` replaces them part by
  part, and between apps the first in `INSTALLED_APPS` wins. The checks name the app an entry came
  from.
- A demo page, "Own look", shows a tour with a look of its own.

### Changed

- Driver.js's stylesheet is now imported into a cascade layer named `page-tours`, the lowest on
  the page. A site's rules outside any layer win over it whatever their order. A site's element
  rules, such as `button { ... }`, and a framework's layered reset now reach the tour's parts as
  they reach the rest of the page. Style the documented names to settle any of it.

## [v0.1.0] - 2026-11-10

### Added

- The package skeleton: an installable Django app with its test suite, CI and release flow.
- A demo project in `demo/` and the documentation site, with installation and contributing pages.
- A tour for a page: `Tour` and `TourStep` declare it, `tour` on a class-based view or
  `with_tour` on a function-based view attaches it, and `{% page_tour %}` in the base template
  plays it when the page opens. A mistake in a declared tour raises `ImproperlyConfigured`.
- A visitor can move through a tour with next, back and close. A step whose element is missing,
  hidden or named by an invalid selector is skipped, a tour with nothing to show does not play,
  and a tour that fails ends and leaves the page usable. With JavaScript off the page is
  unchanged.
- A tour page in the demo project, at `/tour/`, showing each kind of step.
- A tour plays by itself the first time a browser opens its page, and not again in that browser.
  Which tours a browser has seen is kept in its local storage only, per declaring view; a
  browser that blocks storage sees the tour on every visit.
- A replay control: `{% page_tour_replay %}` places a button, with your own content and
  attributes, that plays the page's tour again from its first step. It shows only on pages with
  a tour and only with JavaScript on.
- A tour declared with `autoplay=False` does not play by itself and plays only when a visitor
  uses a replay control. The demo project has a page for a tour that plays once and a page for
  one that plays only on request.
- Tours can be followed with the keyboard and a screen reader. When a tour ends, focus goes back
  to where it was before the tour started, at any step and however the tour ends.
- A tour's own controls (next, previous, done and the close button's label) are shown in the
  language the page is served in. The package ships an English catalogue for its strings in
  `page_tours/locale/en/`, which a project translates like the rest of its site.
- The system check `page_tours.W001` warns when the request context processor is missing.
- Driver.js 1.10.2 is shipped as a static file, so nothing is loaded from a CDN. sha256 of
  `driver.js.iife.js`: `541520f33f84cc5cf6696b421f705cc9efe2d72656b3b5cd7f72c22e6d7e17c0`; of
  `driver.css`: `ff1934a5a7ef3f50deb9266ba8945b3eb407ee10b97da12feda4b7c10055bf12`.
