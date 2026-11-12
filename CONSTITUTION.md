# django-page-tours Constitution

<!-- Authored at onboarding. Rarely changed; changes go through the constitution pathway
     (human-gated), never mid-feature. Read at the Constitution Check in /plan and by
     reviewers. -->

## Core articles

### Article I — Testing
Every change follows [`docs/contributing/standards/testing.md`](docs/contributing/standards/testing.md): what gets a test
and what does not, the test-first cycle, test structure and fixtures, and the coverage floors.

### Article II — Simplicity
Start with the simplest design that satisfies the spec. New dependencies, new abstractions,
and new infrastructure each require a stated justification in plan.md Complexity Tracking.
YAGNI over speculation.

### Article III — Anti-Abstraction
No wrapper layers, base classes, or "future-proofing" indirection without a present, concrete
second use. Prefer duplication over the wrong abstraction. A second use also counts as
present when it is in another approved specification built in the same batch, such as several
features specified together from one prototype.

### Article IV — Integration-First
Contracts and integration points are designed and tested before internals are polished.
Acceptance scenarios exercise the system the way users touch it.

### Article V — Security & data-safety
Values interpolated into rendered output are escaped through the framework's template layer,
never hand-built string interpolation of model or user data. Secrets live in runtime config,
never in code, fixtures, or version control. Authentication, authorisation, cryptography and
permission changes never take a shortened review path.

### Article VI — Documentation
Public API changes ship their docs in the same PR: README + CHANGELOG updated. Docstrings,
component annotations and code comments follow
[`docs/contributing/standards/code-documentation.md`](docs/contributing/standards/code-documentation.md). The pages under
`docs/` and the README's quickstart follow
[`docs/contributing/standards/documentation.md`](docs/contributing/standards/documentation.md). The built
documentation must build clean. The README states what the package is, what it deliberately is
not, how to install and configure it, and links to the full documentation.

### Article VII — Dependency discipline
A new runtime dependency requires a stated justification (Simplicity applied to the dependency
tree; prefer the shared `mvp-shared` toolchain bundle over ad-hoc dev deps). `deptry` must pass:
no unused, missing, or transitively-relied-upon dependencies.

### Article VIII — Internationalization
User-facing strings are translatable. In Python (models, forms, views, admin, template tags,
validators) they are wrapped with `gettext_lazy` (imported as `_`); templates load
`{% load i18n %}` and wrap strings with `{% trans %}` / `{% blocktrans %}`. Model `verbose_name`
/ `verbose_name_plural` and form `label` / `help_text` / `error_messages` use `gettext_lazy`; pure
acronyms are exempt. A package ships a base English (`en`) catalog and a `locale/` directory so
host projects can compile or extend translations. CI runs `makemessages` clean over the source as
the i18n gate; correct wrapper usage is otherwise enforced by review, and a hard-coded user-visible
string in a PR is a blocking comment. Messages written for the developer, such as system
checks, exception messages and log lines, are plain English and never marked for translation. A
package with no user-facing strings satisfies this trivially.

This article covers the package and never its demo or example application. A demo is never
translated: its strings are plain text, with no `gettext_lazy`, `{% load i18n %}`, `{% trans %}`
or `{% blocktrans %}`, and `makemessages` runs over the package source only. Every string marked
in a demo is one more for the package's translators to carry, for an app nobody installs.
Translation markup in a demo is a blocking comment. A demo may still turn on `LocaleMiddleware`
and `set_language`, so the package's own translations can be seen working.

### Article IX — Data-model conventions (Django)
Every model field is a deliberate indexing decision. Because consumers of a published package cannot
add their own indexes, any field with a plausible lookup / filter / ordering path is indexed at its
definition (`db_index`, `unique`, an FK's automatic index, or a composite `Meta.constraints` /
`Meta.indexes`); a field with no query path stays unindexed to avoid write cost. The choice —
indexed or not, and why — is recorded (plan `data-model.md` or `decisions.md`). `verbose_name` and
`help_text` are mandatory on every model field (Article VIII). **Migrations are consolidated per
PR:** the migrations a feature branch introduces are squashed into as few files as possible before
the PR is submitted (branch-local and unapplied, so safe at any release stage); data migrations
(`RunPython`/`RunSQL`) are exempt from auto-regeneration — keep them via `squashmigrations` or
standalone.

### Article X — Cohesion (Python)
Related behaviour is grouped in a class, not scattered across module-level functions.

**The test:** two or more module-level functions that share a *subject* belong on a class. They
share a subject when they operate on the same data, take the same first argument, are only
meaningful in sequence, or are named around the same noun (`build_x`, `validate_x`, `render_x`).

**Why this is a standard and not a taste.** In a published package, a class is the extension
point. A consumer who needs different behaviour subclasses it and overrides one method. A module
of functions can only be monkey-patched, which is not a supported interface and breaks on any
internal change. Grouping also gives the behaviour a name, a place for shared configuration, and
one import instead of six.

**Shape:** shared state or configuration → a regular class holding it. Grouping for namespacing
with no shared state → still a class, with `@classmethod`/`@staticmethod`, or a small frozen
dataclass carrying the config. Expose a module-level convenience function only as a thin wrapper
over the class, never as the implementation.

**Django first.** Where the framework already owns the grouping, use it rather than inventing a
class: a `QuerySet`/`Manager` method instead of a function taking a queryset, a model method or
property instead of a function taking an instance, a `Form`/`Serializer` method instead of a free
validation function, a `TemplateView` method instead of a helper called by a view.

**Django standards.** Where code lives in a Django codebase, and when a new abstraction is worth
adding, is set out in [`docs/contributing/standards/django.md`](docs/contributing/standards/django.md).

**Exceptions — narrow, and stated rather than assumed.** A genuinely standalone pure function with
no siblings. Framework-dictated module shapes: `conftest.py` fixtures, migrations, `urls.py`,
`apps.py`, decorator-registered template tags and filters, signal receivers, management-command
entry points. Factory functions that return the class. A module of independent utilities that
genuinely share no subject.

**This does not license abstraction.** Article III still holds: one class grouping today's
behaviour is the goal, not a base class, a registry, or a hierarchy built for a second
implementation that does not exist. Grouping related functions is organisation; adding a layer
between the caller and the work is not.

## Project articles (django-page-tours-specific)

### Article XI — Compatibility
The supported Python and Django versions are stated in `pyproject.toml`, its classifiers, the
README's Requirements section and the CI test matrix. Those four agree at all times. Changing
them is a deliberate change, never a side effect of a dependency bump.

Until 0.1.0 nothing is stable and any name may change in a patch. From 0.1.0 the public surface
is the one the README documents. It is semver-stable: a rename or a removal is a major version,
and a deprecation lives at least one minor release with a warning before it goes.

### Article XII — Stack norms
uv-managed with a hatchling build backend, and with the development toolchain coming from the
shared `mvp-shared` bundle rather than per-repo pins. CI calls the shared reusable workflows,
pinned to a tag and never `@main`. Documentation is Sphinx and must build clean.

Driver.js is shipped inside the package as a static file, at one recorded release, with its
licence beside it. No page the package renders loads a script or stylesheet from another origin.
Moving to a new Driver.js release is its own change, recorded in the CHANGELOG.

### Article XIII — A tour never breaks its page
The page works the same with a tour as without one. The package never hides, moves or changes
an element of the page outside a step that is showing. A step whose element is not on the page
is skipped, never an error. A failure inside the tour script ends the tour and leaves the page
as it was. With JavaScript off, the page renders as if it had no tour.

### Article XIV — No look of its own
The package's own stylesheet is Driver.js's, and the markup it emits carries no classes from
any CSS framework. A site gives the tour its look with its own CSS, so a change that makes the
package know about one site's design is the wrong change.

## Quality bar

Read at plan and review; applies to every change.

- Test coverage: **project ≥ 90%, patch ≥ 85%** (`codecov.yml` is the reference), with a small
  tolerance — floors, not a 100% ratchet.
- Every public API change updates README + CHANGELOG in the same PR.
- Lint, type-check (`mypy`), and `deptry` pass. The lint gate is `pre-commit run --all-files`,
  not a bare `ruff check .`: the hook config excludes `docs/` and migrations, and runs hooks a
  bare invocation does not.
- The package builds and its metadata is valid; the README renders on the package index
  (absolute URLs only — a relative link breaks there); the public API honors the deprecation
  policy in Article XI.
- Documentation builds clean, with warnings treated as errors.
- Every feature ships its documentation page and its page in the demo project in the same pull
  request. The demo has a page showing each kind of tour step the package supports.

Article IX is satisfied trivially: there are no models, and seen state lives in the browser.
Adding a model brings the article into play rather than being an exception to it.

## Non-negotiables

- Tests, build and lint pass before a change merges. Nobody overrides a red check.
- The default branch requires one approval, and the author of a change never approves it.
- Nothing pushes to the default branch outside a pull request. Releases run through the Prepare
  Release → Tag Release → Publish flow, never a hand-pushed tag.

---

**Version**: 1.1.1 | **Ratified**: 2026-11-06 | **Last Amended**: 2026-11-11
