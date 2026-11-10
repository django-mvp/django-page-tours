# Implementation Plan: Tours shipped by reusable apps

**Branch**: `004-tours-from-reusable-apps` | **Spec**: [spec.md](spec.md) |
**Research**: [research.md](research.md)

## Summary

A project changes an installed app's tour with one setting, `PAGE_TOURS_OVERRIDES`, that maps the
tour's name (the dotted path of the view that declares it, ADR 0002) to the dotted path of a
replacement tour, or to `None` to turn it off. `Tour.for_page` applies the setting after it finds
the declared tour, so the tag, the replay control and the seen state all follow without change.
Every replacement is imported when the project starts. A new system check, `page_tours.W002`,
reports a name in the setting that no routed view declares a tour under.

## Technical Context

- **Language**: Python 3.12+, Django 5.2, 6.0 and 6.1. No change to the starter script.
- **Dependencies**: none added.
- **Storage**: none. No models, no migrations.
- **Testing**: pytest-django for Python and rendered HTML, pytest-playwright (Chromium) for the one
  browser scenario, as the existing suites.

## Constitution Check

- **Article II (simplicity)**: one setting, read where the tour is already found. No registry,
  no new module.
- **Article III (anti-abstraction)**: the setting has Django's `MIGRATION_MODULES` shape and
  resolves with `import_string`.
- **Article VI (documentation)**: a new guide page, the README, CHANGELOG and `CONTEXT.md` in
  this pull request.
- **Article VIII (translation)**: the new error and warning messages are `gettext_lazy`.
- **Article XIII (a tour never breaks its page)**: a mistaken setting fails at start-up, never
  while a page renders.

## Design

### The setting

```python
PAGE_TOURS_OVERRIDES = {
    "shop.views.CartView": "myproject.tours.cart_tour",
    "shop.views.order_history": None,
}
```

- Key: a tour's name, the dotted path `tour_id` gives (ADR 0002). For a class-based view, the
  class whose own body declares `tour`. For a function-based view, the function `with_tour`
  decorates.
- Value: a dotted path to a `Tour`, or `None`. Anything else is refused.
- Absent setting: `{}`.

### Resolving the setting (`page_tours/tours.py`)

- `resolve_override(name, value) -> Tour | None`: `None` returns `None`; a string is resolved
  with `import_string` and must be a `Tour`. Raises `ImproperlyConfigured`, naming the key, when
  the value is neither a string nor `None`, when the path does not import (catch `ImportError`
  only, and chain it; a replacement module whose `Tour(...)` raises propagates its own
  `ImproperlyConfigured` unchanged), or when it names something other than a `Tour`.
- `tour_overrides() -> dict[str, Tour | None]`: every entry of
  `getattr(settings, "PAGE_TOURS_OVERRIDES", {})` through `resolve_override`. Used at start-up.
- `Tour.for_page(context)`: finds the declared tour as today. When there is one and its name,
  `tour_id(context)`, is a key of the setting, it resolves only that entry. `None` turns the tour
  off. A replacement is returned at its played version (below). Otherwise the declared tour. Not
  cached, so a test that changes the setting sees the change at once (D13).
- `tour_id` keeps its rule, moved into `declaring_view_name(view_class)`, which returns the dotted
  path of the first class along `view_class.__mro__` whose own `__dict__` holds `tour`, or of
  `view_class` when none does. `tour_id` and the check both call it, so the rule is stated once.
  A replaced tour keeps its name and therefore its seen state (FR-008).
- `PageToursConfig.ready` calls `tour_overrides()` once, after registering the checks, so every
  mistake in the setting, including a replacement module whose `Tour(...)` raises, fails when the
  project starts (FR-010).

### The version a replaced tour plays at

A replacement's version counts on from the app tour's: the page emits the replacement with
`version = app tour's version + replacement's version - 1`, built with `dataclasses.replace`.

- A replacement left at version 1 plays at the app tour's version, so a visitor who saw the app's
  tour at any version does not see the replacement by itself (FR-008, scenario 9, SC-004).
- Raising the replacement's version shows it again (FR-004: a replacement carries what a tour
  carries).
- Turning a tour off and on changes nothing stored, so it resets nobody.
- An app release that raises its own tour's version shows the replacement again once. The app's
  author said the page changed enough, so the project's visitors see the project's tour of it
  again.

### The tag and the replay control

No change. `{% page_tour %}` emits the tour `Tour.for_page` returns under the name `tour_id`
gives, with the replacement's `autoplay` and `version`. A tour turned off makes `for_page`
return `None`, so the tag emits nothing and `{% page_tour_replay %}` renders nothing (scenario 4).

### The stale-change check (`page_tours/checks.py`)

- `with_tour`'s decorator sets `page_tour_view` on the wrapper it returns, the same path it puts
  on the request, sync and async.
- `declared_tour_names(patterns) -> set[str]`: walks the given URL patterns, recursing into every
  `URLResolver.url_patterns`. For each `URLPattern.callback`: `page_tour_view` first, when the
  callback has it; otherwise, with `view_class`, when `view_initkwargs.get("tour")` or
  `getattr(view_class, "tour", None)` is a `Tour`, the name `declaring_view_name(view_class)`
  gives. The same rule as `tour_id`, from the same helper.
- `check_overrides_name_declared_tours`, registered with `checks.Tags.urls`: for each key of the
  setting not in `declared_tour_names(get_resolver().url_patterns)`, one
  `checks.Warning(..., obj=<key>, id="page_tours.W002")`, the message naming the key and the hint
  saying a view that was renamed or moved gives its tour a new name. Silent when the setting is
  absent or empty. It reads the raw keys and does not resolve values, so a bad value is reported
  once, by `ready`.

### Demo project

A second installed app in the demo stands for a reusable app: `demo/library/` (`apps.py`,
`views.py`, `templates/library/…`, `__init__.py`), label `library`, listed in
`INSTALLED_APPS`. Its pages extend the demo's `base.html`, and each declares a tour:

- `BookListView` at `/library/books/`: plays as the app declared it.
- `BookDetailView` at `/library/book/`: the project replaces it with `demo.tours.book_tour`, a
  tour that reuses the app's steps with the second reworded.
- `LoansView` at `/library/loans/`: the project turns it off.

`demo/settings.py` sets `PAGE_TOURS_OVERRIDES` for the last two, with a comment saying the
library app is untouched. The overview page links the three pages with one line each.
`demo/tours.py` holds the replacement. These are new files, so the sibling feature's edits to the
demo's own pages do not meet them, except in `overview.html`, `settings.py` and `urls.py`.

### Documentation

- `docs/developer/tours-from-reusable-apps.md`, in the Guides toctree after `replaying-a-tour`:
  for an app author, ship tours by declaring them on the app's views as in any project, and treat
  moving or renaming a view that declares a tour, or raising its version, as a change projects
  see; for a project, find a tour's name, replace it (reusing the app's steps), turn it off, how
  a replacement's version counts on from the app's, and what `W002` means, including that it
  reads the root URLconf only.
- `docs/developer/tours.md`, "Seen tours": one sentence that a tour's name is also how a project
  changes it, linking the new page.
- README: one line in the feature list. CHANGELOG `[Unreleased]`: one entry.
- `CONTEXT.md`: **Tour name** (the dotted path of the declaring view, how it is seen and how a
  project changes it) and **Tour override** (a project's replacement for a tour, or its choice
  to turn it off). `_Avoid:_` customisation, patch.

### ADR

At S5, D3, D11 and D12 graduate as one ADR: a project changes an installed app's tour by its
name, in `PAGE_TOURS_OVERRIDES`, and the replacement plays at its own version. It makes ADR
0002's name part of what an app promises the projects that install it. Number claimed from
origin/main at the push.

## Tests

- `tests/views.py`: an app-like set of views for the overrides: `OverriddenTourView`
  (a `ControlsTourView` with its own tour), `OverriddenTourSubclassView` (sets no tour),
  `OffTourView`, `UntouchedTourView`, a function-based `overridden_function_view`, and the
  replacement tours as module constants; routes in `tests/urls.py`.
- `tests/test_tours.py`, `TestTourOverrides`: a replacement is what `for_page` returns; `None`
  turns it off; the replacement keeps `tour_id`; a subclass that sets no tour gets the change; a
  subclass that sets its own does not; a function-based view; `as_view(tour=...)` on the
  overridden class; another tour is untouched; each refusal of `tour_overrides()` (bad type,
  path that does not import, path to something that is not a tour); `ready` raises for a bad
  setting.
- `tests/test_templatetags/test_page_tours.py`, `TestOverriddenTourPayload`: the page's payload
  carries the replacement's steps, the declared id, and the version counted on from the app
  tour's; one step reworded among the app's steps
  arrives in order; a replacement with `autoplay=False` carries it; a turned-off page has no
  payload and no replay template; two URLs of the view both carry the change.
- `tests/test_static/test_page_tours_js.py`, `TestOverriddenTourSeen`, with the app's tour at
  version 2: having seen it, the replacement left at version 1 does not play by itself and the
  replay control plays it (scenario 9); a replacement at version 2 plays by itself once.
- `tests/test_checks.py`, `TestOverridesCheck`: `W002` for a name no routed view declares, with
  the name as `obj`; silent for a routed class, a routed subclass's inherited name, a function
  view, a view under `include()`, and a subclass that sets no tour routed with `as_view(tour=...)`
  under the name `tour_id` gives it; `W002` for that subclass's own name; silent with no
  setting.
- `tests/test_demo.py`: the library's untouched page carries its own steps, the replaced page
  carries the project's, the turned-off page carries no payload.
