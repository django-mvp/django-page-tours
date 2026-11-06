# Implementation Plan: A tour on a page

**Branch**: `001-tour-on-a-page` | **Date**: 2026-11-06 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/001-tour-on-a-page/spec.md`, research in
[research.md](research.md)

## Summary

A developer declares a `Tour` of `TourStep`s in Python: as a `tour` attribute on a class-based
view, or with the `with_tour()` decorator on a function-based view. A site places the
`{% page_tour %}` tag once in its base template. The tag finds the view the request resolved to,
and when that view has a tour it emits Driver.js's stylesheet and script, the package's own
starter script, and the steps as escaped JSON. The starter script hands the steps to Driver.js
with missing and hidden elements skipped, and ends the tour cleanly on any failure. A page whose
view has no tour gets nothing from the tag.

## Technical Context

**Language/Version**: Python 3.12 and 3.13, Django 5.2, 6.0, 6.1. Browser JavaScript (ES2020,
no build step).
**Primary Dependencies**: Django only. Driver.js 1.10.2 vendored as static files.
**Storage**: None. No models, no migrations (FR-014).
**Testing**: pytest-django for rendered HTML and Python behaviour; pytest-playwright (Chromium)
against `live_server` for what only a browser shows.
**Target Platform**: any Django site; evergreen browsers.
**Project Type**: reusable Django app.
**Constraints**: nothing loaded from another origin; no CSS framework classes in emitted markup;
a page without a tour is byte-for-byte unaffected by the tag.

## Constitution Check

| Article | How this plan meets it |
|---|---|
| I Testing | Every acceptance scenario has a test (task list). No test of wording or layout |
| II Simplicity | Two dataclasses, one decorator, one tag, one check, one script. No settings |
| III Anti-abstraction | No base view, no mixin, no registry. The tour is a class attribute or a function attribute |
| V Security | Titles and texts are escaped with `django.utils.html.escape`, then embedded with `json_script`. No hand-built markup |
| VI Documentation | Developer guide page, installation page, index, README and CHANGELOG change in the stories that introduce each name |
| VII Dependencies | No new runtime dependency. Driver.js is a vendored static file |
| VIII i18n | The package has no user-facing strings of its own in this feature beyond the app's `verbose_name`, already wrapped. The check's message is wrapped. Developer strings are rendered with `str()` under the active language |
| X Cohesion | Tour lookup is a classmethod on `Tour`, beside the declaration it reads |
| XII Stack | Driver.js at 1.10.2, path carries the release, licence beside it |
| XIII Never breaks its page | Missing and hidden elements skipped; any failure ends the tour and clears Driver.js's markup; the tag emits nothing visible |
| XIV No look of its own | Driver.js's stylesheet only. Emitted markup has an id for the steps' JSON and no classes |

## Design

### Declaring a tour (`page_tours/tours.py`)

```python
@dataclass(frozen=True)
class TourStep:
    title: StrOrPromise
    text: StrOrPromise
    element: str = ""          # a CSS selector; empty means attached to nothing

@dataclass(frozen=True)
class Tour:
    steps: Sequence[TourStep]

    @classmethod
    def for_view(cls, view) -> "Tour | None": ...
    def as_driver_steps(self) -> list[dict]: ...

def with_tour(tour: Tour) -> Callable[[F], F]: ...
```

- **Validation at declaration (FR-004).** `TourStep.__post_init__` raises `ImproperlyConfigured`
  when `title` or `text` is empty. `Tour.__post_init__` raises `ImproperlyConfigured` when
  `steps` is empty, and stores `steps` as a tuple so a declared tour cannot change later. Tours
  are declared at import time, so the error appears when the project starts, before any visitor.
  An empty `element` is the same as none.
- **Class-based views (FR-002).** A class attribute: `tour = Tour(steps=[...])`, read the way
  `template_name` is. No mixin is needed because nothing is read from the instance.
- **Function-based views (FR-002).** `@with_tour(Tour(...))` sets `view.tour` and returns the
  same function. It sits under any `login_required`-style decorator or over it: `functools.wraps`
  copies the attribute (research, "How the tag finds the page's tour").
- **`Tour.for_view(func)`** returns `func.view_class.tour` when the function came from
  `as_view()`, otherwise `func.tour`, otherwise `None`. `getattr` with a default throughout. A
  non-`Tour` value is ignored (returns `None`).
- **`Tour.as_driver_steps()`** returns one dict per step, in the declared order:
  `{"title": escape(str(title)), "text": escape(str(text))}`, plus `"element": selector` when the
  step has one. `str()` runs at render time, so the active language applies (FR-005).
  `escape()` makes Driver.js's `innerHTML` show the characters as text (FR-006, research).
- Exported from `page_tours/__init__.py`: `Tour`, `TourStep`, `with_tour`. Importing the package
  imports no models, so this is safe at settings time.

### The one-time setup (`page_tours/templatetags/page_tours.py`)

`{% load page_tours %}{% page_tour %}`, placed once in the base template's `<head>`. An
inclusion tag, `takes_context=True`, template `page_tours/page_tour.html`.

- Reads `context.get("request")`, then `request.resolver_match` (absent on error pages and
  outside a request), then `Tour.for_view(resolver_match.func)`. Any of them missing → the tag
  renders an empty string (FR-007, edge cases).
- With a tour, the template emits, and nothing else:

  ```django
  {% load static %}
  <link rel="stylesheet" href="{% static 'page_tours/vendor/driver.js-1.10.2/driver.css' %}">
  {{ steps|json_script:"page-tour-steps" }}
  <script src="{% static 'page_tours/vendor/driver.js-1.10.2/driver.js.iife.js' %}" defer></script>
  <script src="{% static 'page_tours/page-tours.js' %}" defer></script>
  ```

  `defer` keeps the order and runs both after the document is parsed. The stylesheet styles only
  Driver.js's own classes, so with JavaScript off it changes nothing on the page (FR-009).
- `{% static %}` resolves against the site's own `STATIC_URL`, so every file comes from the site
  (FR-008, SC-003). A site that sets `STATIC_URL` to a CDN is its own choice and outside "another
  origin" in the sense the spec means: the package itself names no other origin.

### Missing request context processor (`page_tours/checks.py`)

A system check registered in `PageToursConfig.ready()`, `page_tours.W001`, a `Warning` when no
`DjangoTemplates` backend lists `django.template.context_processors.request`, modelled on
`admin.W411`. The message is wrapped for translation (Article VIII). Without it the tag can never
find a tour, and the developer would get no sign of it.

### Vendored Driver.js (`page_tours/static/page_tours/vendor/driver.js-1.10.2/`)

`driver.js.iife.js`, `driver.css` and `LICENSE`, copied byte for byte from the npm archive of
`driver.js@1.10.2` (sha256 recorded in the CHANGELOG entry: `541520f3…e17c0` for the script,
`ff1934a5…bf12` for the stylesheet). The release is in the directory name, so moving to a new
release is one visible change (Article XII). Source on disk:
`/home/sam/projects/worktrees/driverjs-1.10.2/package/`.

### The starter script (`page_tours/static/page_tours/page-tours.js`)

An IIFE, no globals of its own, no build step:

1. Find `#page-tour-steps`. Missing, or `window.driver?.js?.driver` missing (the Driver.js file
   failed to load or static files were not collected) → return, page untouched (FR-009).
2. Parse the JSON. Map each step to `{popover: {title, description: text}}`, and for a step with
   an `element`, `element: () => visibleElement(selector)`, where `visibleElement` returns the
   first match of `document.querySelector(selector)` when it exists and
   `el.checkVisibility({visibilityProperty: true, opacityProperty: true})` is true (falling back
   to `el.getClientRects().length > 0` where `checkVisibility` is absent), and `undefined`
   otherwise, including when the selector is invalid and `querySelector` throws.
3. If no step is showable now (every step has an element and none resolves) → return; no tour
   plays (US2 scenario 6).
4. `driver({steps, skipMissingElement: true, showProgress: true})`, then `drive()`. Driver.js
   skips a step whose element function returns nothing as the tour reaches it, going forward and
   going back (research). The first step shown is the first showable one (FR-010).
5. **Failure (FR-013).** Starting is inside `try`. A `window` `error` listener is added just
   before `drive()` and removed in `onDestroyed`. On any exception while starting, and on any
   uncaught error while the tour is active, the script ends the tour: `destroy()` inside its own
   `try`, then it removes any element still carrying `driver-overlay`, `driver-popover` or the id
   `driver-dummy-element`, and the classes `driver-active`, `driver-fade`, `driver-simple`,
   `driver-active-element`, `driver-active-element-parent` and
   `driver-active-element-parent-no-scroll` wherever they remain. Ending the tour on any
   uncaught error while it is active, not only Driver.js's own, is deliberate: the page outranks
   the tour (Article XIII), and telling Driver.js's errors from others is not reliable.

### Demo page (`demo/`)

`TourView(TemplateView)` at `/tour/`, named `tour`, linked from the page bar in
`demo/templates/base.html`. Its tour has a welcome step attached to nothing, a step attached to
an element on the page, a step attached to an element that is not on the page, and a closing
step attached to a second element. The page has its own working controls (a `<details>`
disclosure and a text field with a submit button posting to the same page) so a visitor can see
the page still works during and after the tour. `base.html` gets `{% load page_tours %}` and
`{% page_tour %}` in `<head>`, which is the one-time setup. The overview page stops saying no
tours are built. Demo strings are plain, never marked for translation (Article VIII).

### Tests

| Module | Subject |
|---|---|
| `tests/test_tours.py` | `TestTourStep`, `TestTour`, `TestWithTour`: validation, order, lookup for CBV, FBV, wrapped views, escaping, translation |
| `tests/test_templatetags/test_page_tours.py` | `TestPageTourTag`: rendered pages through `client`, with test views in `tests/views.py` and templates in `tests/templates/` |
| `tests/test_checks.py` | `TestRequestContextProcessorCheck` |
| `tests/test_apps.py` | the check is registered (existing module, new test) |
| `tests/test_static/test_page_tours_js.py` | browser behaviour of the starter script, through `live_server` and Playwright. Declared in `[tool.forge.conformance] non-mirror-paths` as `tests/test_static/` |
| `tests/test_demo.py` | the demo tour page responds, is linked from the bar, and its tour carries the three kinds of step; one browser test walks it (SC-002) |

Test pages for the browser tests live in `tests/views.py`, `tests/urls.py` and
`tests/templates/` (added to `TEMPLATES[0]["DIRS"]` in `tests/settings.py`), each a minimal page
with one or two controls and a tour shaped for the scenario. Faults are injected from the test
with Playwright, never from package code:

- **Script cannot load**: `page.route` aborts the Driver.js file.
- **Fails while starting**: `page.route` fulfils the Driver.js file with a stand-in whose
  `driver()` returns an object whose `drive()` adds `div.driver-overlay` to `body`, adds
  `driver-active` to `body`, then throws.
- **Fails while playing**: the test page's own inline script makes its second step's element
  throw from `getBoundingClientRect`, which Driver.js calls when it highlights the element; the
  test moves forward onto it.
- **JavaScript off**: a context with `java_script_enabled=False`; the same template rendered by a
  view with the tour and by one without; `inner_text("body")` and every element's bounding box
  in `body` are equal between the two (SC-004).

After every fault, the test asserts no element with a `driver-` class or the dummy id remains,
`body` has no `driver-` class, and the page's own control still works (SC-005).

`DJANGO_ALLOW_ASYNC_UNSAFE=true` goes in `[tool.pytest.ini_options] env` (research). The tests
run under xdist as the verify step does.

## Project Structure

```text
page_tours/
├── __init__.py                      # exports Tour, TourStep, with_tour
├── apps.py                          # ready() registers the check
├── checks.py
├── tours.py
├── templatetags/__init__.py
├── templatetags/page_tours.py
├── templates/page_tours/page_tour.html
└── static/page_tours/
    ├── page-tours.js
    └── vendor/driver.js-1.10.2/{driver.js.iife.js,driver.css,LICENSE}
demo/  views.py, urls.py, templates/base.html, templates/demo/{overview,tour}.html
tests/ test_tours.py, test_checks.py, test_apps.py, test_demo.py, views.py, urls.py,
       settings.py, templates/…, test_templatetags/{__init__,test_page_tours}.py,
       test_static/{__init__,test_page_tours_js}.py
docs/  developer/tours.md (new), developer/installation.md, developer/index.md, index.md
README.md, CHANGELOG.md, pyproject.toml (pytest env, non-mirror path)
```

## Outside this branch

CI needs `install-playwright: true` on the call to the shared tests workflow in
`.github/workflows/tests.yml` for the browser tests to run there. That file is not changed by
this plan's tasks.

## Complexity Tracking

| Addition | Why it is needed | Simpler alternative rejected because |
|---|---|---|
| `page_tours.W001` check | Without the request context processor the tag can never find a tour, silently | Documenting it alone leaves a misconfigured site with no tour and no sign why |
| Clearing Driver.js's classes after a failed `destroy()` | FR-013: nothing of the tour left in the way when Driver.js itself has failed | Trusting `destroy()` fails exactly when Driver.js is the thing that broke |
