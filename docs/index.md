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

The package is in early development and no tours can be declared yet. This site grows as each
feature lands.

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

[Installation](developer/installation.md) in the developer guide says what each step sets up.

## Next steps

- [Developer guide](developer/index.md): installing the package and adding tours to your pages.
- [Reference](reference/api/index): the Python API.

## About the project

- [Goals](https://github.com/django-mvp/django-page-tours/blob/main/GOALS.md): the standing directions the package works toward.
- [Domain model](https://github.com/django-mvp/django-page-tours/blob/main/CONTEXT.md): what tour, tour step, seen and replay mean here.
- [Constitution](https://github.com/django-mvp/django-page-tours/blob/main/CONSTITUTION.md): the rules every change is reviewed against.
- [Changelog](https://github.com/django-mvp/django-page-tours/blob/main/CHANGELOG.md): what changed in each release.

## Support

Report a problem on the [issue tracker](https://github.com/django-mvp/django-page-tours/issues).
Everyone taking part follows the
[code of conduct](https://github.com/django-mvp/.github/blob/main/CODE_OF_CONDUCT.md).

## Licence

MIT. Driver.js is also MIT-licensed.
