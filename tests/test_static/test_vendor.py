"""Tests for the vendored Driver.js files."""

import pytest
from django.contrib.staticfiles import finders

VENDOR_DIR = "page_tours/vendor/driver.js-1.11.0"


class TestVendoredDriverJs:
    """The Driver.js release the package ships."""

    @pytest.mark.parametrize(
        "name",
        [
            "driver.js.iife.js",
            "driver.css",
            "hints.iife.js",
            "hints.css",
            "checklist.iife.js",
            "checklist.css",
            "LICENSE",
        ],
    )
    def test_the_staticfiles_finders_find_the_vendored_file(self, name):
        """The scripts, the stylesheets and the licence are found by the finders."""
        assert finders.find(f"{VENDOR_DIR}/{name}") is not None
