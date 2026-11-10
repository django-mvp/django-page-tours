"""Tests for the vendored Driver.js files."""

import pytest
from django.contrib.staticfiles import finders

VENDOR_DIR = "page_tours/vendor/driver.js-1.10.2"


class TestVendoredDriverJs:
    """The Driver.js release the package ships."""

    @pytest.mark.parametrize("name", ["driver.js.iife.js", "driver.css", "LICENSE"])
    def test_the_staticfiles_finders_find_the_vendored_file(self, name):
        """The script, the stylesheet and the licence are found by the finders."""
        assert finders.find(f"{VENDOR_DIR}/{name}") is not None


class TestPackageStylesheet:
    """The stylesheet that puts Driver.js's rules in a cascade layer."""

    def test_the_staticfiles_finders_find_it(self):
        """The layer file is found beside the starter script."""
        assert finders.find("page_tours/page-tours.css") is not None
