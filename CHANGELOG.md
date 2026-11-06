# Changelog

All notable changes to this project are documented in this file. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- The package skeleton: an installable Django app with its test suite, CI and release flow.
- A demo project in `demo/` and the documentation site, with installation and contributing pages.
- A tour for a page: `Tour` and `TourStep` declare it, `tour` on a class-based view or
  `with_tour` on a function-based view attaches it, and `{% page_tour %}` in the base template
  plays it when the page opens. A mistake in a declared tour raises `ImproperlyConfigured`.
- The system check `page_tours.W001` warns when the request context processor is missing.
- Driver.js 1.10.2 is shipped as a static file, so nothing is loaded from a CDN. sha256 of
  `driver.js.iife.js`: `541520f33f84cc5cf6696b421f705cc9efe2d72656b3b5cd7f72c22e6d7e17c0`; of
  `driver.css`: `ff1934a5a7ef3f50deb9266ba8945b3eb407ee10b97da12feda4b7c10055bf12`.
