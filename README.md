# django-page-tours

[![Tests](https://github.com/django-mvp/django-page-tours/actions/workflows/tests.yml/badge.svg)](https://github.com/django-mvp/django-page-tours/actions/workflows/tests.yml)
[![Build](https://github.com/django-mvp/django-page-tours/actions/workflows/build.yml/badge.svg)](https://github.com/django-mvp/django-page-tours/actions/workflows/build.yml)
[![Docs](https://github.com/django-mvp/django-page-tours/actions/workflows/docs.yml/badge.svg)](https://github.com/django-mvp/django-page-tours/actions/workflows/docs.yml)
[![Publish](https://github.com/django-mvp/django-page-tours/actions/workflows/publish.yml/badge.svg)](https://github.com/django-mvp/django-page-tours/actions/workflows/publish.yml)
[![Coverage](https://codecov.io/gh/django-mvp/django-page-tours/branch/main/graph/badge.svg)](https://codecov.io/gh/django-mvp/django-page-tours)
[![PyPI](https://img.shields.io/pypi/v/django-page-tours)](https://pypi.org/project/django-page-tours/)
[![Development status](https://img.shields.io/pypi/status/django-page-tours)](https://pypi.org/project/django-page-tours/)
[![Python](https://img.shields.io/pypi/pyversions/django-page-tours)](https://pypi.org/project/django-page-tours/)
[![Django](https://img.shields.io/pypi/djversions/django-page-tours)](https://pypi.org/project/django-page-tours/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Licence](https://img.shields.io/github/license/django-mvp/django-page-tours)](https://github.com/django-mvp/django-page-tours/blob/main/LICENSE)

Guided tours of a page for Django sites, shown with [Driver.js](https://driverjs.com/).

A new visitor to an application often can't tell what a page is for or where its important
controls are. A short tour fixes that: a few steps, each pointing at one part of the page with a
sentence about it. Building one by hand means wiring a JavaScript library into templates, writing
the steps in JavaScript far from the view they describe, and remembering who has already seen it.
django-page-tours moves the steps into Python, next to the page, and handles the rest.

> **Status:** pre-release. A tour can be declared for a page and plays when the page opens.
> Nothing is published to PyPI until the first usable version.

## Scope & philosophy

**What it is.** A tour belongs to one page. A developer declares its steps in Python, each one
pointing at an element on the page with a title and a short text. The first time someone opens
the page, the tour plays. They can step through it, skip it or close it, and once they have seen
it, their browser remembers and it does not play again unless they ask for it.

**What it deliberately is not.**

- **Not a design.** The package ships Driver.js's own styling and nothing more. A site gives the
  tour its look with its own CSS.
- **Not a store of progress per account.** Whether someone has seen a tour is kept in their
  browser. The package adds no database tables.
- **Not tours across several pages,** and not a getting-started checklist.
- **Not dependent on a CDN.** Driver.js ships inside the package, so a tour works on a site with a
  strict content security policy or no outside network access.

**When a choice is close:**

1. Lean on Driver.js for anything it already does, rather than reimplementing it.
2. A tour that fails must leave the page exactly as usable as it was without one.
3. Fewer settings beat more. Each one has to earn its place.

## Quickstart

Add `page_tours` to `INSTALLED_APPS`, load the tag once in the `<head>` of your base template,
and declare a tour on a view:

```django
{% load page_tours %}
{% page_tour %}
```

```python
from django.views.generic import TemplateView

from page_tours import Tour, TourStep


class DashboardView(TemplateView):
    template_name = "dashboard.html"
    tour = Tour(steps=[TourStep(title="Welcome", text="A quick look around.")])
```

The [documentation](https://django-mvp.github.io/django-page-tours/) covers function-based views,
steps attached to elements and translation.

## Requirements

- Python 3.12 or 3.13
- Django 5.2, 6.0 or 6.1

## Prior art

| Package | Why it isn't this |
|---|---|
| [django-tour](https://github.com/ambitioninc/django-tour) | No release since 2015 |
| [django-driverjs](https://github.com/iwalucas/django-driverjs) | No release since 2022, no licence |
| [django-tours](https://github.com/wilmerm/django-tours) | Built on Shepherd.js, which is AGPL-licensed. Loads its script from a CDN and keeps tours in the database |

## Licence

MIT. Driver.js is also MIT-licensed.
