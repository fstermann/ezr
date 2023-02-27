from __future__ import annotations

import itertools
import re

import pytest

from ezr import digit
from ezr import EzPattern
from ezr import EzRegex


class TestEzRegex:
    def test_regex_literal(self):
        regex = EzRegex("foo")
        assert str(regex) == "foo"

        regex_comp = regex.compile()
        assert re.match(regex_comp, "foo") is not None
        assert re.match(regex_comp, "bar") is None

    def test_init_literal(self):
        regex = EzRegex(EzRegex("foo"), EzRegex("bar"))
        assert str(regex) == "foobar"

        regex_comp = regex.compile()
        assert re.match(regex_comp, "foobar") is not None
        assert re.match(regex_comp, "barfoo") is None

    @pytest.mark.parametrize(
        "a, b",
        itertools.product(
            ["foo", EzPattern("foo"), EzRegex("foo")],
            ["bar", EzPattern("bar"), EzRegex("bar")],
        ),
    )
    def test_add_literal_regex(self, a, b):
        regex = EzRegex(a + b)
        assert str(regex) == "foobar"

        regex_comp = regex.compile()
        assert re.match(regex_comp, "foobar") is not None
        assert re.match(regex_comp, "barfoo") is None

    def test_negation(self):
        regex = ~EzRegex("foo")
        print(regex._patterns)
        print(regex.__str__())
        assert str(regex) == "[^foo]"

        regex_comp = regex.compile()
        assert re.match(regex_comp, "foo") is None
        assert re.match(regex_comp, "bar") is not None

    def test_negation_already_negated(self):
        regex = ~EzRegex("foo")
        regex = ~regex
        assert str(regex) == "foo"

        regex_comp = regex.compile()
        assert re.match(regex_comp, "foo") is not None
        assert re.match(regex_comp, "bar") is None

    def test_digit(self):
        assert str(digit) == r"\d"

        regex_comp = digit.compile()
        assert re.match(regex_comp, "1") is not None
        assert re.match(regex_comp, "a") is None

    def test_repr(self):
        regex = EzRegex("foo", EzRegex("a", "b"), "bar")
        assert repr(regex) == (
            "EzRegex(\n"
            "  EzPattern('foo')\n"
            "  EzRegex(\n"
            "    EzPattern('a')\n"
            "    EzPattern('b')\n"
            "  )\n"
            "  EzPattern('bar')\n"
            ")"
        )

    @pytest.mark.parametrize(
        "a, b",
        list(
            itertools.product(
                ["foo", EzPattern("foo"), EzRegex("foo")],
                ["bar", EzPattern("bar"), EzRegex("bar")],
            ),
        )[1:],
    )
    def test_or_literal(self, a, b):
        regex = a | b
        assert str(regex) == "foo|bar"

        regex_comp = regex.compile()
        assert re.match(regex_comp, "foo") is not None
        assert re.match(regex_comp, "bar") is not None
        assert re.match(regex_comp, "baz") is None
