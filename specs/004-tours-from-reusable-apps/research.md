# Research — FS-004 Tours shipped by reusable apps

## Assumptions checked

Run on `main` at `b32f9f7` before the specification was written.

- **A tour declared in another installed app plays in the project.** The demo project in `demo/`
  is an installed app separate from `page_tours`, and its views declare tours the way a reusable
  app's would. `uv run pytest tests/test_demo.py`: 22 passed, including its tour pages. Holds.
- **A project's subclass of an app's view keeps the app's tour name.** A subclass of
  `demo.views.OnRequestView` that sets no tour of its own is named
  `demo.views.OnRequestView` by `tour_id`. Holds, so scenario 6 can be met by naming the app's
  view.
- **A mistaken tour is refused when declared.** `Tour(steps=[])` and a `TourStep` with an empty
  title raise `ImproperlyConfigured` at construction (`page_tours/tours.py`). Holds, so FR-010
  follows from the existing rule when the replacement is built at start-up.

## Planned on `main` at `14bb333`

Tour versions (#21) merged as #29 before planning: `Tour(version=...)` is a whole number, 1 by
default, and the browser stores the version that played as the value under the existing key
`page-tours:seen:<name>` (ADR 0003). A browser holding any other version plays the tour once.

### Where the project's change lives

- **A setting, `PAGE_TOURS_OVERRIDES`.** Adopted. A mapping from a tour's name to the dotted path
  of the project's replacement, or to `None` to turn the tour off. Django already uses this
  shape for the same job: `MIGRATION_MODULES` maps an installed app to a replacement module, or
  to `None` to turn its migrations off. The project's settings are where a developer already
  looks for what the project changes about its installed apps, and one setting answers both
  halves of FR-002 and FR-003.
- **A call in the project's code** (a registry the project fills in its `AppConfig.ready`). Not
  adopted. It needs a place to be called from and an order relative to other apps' `ready`, and
  it is global state a test has to reset. The setting needs neither.
- **The replacement itself in settings.** Not possible: a replacement that reuses the app's steps
  imports the app's views, and settings load before the app registry. So the setting holds a
  dotted path, resolved with `django.utils.module_loading.import_string`, as Django resolves
  `FORM_RENDERER` and `DEFAULT_EXCEPTION_REPORTER`.

### How a version meets a replacement (decisions.md D4, D12)

What the browser compares is the version of the tour the page emits (`page-tours.js` compares the
stored value to `String(payload.version)` for equality). A browser that saw the app's tour at
version 2 holds `"2"`. Three readings were weighed:

- Emit the replacement's own version. A replacement left at 1 plays once for everyone who saw the
  app's tour at 2. Against FR-008. Not adopted.
- Emit the app tour's version. The project can never show its replacement again. Against FR-004.
  Not adopted.
- Count the replacement's version on from the app tour's: `app + replacement - 1`. A replacement
  at 1 plays at the app's version, so FR-008 holds at any app version; raising it shows it again.
  An app release that raises its own version also shows the replacement again once, which is
  where it gives up D4's starting reading. Adopted.

### Listing the declared tours for the check (FR-009)

`django.urls.get_resolver()` and each `URLResolver.url_patterns`, walked recursively, give every
routed callback. A class-based view's callback carries `view_class` and `view_initkwargs`
(Django's `View.as_view`), so its tour name comes from the same rule `tour_id` applies. A
function-based view's wrapper carries nothing today, so `with_tour` records the name it already
computes on the wrapper as well as on the request. `django.contrib.admindocs.views` has a walk of
the same shape, `extract_views_from_urlpatterns`, but importing it pulls in `django.contrib.admin`
and `django.contrib.auth`, which a project need not install. The walk is a dozen lines.

## What already exists

- Resolving a dotted path to an object: Django, `django.utils.module_loading.import_string`.
- A replacement or `None` per name, read from settings: Django's own `MIGRATION_MODULES` shape.
  New code is the lookup in `Tour.for_page`, three lines.
- Refusing a mistaken replacement: this repo, `Tour.__post_init__` and `TourStep.__post_init__`
  already raise `ImproperlyConfigured`. New code is only importing every replacement at start-up,
  in `PageToursConfig.ready`, so the import happens then.
- A tour's name: this repo, `tour_id` (ADR 0002). Nothing new.
- Keeping a replacement's seen state: this repo, the name is the declaring view's and the starter
  script keys on it. New code is the version arithmetic, `dataclasses.replace` (standard library).
- Hiding the replay control on a page whose tour is off: this repo, `page_tour_replay` already
  renders nothing when `Tour.for_page` returns `None`. Nothing needed.
- Reporting a stale change: Django's system check framework, as `page_tours.W001` already uses.
  New code is the check and the URL walk, for which no installed package offers a dependency-free
  equivalent.
