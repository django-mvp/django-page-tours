"""Tests for page_tours.driver."""

import gc
import json
import re
from dataclasses import dataclass
from typing import ClassVar

import pytest
from django.core.exceptions import ImproperlyConfigured
from django.utils import translation
from django.utils.functional import Promise
from django.utils.safestring import SafeString
from django.utils.translation import gettext, gettext_lazy

from page_tours import driver as driver_module
from page_tours.driver import (
    Declaration,
    DriverObject,
    PopoverContent,
    declaration_overrides,
    declarations,
    driver_value,
    resolve_override,
)


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


@dataclass(frozen=True, kw_only=True)
class Thing(Declaration):
    """The smallest declaration, of a kind of its own."""

    kind: ClassVar[str] = "thing"
    content_field: ClassVar[str] = "items"

    items: tuple[str, ...] = ()


@dataclass(frozen=True, kw_only=True)
class Other(Declaration):
    """A declaration of a different kind."""

    kind: ClassVar[str] = "other"
    content_field: ClassVar[str] = "items"

    items: tuple[str, ...] = ()


ELEMENT = re.compile(
    r'<script id="page-tours-(\w+)" type="application/json">(.*?)</script>',
    re.DOTALL,
)

REPLACEMENT = Thing(name="tests.driver.replacement", version=3, items=("new",))
QUIET = Thing(name="tests.driver.quiet", items=("quiet",))
FOREIGN = Other(name="tests.driver.foreign")
NOT_A_DECLARATION = "not a declaration"
PATH = "tests.test_driver."


def payload_of(declaration):
    """Return the payload a rendered declaration carries."""
    match = ELEMENT.fullmatch(str(declaration))
    assert match is not None
    return json.loads(match.group(2))


class TestDeclaration:
    """Declaring something a page renders."""

    @pytest.mark.parametrize("name", ["", "   ", None, 3, gettext_lazy("x")])
    def test_a_name_that_is_not_a_non_blank_string_is_an_error(self, name):
        """A name is plain text with something in it."""
        with pytest.raises(ImproperlyConfigured):
            Thing(name=name)

    @pytest.mark.parametrize("version", [0, -1, True, "2"])
    def test_a_version_that_is_not_a_whole_number_of_one_or_more_is_an_error(
        self, version
    ):
        """Only 1, 2, 3 and so on are versions."""
        with pytest.raises(ImproperlyConfigured):
            Thing(name="tests.driver.version", version=version)

    def test_a_declaration_is_at_version_one_unless_told_otherwise(self):
        """The version has a default."""
        assert Thing(name="tests.driver.default").version == 1

    def test_the_error_names_the_class_of_the_declaration(self):
        """A refused Thing is reported as a Thing."""
        with pytest.raises(ImproperlyConfigured) as raised:
            Thing(name="")

        assert "Thing" in str(raised.value)
        assert "Other" not in str(raised.value)

    def test_a_declaration_is_recorded_under_its_name(self):
        """It can be found by its name once it exists."""
        thing = Thing(name="tests.driver.recorded")

        assert declarations()["tests.driver.recorded"] == [thing]

    def test_two_declarations_with_one_name_are_both_recorded(self):
        """Both are kept, so a check can report the clash."""
        first = Thing(name="tests.driver.twice")
        second = Other(name="tests.driver.twice")

        recorded = declarations()["tests.driver.twice"]

        assert any(found is first for found in recorded)
        assert any(found is second for found in recorded)

    def test_a_declaration_that_no_longer_exists_is_forgotten(self):
        """One that nothing refers to any more is no longer declared."""
        Thing(name="tests.driver.forgotten")
        gc.collect()

        assert "tests.driver.forgotten" not in declarations()

    def test_declarations_made_and_dropped_leave_nothing_behind(self):
        """A view that builds its declaration on every request grows nothing."""
        for _ in range(3):
            Thing(name="tests.driver.per-request")
        gc.collect()

        assert "tests.driver.per-request" not in driver_module.declared

    def test_the_package_fields_do_not_reach_driverjs(self):
        """Name and version are read in Python only."""
        assert Thing(name="tests.driver.fields", version=2).as_driver() == {"items": []}


class TestDeclarationRendering:
    """A declaration renders as the element the package's script plays it from."""

    def test_the_element_is_named_for_the_kind(self):
        """Each kind has its own element id."""
        thing = Thing(name="tests.driver.element")

        assert ELEMENT.fullmatch(str(thing)).group(1) == "thing"

    def test_the_payload_carries_exactly_its_kind_id_version_parts_and_config(self):
        """Nothing else reaches the browser."""
        payload = payload_of(Thing(name="tests.driver.payload", version=2))

        assert set(payload) == {"kind", "id", "version", "parts", "config"}
        assert payload["kind"] == "thing"
        assert payload["id"] == "tests.driver.payload"
        assert payload["version"] == 2

    def test_the_config_is_the_declaration_as_driverjs_takes_it(self):
        """The fields that are not the package's are the config."""
        thing = Thing(name="tests.driver.config", items=("a", "b"))

        assert payload_of(thing)["config"] == {"items": ["a", "b"]}

    def test_it_renders_as_safe_html_in_a_template(self):
        """``str()`` is what a template converts, and it has to arrive unescaped."""
        thing = Thing(name="tests.driver.safe")

        assert isinstance(str(thing), SafeString)
        assert thing.__html__() == str(thing)


class TestDeclarationOverrides:
    """A project changes or turns off a declaration."""

    def test_a_replacement_renders_in_place_under_the_original_name(self, settings):
        """What was seen under the name stays seen."""
        original = Thing(name="tests.driver.original")
        settings.PAGE_TOURS_OVERRIDES = {original.name: PATH + "REPLACEMENT"}

        payload = payload_of(original)

        assert payload["id"] == original.name
        assert payload["config"] == {"items": ["new"]}

    def test_a_replacement_counts_on_from_the_original_version(self, settings):
        """The version played is the original's plus the replacement's, less one."""
        original = Thing(name="tests.driver.counted", version=2)
        settings.PAGE_TOURS_OVERRIDES = {original.name: PATH + "REPLACEMENT"}

        assert payload_of(original)["version"] == 2 + 3 - 1

    def test_none_renders_nothing(self, settings):
        """An entry of None turns the declaration off."""
        original = Thing(name="tests.driver.off")
        settings.PAGE_TOURS_OVERRIDES = {original.name: None}

        assert str(original) == ""

    def test_a_replacement_of_another_class_is_refused_when_it_renders(self, settings):
        """A tour cannot stand in for hints."""
        original = Thing(name="tests.driver.wrong-class")
        settings.PAGE_TOURS_OVERRIDES = {original.name: PATH + "FOREIGN"}

        with pytest.raises(ImproperlyConfigured) as raised:
            str(original)

        assert original.name in str(raised.value)
        assert "Thing" in str(raised.value)

    def test_rendering_a_replacement_declares_nothing(self, settings):
        """Playing a replacement under the original's name is not a second one."""
        original = Thing(name="tests.driver.no-new")
        settings.PAGE_TOURS_OVERRIDES = {original.name: PATH + "REPLACEMENT"}
        before = {name: len(found) for name, found in declarations().items()}

        str(original)

        assert {name: len(found) for name, found in declarations().items()} == before

    def test_a_change_to_the_setting_is_seen_at_once(self, settings):
        """The setting is read every time the declaration renders."""
        original = Thing(name="tests.driver.live", items=("own",))
        settings.PAGE_TOURS_OVERRIDES = {original.name: None}
        assert str(original) == ""

        settings.PAGE_TOURS_OVERRIDES = {}

        assert payload_of(original)["config"] == {"items": ["own"]}


class TestResolveOverride:
    """Resolving one entry of the setting."""

    @pytest.mark.parametrize("value", [42, [PATH + "REPLACEMENT"], True])
    def test_a_value_that_is_neither_a_path_nor_none_is_refused(self, value):
        """Only a dotted path or None is an entry."""
        with pytest.raises(ImproperlyConfigured):
            resolve_override("tests.driver.entry", value)

    @pytest.mark.parametrize(
        "path", [PATH + "missing", "tests.no_such_module.thing", "nodots"]
    )
    def test_a_path_that_does_not_import_is_refused_with_its_cause(self, path):
        """The import error that explains the refusal is chained."""
        with pytest.raises(ImproperlyConfigured) as raised:
            resolve_override("tests.driver.entry", path)

        assert isinstance(raised.value.__cause__, ImportError)

    def test_a_path_to_something_that_is_not_a_declaration_is_refused(self):
        """What the path names has to be a declaration."""
        with pytest.raises(ImproperlyConfigured):
            resolve_override("tests.driver.entry", PATH + "NOT_A_DECLARATION")

    def test_a_declaration_of_another_class_is_refused_when_a_class_is_given(self):
        """The class the entry has to be is the caller's to name."""
        with pytest.raises(ImproperlyConfigured):
            resolve_override("tests.driver.entry", PATH + "FOREIGN", Thing)

    def test_any_declaration_resolves_without_a_class(self):
        """At start-up the original may not be imported, so any kind will do."""
        assert resolve_override("tests.driver.entry", PATH + "FOREIGN") is FOREIGN

    def test_none_resolves_to_none(self):
        """A declaration turned off has no replacement."""
        assert resolve_override("tests.driver.entry", None) is None

    def test_every_entry_of_the_setting_is_resolved(self, settings):
        """The replacements and the declarations turned off, by name."""
        settings.PAGE_TOURS_OVERRIDES = {
            "tests.driver.a": PATH + "QUIET",
            "tests.driver.b": None,
        }

        assert declaration_overrides() == {
            "tests.driver.a": QUIET,
            "tests.driver.b": None,
        }

    def test_no_setting_resolves_to_nothing(self):
        """A project that sets nothing changes nothing."""
        assert declaration_overrides() == {}

    def test_one_bad_entry_refuses_the_whole_setting(self, settings):
        """A good entry does not hide a bad one."""
        settings.PAGE_TOURS_OVERRIDES = {
            "tests.driver.a": PATH + "QUIET",
            "tests.driver.b": 42,
        }

        with pytest.raises(ImproperlyConfigured):
            declaration_overrides()
