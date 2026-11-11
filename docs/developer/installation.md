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

Django can now find the package's static files. There are no migrations to run.

## Include the package's files in your base template

A tour needs one stylesheet and two scripts, which the package ships as static files. Include
them once, in the `<head>` of your base template:

```django
{% load static %}
<head>
  ...
  <link rel="stylesheet" href="{% static 'page_tours/page-tours.css' %}">
  <script src="{% static 'page_tours/vendor/driver.js-1.11.0/driver.js.iife.js' %}" defer></script>
  <script src="{% static 'page_tours/page-tours.js' %}" defer></script>
</head>
```

- **Load Driver.js before `page-tours.js`.** The package's script plays the tour with it.
- **`defer` is optional.** The script waits until the page is parsed before it looks for the
  tour, so the scripts work in the `<head>` or at the end of the `<body>`, with or without
  `defer`.
- **Link the stylesheet wherever you like.** Before a tour plays, the script moves it to the
  start of the `<head>`, so that Driver.js's styles sit under every style of your own (see
  [Styling tours](styling-tours.md)). The script finds the link by its path,
  `page_tours/page-tours.`, so a hashed file name from `ManifestStaticFilesStorage` is found too.
- **On a page with no tour the files do nothing.** Nothing shows, and a
  [replay control](replaying-a-tour.md) marked `hidden` stays hidden.

The files come from your own static files, so nothing is loaded from another site. Each page
then outputs its own tour with `{{ tour }}`, the way a form outputs its assets with
`{{ form.media }}`. [Adding a tour to a page](tours.md) shows how.

## Settings

None are required. Two are there when you need them:

- `PAGE_TOURS_CLASSES` gives the parts of a shown step classes of your own. See
  [Styling tours](styling-tours.md).
- `PAGE_TOURS_OVERRIDES` replaces or turns off the tour of an installed app. See
  [Tours from reusable apps](tours-from-reusable-apps.md).
