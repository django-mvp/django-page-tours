"""The library app, which stands for a reusable app installed in a project."""

from django.apps import AppConfig


class LibraryConfig(AppConfig):
    """A small app that ships its own pages and tours, as an installed package would."""

    name = "demo.library"
    label = "library"
