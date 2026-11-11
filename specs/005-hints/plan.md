# Implementation Plan: Hints on a page

**Branch**: `005-hints` | **Spec**: [spec.md](spec.md) | **Research**: [research.md](research.md)

## Summary

A developer declares a page's hints as `Hints(name=…, hints=[Hint(…)], …)` and renders them with
`{{ hints }}`, the way a tour is declared and rendered. Three shared bases come first, in a new
module `page_tours/driver.py`: `DriverObject`, which turns a dataclass's fields into the object
Driver.js takes; `PopoverContent`, the popover fields a tour step and a hint share; and
`Declaration`, what a page renders, with its name, version, overrides and payload. `Tour` and
`TourStep` move onto them, and their own conversion code goes. In the browser, `page-tours.js`
gains one memory function for what a browser remembers, one popover part-classes function, and a
single entry point that plays the hints and the tour found on the page. Driver.js 1.11.0's hints
build, already vendored, draws the beacons, and its stylesheet hides them during a tour.

## Technical Context

- **Language**: Python 3.12+, Django 5.2, 6.0 and 6.1. JavaScript in the starter script, no build.
- **Dependencies**: none added. Driver.js 1.11.0's `hints.iife.js` and `hints.css` are vendored.
- **Storage**: none on the server. No models, no migrations. The browser's `localStorage`.
- **Testing**: pytest-django for Python and rendered HTML, pytest-playwright (Chromium) for
  browser behaviour, as the existing suites.

## Constitution Check

- **Article II (simplicity)**: three small bases, each with one job. No registry beyond the one
  that exists for tours, which moves.
- **Article III (anti-abstraction)**: each base has two uses in this feature (`Tour` and `Hints`;
  `TourStep` and `Hint`; five Driver.js objects) and a third in FS-006, an approved specification
  built in the same batch from the same prototype.
- **Article V (escaping)**: the payload goes through `json_script`. Text inside it is passed to
  Driver.js as it is, as a tour step's is (FR-006, D3).
- **Article VI (documentation)**: a new guide page, and the installation, styling, reusable-app
  and tours pages, README, CHANGELOG and `CONTEXT.md`, in this pull request.
- **Article VIII (translation)**: the new button text and every new message are lazy translated.
- **Article XI (compatibility)**: before 0.1.0. The renamed payload element, the moved functions,
  keyword-only declarations and the tour seen once more are in the changelog.
- **Article XIII (a page never breaks)**: each kind plays inside its own `try`. A missing hints
  script, blocked storage or a Driver.js error leaves the page as it would be without hints.

## Design

### `page_tours/driver.py` — the shared bases

```python
Side = Literal["top", "right", "bottom", "left"]
Alignment = Literal["start", "center", "end"]

def driver_value(value): ...        # DriverObject → as_driver(); tuple/list → list; Promise → str

@dataclass(frozen=True, kw_only=True)
class DriverObject:
    package_fields: ClassVar[frozenset[str]] = frozenset()
    nested: ClassVar[dict[str, frozenset[str]]] = {}
    def as_driver(self) -> dict[str, Any]: ...

@dataclass(frozen=True, kw_only=True)
class PopoverContent(DriverObject):
    title / description: str | Promise | None = None
    side: Side | None = None
    align: Alignment | None = None
    popoverClass: str | None = None
    popover_fields: ClassVar[frozenset[str]]   # the five names above

declared: dict[str, list[weakref.ref[Declaration]]]
def forget(name, ref): ...

@dataclass(frozen=True, kw_only=True)
class Declaration(DriverObject):
    name: str
    version: int = 1
    kind: ClassVar[str]                 # "tour", "hints"
    content_field: ClassVar[str]        # "steps", "hints": what W005 compares
    package_fields = {"name", "version"}
    def __post_init__(self): ...        # refuse name/version, record in `declared`
    def payload(self, version) -> dict  # {"kind", "id", "version", "parts", "config"}
    def __html__(self) / __str__(self)  # overrides, then json_script(…, f"page-tours-{kind}")

def resolve_override(name, value, cls=Declaration) -> Declaration | None
def declaration_overrides() -> dict[str, Declaration | None]
def declarations() -> dict[str, list[Declaration]]
```

- `as_driver()` creates every inner object named in `nested`, even when it stays empty (a step
  with no popover fields still carries `popover: {}`, which Driver.js needs to show its popover),
  then leaves out a package field and a `None`, converts each value with `driver_value`, and puts
  a field named in `nested` into that inner object. A `TourStep`'s
  popover fields go into `popover`, as `as_driver_steps` does today, and its `element`,
  `disableActiveInteraction`, `advanceOn` and `waitForElement` stay on the step.
- `Declaration.__post_init__` raises `ImproperlyConfigured` for a name that is not a non-empty
  string and a version that is not a whole number of 1 or more, with a message naming the class
  (`"%(cls)s needs a name."`). Subclasses check their own content first (a tour's steps), then call
  `super().__post_init__()`.
- `Declaration.__html__` does what `Tour.__html__` does today for any kind: the replacement of an
  entry in `PAGE_TOURS_OVERRIDES` renders in its place under this declaration's name, at this
  version plus the replacement's less one, or nothing when the entry is `None`. It resolves with
  `resolve_override(self.name, value, type(self))`, so a replacement of the wrong class raises
  `ImproperlyConfigured` naming the entry and the class it should be (FR-010).
- `resolve_override` keeps its present refusals and messages, with the class named in place of
  "Tour". `declaration_overrides()` and `declarations()` are `tour_overrides()` and
  `declared_tours()` renamed and moved. No aliases.
- No leading-underscore names: `_declared` and `_forget` become `declared` and `forget`.

### `page_tours/tours.py` — `Tour` and `TourStep` on the bases

- `TourStep(PopoverContent)`: its own fields after the five popover fields, unchanged in name,
  type and default, except `title` and `description`, which now default to `None` (left out, as
  `""` is today). `element` keeps its `""` default, which is sent, and the script drops a falsy
  `element` from the step it gives Driver.js (`document.querySelector("")` throws). `nested = {"popover": popover_fields | {showButtons, disableButtons,
  showProgress, progressText, nextBtnText, prevBtnText, doneBtnText}}`.
- `Tour(Declaration)`: `steps`, `autoplay`, then every Driver.js option as today. `kind = "tour"`,
  `content_field = "steps"`, `package_fields` adds `autoplay`. `__post_init__` refuses empty
  steps and freezes them. `payload()` adds `autoplay` to the base's.
- `PACKAGE_FIELDS`, `STEP_LEVEL_FIELDS`, `as_driver_steps`, `_declared`, `_forget`,
  `resolve_override`, `tour_overrides`, `declared_tours` and the payload code in `__html__` go.
- `Button` stays, and is documented on the tours page with the values `showButtons` takes (the
  verify docs step reports it undocumented at the base).

The tour's payload becomes:

```json
{"kind": "tour", "id": "…", "version": 1, "autoplay": true, "parts": {…},
 "config": {"steps": [{"element": "…", "popover": {…}}], "animate": true, …}}
```

in `<script id="page-tours-tour" type="application/json">`.

### `page_tours/hints.py` — `Hints`, `Hint`, `Beacon`

As the hand-over's item 2, every class keyword-only:

- `Beacon(DriverObject)`: `side`, `align`, `animate`, `className`, `offsetX`, `offsetY`, all
  `None` by default.
- `Hint(PopoverContent)`: `element` (required), `id`, `beacon`, `showButton`, `buttonText`, all
  `None` by default. `nested = {"popover": popover_fields | {"showButton", "buttonText"}}`.
- `Hints(Declaration)`: `hints` (required, frozen to a tuple), `beacon: Beacon | None = None`,
  `buttonText = GOT_IT_LABEL` (`pgettext_lazy("page hint control", "Got it")`),
  `popoverClass = ""`, `popoverOffset = 10`, `overlay = False`, `overlayColor = "#000"`,
  `overlayOpacity = 0.7`. `kind = "hints"`, `content_field = "hints"`.

`page_tours/__init__.py` exports `Beacon`, `Hint` and `Hints` beside `Tour` and `TourStep`.

### `page_tours/parts.py` and `page_tours/checks.py`

- `TourParts.parts` gains `"beacon"` (documented name `page-tour-beacon`). W003 and W004 cover it
  with no further code (FR-020).
- W002 reads `declarations()`. Its message speaks of a declaration under the name, not a tour.
- W005 groups every declaration under a name by `(type(declaration), getattr(declaration,
  declaration.content_field))`. More than one group is a warning: two tours with different steps,
  two sets of hints with different hints, or a tour and hints under one name (FR-009). A tour
  routed at two versions, or with a different `autoplay`, is still one group.
- `apps.py` calls `declaration_overrides()`.

### `page_tours/static/page_tours/page-tours.js`

Shared, at the top of the script:

- `visibleElement(selector)`, as today.
- `memory(kind, payload)`: `get()` returns the stored ids for `payload.version`, or `[]` when the
  entry is absent, of another version, not this shape, or unreadable; `set(ids)` stores
  `{version, ids}` and swallows a storage error; `clear()` removes the entry and swallows an
  error. Key `page-tours:<kind>:<payload.id>`.
- `addClasses(parts, element, part)` and `popoverParts(parts)`, the tour's `nameParts` made to
  take its parts and to tolerate a caller with no `driver` (a hint), naming the next button `next`
  there.

The tour (`playTour(payload)`): today's code, reading `page-tours-tour`, `payload.config.steps`
and `payload.config`'s options, deleting a falsy `element` from each step it maps, its seen record through `memory("seen", payload)` (seen is
`get().length > 0`, marked with `set([payload.id])`). Every workaround it carries for 1.11.0 stays.

The hints (`playHints(payload)`), when `window.driverHints` is there:

- `dismissed = memory("dismissed", payload)`. A hint's key is its `id`, else its `element`,
  worked out in the script only. The build's own `id` is left as declared (its default is the
  hint's index), so two hints on one element are both drawn and share their key.
- The hints shown are the declared ones not dismissed, each with its
  `popover.onPopoverRender` set to `popoverParts(parts)`, and its beacon's `className` set to the
  beacon part's classes, then the hint's own `className`, else the hints' `beacon.className`.
- `onDismiss` adds the key of the hint it receives to `dismissed`. `instance.show()`.
- Each `[data-page-hints-restore]` control: on click, `dismissed.clear()`,
  `instance.setHints(<all hints>)`, `instance.show()`; then `hidden = false`.

`play()`: moves the stylesheet first, as today, then for `"hints"` and then `"tour"` reads
`page-tours-<kind>` and calls its player inside its own `try`, so neither kind's failure stops the
other or raises on the page. The hints come first so a tour step can point at a beacon.

### `page_tours/static/page_tours/page-tours.css`

Imports `hints.css` into the `page-tours` layer after `driver.css`, and holds nothing else.
`hints.css` is Driver.js's: it hides the beacons while a tour plays (D16) and gives them their
look.

### Templates loading the scripts

`hints.iife.js` is one more `<script>` after `driver.js.iife.js`, in `tests/templates/test_base.html`
and the other test base templates that load Driver.js, in `demo/templates/base.html`, and in the
installation page.

### Demo project

- `demo/hints.py`: `REPORT_HINTS`, four hints as the prototype's, under `demo.report`.
  `REPORT_TOUR` in `demo/tours.py`, under `demo.report-tour`, `autoplay=False`.
- `HintsView` at `/hints/`, `demo/templates/demo/hints.html` as the prototype's, with a restore
  control and a replay control. Imports at module level.
- The nav link and the overview paragraph, and `.demo-quiet-beacon` in `base.html`'s styles.

### Documentation

- `docs/developer/hints.md`, a new guide: declaring hints, their options and which are left out
  (`onDismiss`, `onButtonClick`, `onPopoverRender`: a hint's button cannot start a tour),
  dismissal, identifiers and version, give every hint a title (it names the beacon), the restore
  control, hints and a tour on one page, the beacon part, overrides.
- `installation.md`: the hints script. `styling-tours.md`: a hint's popover takes the step's parts,
  and the beacon part. `tours-from-reusable-apps.md`: hints by name, one namespace of names,
  `declarations()` and `declaration_overrides()`. `tours.md`: `Button`, and the payload element.
- `CONTEXT.md`: Declaration, Hints, Hint, Beacon, Dismissed hint, Restore control; the name is
  one namespace for every declaration.
- `CHANGELOG.md`: hints; `page-tour-steps` → `page-tours-tour` with `config`; the moved functions;
  keyword-only declarations; a tour seen before is seen once more.
- README: hints in what the package does.

### ADR

One, graduated at converge: every declaration a page renders shares one base, one namespace of
names and one shape of browser record (D14). Numbered then from `origin/main`. ADR 0006's description of
the stored seen value is superseded by it, marked in place.

## Tests

Mirroring the source tree (`docs/contributing/standards/testing.md`):

- `tests/test_driver.py`: `as_driver` leaves out `None` and package fields, nests, converts lazy
  strings, nested objects and lists; `Declaration` refusals, registry, overrides of the wrong
  class, payload element per kind.
- `tests/test_tours.py`: existing tests moved to the new payload (`config.steps`,
  `page-tours-tour`) and the moved functions. What they assert about a tour does not change.
- `tests/test_hints.py`: US1 scenarios 1–9, 12 on the rendered payload; the default button text in
  the active language.
- `tests/test_checks.py`: W005 across kinds and for hints; W002 for a hints name; W003/W004 for
  the beacon part.
- `tests/test_parts.py`: the beacon part's name and classes.
- `tests/test_static/test_page_tours_js.py`: browser scenarios of US1 (1, 4, 10, 11, 15), US2
  (all) and US3 (1–3), and the tour's seen record under the new shape, including an old record
  read as not seen.
- `tests/test_demo.py`: the hints page renders hints and a tour.

Test views and routes for hints go in `tests/views.py` and `tests/urls.py`, as the tour ones do.
