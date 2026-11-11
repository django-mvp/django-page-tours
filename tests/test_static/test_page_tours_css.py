"""Tests for the package's stylesheet, page_tours/static/page_tours/page-tours.css."""

import re

from django.contrib.staticfiles import finders


class TestPackageStylesheet:
    """The stylesheet that puts Driver.js's rules in a cascade layer."""

    def test_the_staticfiles_finders_find_it(self):
        """The layer file is found beside the starter script."""
        assert finders.find("page_tours/page-tours.css") is not None


class TestChecklistStylesheet:
    """Driver.js's checklist rules sit in the same cascade layer as the others."""

    def test_the_checklist_rules_are_imported_into_the_layer(self):
        """The import names the vendored file and the package's layer."""
        with open(finders.find("page_tours/page-tours.css")) as stylesheet:
            imports = re.findall(
                r'@import url\("([^"]+)"\) layer\(([^)]+)\);', stylesheet.read()
            )

        assert ("vendor/driver.js-1.11.0/checklist.css", "page-tours") in imports

    def test_the_imported_file_is_found(self):
        """The file the stylesheet imports is shipped beside it."""
        assert (
            finders.find("page_tours/vendor/driver.js-1.11.0/checklist.css") is not None
        )
