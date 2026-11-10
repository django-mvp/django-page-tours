"""Tests for the package's own stylesheet, page_tours/static/page_tours/page-tours.css."""

from django.contrib.staticfiles import finders


class TestPackageStylesheet:
    """The stylesheet that puts Driver.js's rules in a cascade layer."""

    def test_the_staticfiles_finders_find_it(self):
        """The layer file is found beside the starter script."""
        assert finders.find("page_tours/page-tours.css") is not None
