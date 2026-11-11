"""Tests for page_tours.driver."""

from dataclasses import dataclass

import pytest
from django.utils import translation
from django.utils.functional import Promise
from django.utils.translation import gettext, gettext_lazy

from page_tours.driver import DriverObject, PopoverContent, driver_value


@dataclass(frozen=True, kw_only=True)
class Inner(DriverObject):
    """A Driver.js object nested in another."""

    size: int | None = None


@dataclass(frozen=True, kw_only=True)
class Outer(DriverObject):
    """A Driver.js object with a package field and an inner object."""

    package_fields = frozenset({"label"})
    nested = {"box": frozenset({"color"})}

    label: str = "kept in Python"
    color: str | None = None
    width: int | None = None
    text: str | Promise | None = None
    inner: Inner | None = None
    inners: tuple[Inner, ...] | None = None
    buttons: tuple[str, ...] | None = None


@dataclass(frozen=True, kw_only=True)
class Popover(PopoverContent):
    """A popover content whose popover fields are nested."""

    nested = {"popover": PopoverContent.popover_fields}

    element: str = ""


class TestDriverObject:
    """Converting a declared object to the form Driver.js takes."""

    def test_a_field_left_as_none_is_left_out(self):
        """A null would override the value Driver.js falls back to."""
        assert Outer(width=3).as_driver() == {"box": {}, "width": 3}

    def test_a_package_field_is_left_out(self):
        """A package field is read in Python, never by Driver.js."""
        assert "label" not in Outer(label="x").as_driver()

    def test_a_false_value_is_kept(self):
        """Only None means unset."""
        assert Outer(text="").as_driver()["text"] == ""

    def test_a_nested_field_goes_into_its_inner_object(self):
        """A field named in ``nested`` sits in that object, not beside it."""
        assert Outer(color="red").as_driver() == {"box": {"color": "red"}}

    def test_an_inner_object_exists_when_it_stays_empty(self):
        """Driver.js needs the object itself, whatever it holds."""
        assert Outer().as_driver()["box"] == {}

    def test_a_step_with_no_popover_fields_still_has_a_popover(self):
        """Driver.js cannot show a popover that is not there."""
        assert Popover().as_driver() == {"element": "", "popover": {}}

    def test_a_popover_field_goes_into_the_popover(self):
        """The five popover fields sit in ``popover``."""
        step = Popover(title="T", description="D", side="left", align="end")

        assert step.as_driver()["popover"] == {
            "title": "T",
            "description": "D",
            "side": "left",
            "align": "end",
        }

    def test_a_nested_object_is_converted(self):
        """An object held by another arrives as the dict Driver.js takes."""
        assert Outer(inner=Inner(size=4)).as_driver()["inner"] == {"size": 4}

    def test_a_tuple_of_objects_is_converted_to_a_list_of_dicts(self):
        """Every object of the tuple is converted, in order."""
        outer = Outer(inners=(Inner(size=1), Inner(size=2)))

        assert outer.as_driver()["inners"] == [{"size": 1}, {"size": 2}]

    def test_a_lazy_string_renders_in_the_active_language(self):
        """The language active when the object is converted decides the text."""
        outer = Outer(text=gettext_lazy("Yes"))

        with translation.override("de"):
            text = outer.as_driver()["text"]
            expected = str(gettext("Yes"))

        assert text == expected != "Yes"


class TestDriverValue:
    """Converting one value of a field."""

    def test_a_tuple_becomes_a_list(self):
        """JSON has lists, and Driver.js reads them."""
        assert driver_value(("next", "close")) == ["next", "close"]

    def test_a_list_is_converted_item_by_item(self):
        """A lazy string inside a list is rendered too."""
        assert driver_value([gettext_lazy("Yes")]) == [str(gettext("Yes"))]

    def test_a_lazy_string_becomes_a_string(self):
        """A lazy string cannot be written as JSON."""
        assert type(driver_value(gettext_lazy("Yes"))) is str

    @pytest.mark.parametrize("value", ["text", 3, 0.5, False, "<b>x</b>"])
    def test_any_other_value_is_passed_as_it_is(self, value):
        """Text is passed to Driver.js as written."""
        assert driver_value(value) == value
