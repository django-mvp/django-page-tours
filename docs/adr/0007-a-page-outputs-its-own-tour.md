# ADR 0007 — A page outputs its own tour

**Status:** accepted. Supersedes ADR 0001 and amends ADR 0006.

## Decision

A page's template outputs the page's tour with `{{ tour }}`, and nothing finds the tour for it.

- `Tour` renders itself. `Tour.__html__` returns the `<script id="page-tour-steps"
  type="application/json">` element the package's script plays the tour from, marked safe, and
  `Tour.__str__` returns the same, because Django's templates convert a value with `str()` before
  they escape it. That is the payload `{% page_tour %}` used to build: the name, the version,
  autoplay, the steps, the control labels in the active language and the classes of each part.
- `PAGE_TOURS_OVERRIDES` is applied when the tour renders. A replaced tour renders the
  replacement's steps under its own name, and a tour turned off renders an empty string.
- A view puts the tour in its template context like any other value: `extra_context` or
  `get_context_data` on a class-based view, the context passed to `render` in a function-based
  view.
- The host project includes the package's three static files itself, wherever it chooses:
  `page_tours/page-tours.css`, `page_tours/vendor/driver.js-1.10.2/driver.js.iife.js` and
  `page_tours/page-tours.js`. The script waits until the document is parsed, so the steps element
  can sit anywhere in the page and the scripts can be loaded with or without `defer`.
- The script finds the package's stylesheet by its path, `page_tours/page-tours.`, and moves it to
  the start of `<head>` before a tour plays (ADR 0005).
- A page has one tour. Should a template render `{{ tour }}` twice, the script plays the first
  element and leaves the second alone.

`{% page_tour %}`, the `page_tours` template tag library, its template, the `tour` attribute of a
class-based view and `Tour.for_page` are removed.

## Why

`{% page_tour %}` sat in the base template's `<head>`. Reading the page that declared a tour, it
was not clear what put the tour on the page or where it came from: the tag reached into the
context for `view.tour`, then for `tour`, then applied the overrides, all out of sight. A form
outputs its own assets with `{{ form.media }}`, and a developer already knows that shape. With
`{{ tour }}` the page template says where its tour is, and the view's context says which tour it
is, in the same way as every other value the page shows.

- **The rule that a tour never plays over an error page now holds by itself.** ADR 0001 read the
  tour only from what the view's own rendering put in the context, because the URL's view is
  still recorded when it raises. An error page renders its own template with its own context, so
  `{{ tour }}` there has no tour to render, whatever the error template extends.
- **The static files are the project's to place.** The tag added them only on a page with a tour.
  Included once in the base template, they load on every page, and the script does nothing on a
  page with no tour, so a replay control written with `hidden` stays hidden there.
- **`__html__` rather than a filter or a tag,** because it needs nothing loaded in the template
  and is the protocol Django already uses for values that render themselves.
- **The stylesheet is found by its path rather than by an attribute the developer has to write.**
  A hashed name from `ManifestStaticFilesStorage` still contains the path, and a link the
  developer forgot to mark would otherwise have left Driver.js's layer above the site's.

## Consequences

- Upgrading is a change in every project: include the three files, put `{{ tour }}` in each page
  template that has a tour, and move each view's `tour` into its context. The changelog lists the
  steps.
- A reusable app's page templates carry `{{ tour }}` themselves. The app no longer depends on the
  project's base template to place a tag, only to load the three files.
- The package's script and Driver.js load on pages that have no tour. Both are static files the
  browser caches.
- `str(tour)` is markup, not a description of the tour. `repr(tour)` still describes it.
- A subclass of a class-based view shares its parent's tour only through the context it inherits,
  such as `extra_context`, like any other value.

## Revisit if

- A page needs more than one tour.
- Django gains a standard way for a value in the context to declare the static files it needs.
