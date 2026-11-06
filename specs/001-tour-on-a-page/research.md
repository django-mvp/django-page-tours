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

## Planning notes

The specification directory has no `planning-notes.md`, so there are no planning suggestions to
answer.

## Driver.js 1.10.2

Read from the published archive (`npm pack driver.js@1.10.2`), the latest release on 2026-11-06.
Quotations are from `package/dist/driver.js.iife.js`.

- **The browser build sets one global.** The file opens with
  `this.driver=this.driver||{},this.driver.js=(function(e){…})`, so a page that loads it gets
  `window.driver.js.driver(config)`, which returns the tour object with `drive()`, `destroy()`,
  `isActive()`, `moveNext()` and `movePrevious()`.
- **A step's title and description are written as markup.** The popover code assigns
  `n.title.innerHTML=i` and `n.description.innerHTML=a`. A developer's string reaching Driver.js
  unchanged would be interpreted as markup, so FR-006 needs the strings escaped before they reach
  the browser.
- **A step with no element is shown on its own**, centred over the page on a placeholder element
  (`driver-dummy-element`). That is FR-003's step attached to nothing.
- **Driver.js skips a missing element itself, when asked.** The configuration has
  `skipMissingElement` (default `false`). The check runs as the tour reaches each step, in both
  directions: `function I(e,t){return!(t.skipMissingElement??e.getConfig("skipMissingElement"))
  ||!t.element?!1:!p(t.element)}` with `p(e)` resolving `e` as a function's return value, a
  selector through `document.querySelector`, or an element. A step whose `element` is a function
  returning nothing is therefore skipped too, which is how a hidden element can count as missing
  (FR-012) without a second mechanism.
- **Driver.js's own markup carries its own class names** (`driver-overlay`, `driver-popover`,
  `driver-active` on `body`, `driver-active-element` on the highlighted element) and
  `destroy()` removes them. That is how "nothing of the tour left in the way" is checked.
- **Licence.** `package/license`, MIT, copyright Kamran Ahmed.

## How the tag finds the page's tour

The tour belongs to the view that renders the page (CONTEXT.md, Tour), so the one-time setup in
the base template must find the view without the view passing anything to its template.

- **`request.resolver_match` is the wrong source.** It names the view the URL resolved to, and
  it stays set when that view raises: `django/core/handlers/base.py` sets it in
  `resolve_request` before calling the view, and the 404 and 403 handlers render their page with
  the same request (`django/views/defaults.py`, `page_not_found` and `permission_denied`). A
  lookup through it would play a page's tour on the error page shown instead of that page,
  including to a visitor refused permission.
- **A class-based view's own rendering carries the view.** `ContextMixin.get_context_data` puts
  the instance in the context as `view` (`django/views/generic/base.py`), and an error handler's
  context has no `view`.
- **A function-based view's rendering can carry it on the request**, set by a wrapping decorator
  and removed if the view raises. Django's own view decorators wrap with `functools.wraps`, so
  stacking with `login_required` and the like keeps working.
- `request` is in a template's context only with `django.template.context_processors.request`.
  Django's own project template enables it, and the admin already checks for it with a warning
  (`django/contrib/admin/checks.py`, `admin.W411`). Without it the tag cannot find a
  function-based view's tour and would play none without a word to the developer.

## Browser tests

- `pytest-playwright` 0.9.0 and `playwright` 1.64.1 come with the `mvp-shared[test]` bundle and
  Chromium is installed locally. pytest-django's `live_server` serves static files when
  `django.contrib.staticfiles` is installed.
- Playwright's sync API runs an event loop in the test thread, which makes Django refuse database
  access from it. `DJANGO_ALLOW_ASYNC_UNSAFE=true` in the test environment is the documented
  answer (pytest-env is in the bundle).
- **CI does not install a browser yet.** `.github/workflows/tests.yml` calls the shared tests
  workflow without `install-playwright: true`, whose default is `false`. The browser tests need
  that input set.

## What already exists

| New piece | Where the search stopped |
|---|---|
| `Tour` and `TourStep` declarations | 7, new code. Nothing in the repo, its dependencies or Django declares a guided tour |
| Attaching a tour to a class-based view | 4, Django: a class attribute read from the `view` the generic views put in the context, the way `template_name` is declared |
| Attaching a tour to a function-based view | 7, new code: a decorator that marks the request while the view runs. Nothing in Django attaches data to a view function's rendering |
| The tag placed once in the base template | 4, Django: an inclusion tag |
| Getting the steps to the browser safely | 4, Django: the `json_script` filter, after `django.utils.html.escape` |
| Drawing the tour, moving through it, closing it | 6, Driver.js 1.10.2, vendored |
| Skipping a missing or hidden element | 6 then 5: Driver.js's `skipMissingElement`, with the browser's `Element.checkVisibility()` deciding hidden |
| Ending a failed tour and clearing what it left | 7, new code: a short script of ours around Driver.js |
| Warning when the request context processor is missing | 4, Django's system check framework, as the admin does |
| The demo page | 2, the demo's existing `TemplateView` pattern and base template |
