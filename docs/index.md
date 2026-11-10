# Django Page Tours

```{toctree}
:hidden:

Home <self>
Developer guide <developer/index>
Reference <reference/api/index>
Contributing <contributing/index>
Changelog <https://github.com/django-mvp/django-page-tours/blob/main/CHANGELOG.md>
```

Django Page Tours gives a Django site guided tours of its pages. You declare a tour for a page in
Python, next to the view that renders it, as a short list of steps that each point at one part of
the page. [Driver.js](https://driverjs.com/), shipped inside the package, shows the tour in the
visitor's browser.

A tour plays by itself the first time a browser opens its page and then stays out of the way. A
visitor can play it again from a replay control you place. It works from the keyboard and with a
screen reader, speaks the page's language, and takes your site's look. A project can change the
tours of the apps it installs without editing them.

## Requirements

- Python 3.12 or 3.13
- Django 5.2, 6.0 or 6.1

## Installation

```bash
pip install django-page-tours
```

Add the app to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ...
    "page_tours",
]
```

Place the tag once in the `<head>` of your base template:

```django
{% load page_tours %}
<head>
  ...
  {% page_tour %}
</head>
```

The tag draws nothing where it stands. It adds the tour's stylesheet, steps and scripts to the
page, and the tour then shows over the page.

[Installation](developer/installation.md) in the developer guide says what each step sets up.

## Example

Declare a tour on a class-based view:

```python
from django.views.generic import TemplateView

from page_tours import Tour, TourStep


class DashboardView(TemplateView):
    template_name = "dashboard.html"
    tour = Tour(
        name="dashboard",
        steps=[
            TourStep(title="Welcome", text="A quick look around."),
            TourStep(title="Projects", text="Your work is here.", element="#projects"),
        ],
    )
```

The page plays the tour when it opens, and the browser remembers it by its name, `dashboard`.
[Adding a tour to a page](developer/tours.md) covers naming a tour, function-based views, steps
and translation.

## Next steps

- [Developer guide](developer/index.md): installing the package, [adding a tour to a page](developer/tours.md),
  [replaying a tour](developer/replaying-a-tour.md), [tours from reusable apps](developer/tours-from-reusable-apps.md)
  and [styling tours](developer/styling-tours.md).
- [Reference](reference/api/index): the Python API.

## About the project

- [Goals](https://github.com/django-mvp/django-page-tours/blob/main/GOALS.md): the standing directions the package works toward.
- [Domain model](https://github.com/django-mvp/django-page-tours/blob/main/CONTEXT.md): what tour, tour step, seen, tour version and replay mean here.
- [Constitution](https://github.com/django-mvp/django-page-tours/blob/main/CONSTITUTION.md): the rules every change is reviewed against.
- [Changelog](https://github.com/django-mvp/django-page-tours/blob/main/CHANGELOG.md): what changed in each release.

## Support

Report a problem on the [issue tracker](https://github.com/django-mvp/django-page-tours/issues).
Everyone taking part follows the
[code of conduct](https://github.com/django-mvp/.github/blob/main/CODE_OF_CONDUCT.md).

## Licence

MIT. Driver.js is also MIT-licensed.
