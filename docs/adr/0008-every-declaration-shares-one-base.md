# ADR 0008 — Every declaration a page renders shares one base

**Status:** accepted. Amends ADR 0006 and ADR 0007.

## Decision

A tour and a page's hints are two kinds of one thing, a declaration, and every later kind is
built the same way.

- Each Driver.js object the package declares is a frozen, keyword-only dataclass on
  `page_tours.driver.DriverObject`, whose fields are named as Driver.js names its options.
  `as_driver()` turns it into the object Driver.js takes: a field left as `None` is left out, a
  lazy string renders in the active language, nested objects and lists are converted, and the
  fields Driver.js reads from an inner object, such as a step's `popover`, go into it.
- `PopoverContent` holds the popover fields a tour step and a hint share.
- `Declaration` is what a page renders with `{{ … }}`. It holds the name and the version, records
  itself under its name, applies `PAGE_TOURS_OVERRIDES` when it renders, and outputs
  `<script id="page-tours-<kind>" type="application/json">` with the kind, the name, the version,
  the classes of each part and its Driver.js object under `config`. A tour renders as
  `page-tours-tour` and hints as `page-tours-hints`.
- Names are one namespace across every kind. Two declarations of different kinds under one name
  are reported by the system checks as one name declared twice, and an override's replacement
  has to be of the same class as the declaration it replaces.
- In the browser, what a visitor did is kept the same way for every kind: under
  `page-tours:<record>:<name>`, as the version it holds for and a list of ids. A seen tour is
  `page-tours:seen:<name>`, dismissed hints are `page-tours:dismissed:<name>`. A record of another
  version reads as nothing stored.

## Why

Driver.js 1.11.0 adds hints and a checklist beside its tours. Each is configured with a plain
object, and each needs the same things from the package: a declaration in Python with
Driver.js's names, a name a project overrides it by, a version that makes a browser forget, and a
record of what a visitor did. Writing those once keeps every kind behaving alike, and the code a
kind adds is its own fields and nothing else. The checklist is the third kind, so the bases have
two uses in this change and a third already specified.

- **The fields are Driver.js's names**, so Driver.js's documentation describes every option, and
  `as_driver()` is the whole conversion: no list of names to keep in step with the fields.
- **One namespace of names**, because a name is how a project reaches a declaration in
  `PAGE_TOURS_OVERRIDES`, and one entry has to mean one thing.
- **One shape of browser record**, so that a version and a set of ids is all any kind needs, and
  the code that reads and writes local storage, and copes with it being blocked, exists once.

## Consequences

- The tour's element was `page-tour-steps` with its options under `options` and its steps beside
  them. It is now `page-tours-tour` with the steps inside `config`.
- `declared_tours`, `tour_overrides` and `resolve_override` are now `declarations`,
  `declaration_overrides` and `resolve_override` in `page_tours.driver`.
- Declarations take keyword arguments only, because the base's `version` has a default ahead of
  each kind's required fields.
- A browser that remembered a tour as seen under the old value, a bare version number, sees the
  tour once more. The changelog says so.

## Revisit if

- A Driver.js object needs a conversion that `as_driver()` cannot express with `None`, nesting and
  lazy strings.
- A kind needs a browser record that is not a set of ids.
