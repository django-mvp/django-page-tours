# Installation

Django Page Tours is a Django app with no models and no settings of its own, so installing it
takes two steps.

## Install the package

```bash
pip install django-page-tours
```

The package depends only on Django. Driver.js is inside it as a static file, so there is nothing
to install from npm and nothing is loaded from a CDN.

## Add the app to your project

Add `page_tours` to `INSTALLED_APPS` in your settings:

```python
INSTALLED_APPS = [
    # ...
    "django.contrib.staticfiles",
    "page_tours",
]
```

Django can now find the package's templates and static files. There are no migrations to run.
