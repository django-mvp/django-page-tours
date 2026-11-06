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

## Add the tag to your base template

Load the tag library and place the tag once in the `<head>` of your base template:

```django
{% load page_tours %}
<head>
  ...
  {% page_tour %}
</head>
```

The tag needs `django.template.context_processors.request` in the `context_processors` option of
your `TEMPLATES` setting, and Django's `check` command warns with `page_tours.W001` when it is
missing. [Adding a tour to a page](tours.md) shows how to declare a tour.
