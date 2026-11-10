# Installation

Django Page Tours is a Django app with no models and no settings you have to set, so installing
it takes three steps.

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

The tag draws nothing where it stands. On a page with a tour it adds the tour's stylesheet, its
steps and the scripts that play it, the way `{{ form.media }}` adds a form's assets, and the tour
then shows over the page. That is why it goes once in the base template and not where a tour is
used: every page that extends the template is served by it, and a page with no tour gets nothing
from it. The one tag a visitor sees is the [replay control](replaying-a-tour.md), which you place
where its button should appear.

The tag needs nothing else from your settings. [Adding a tour to a page](tours.md) shows how to
declare a tour.

## Settings

None are required. Two are there when you need them:

- `PAGE_TOURS_CLASSES` gives the parts of a shown step classes of your own. See
  [Styling tours](styling-tours.md).
- `PAGE_TOURS_OVERRIDES` replaces or turns off the tour of an installed app. See
  [Tours from reusable apps](tours-from-reusable-apps.md).
