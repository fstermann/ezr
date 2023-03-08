from __future__ import annotations

import itertools
import re

import pytest

from ezr import CharacterSet
from ezr import digit
from ezr import EzRegex
from ezr import Pattern
from ezr import Quantifier


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
            ["f", Pattern("f"), EzRegex("f")],
            ["b", Pattern("b"), EzRegex("b")],
        ),
    )
    def test_add_literal_regex(self, a, b):
        regex = EzRegex(a + b)
        assert str(regex) == "fb"

        regex_comp = regex.compile()
        assert re.match(regex_comp, "fb") is not None
        assert re.match(regex_comp, "bf") is None

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
            "  Pattern('f')\n"
            "  Pattern('o')\n"
            "  Pattern('o')\n"
            "  EzRegex(\n"
            "    Pattern('a')\n"
            "    Pattern('b')\n"
            "  )\n"
            "  Pattern('b')\n"
            "  Pattern('a')\n"
            "  Pattern('r')\n"
            ")"
        )

    @pytest.mark.parametrize(
        "a, b",
        list(
            itertools.product(
                ["f", Pattern("f"), EzRegex("f")],
                ["b", Pattern("b"), EzRegex("b")],
            ),
        )[1:],
    )
    def test_or_literal(self, a, b):
        regex = a | b
        assert str(regex) == "f|b"

        regex_comp = regex.compile()
        assert re.match(regex_comp, "f") is not None
        assert re.match(regex_comp, "b") is not None
        assert re.match(regex_comp, "c") is None

    def test_with_quantifier(self, lower_upper_lazy):
        lower, upper, lazy = lower_upper_lazy
        if lower is not None and upper is not None and lower > upper:
            with pytest.raises(
                ValueError,
                match=r"Lower bound cannot be greater than upper bound",
            ):
                regex = EzRegex("foo", "bar", lower=lower, upper=upper, lazy=lazy)
            return
        regex = EzRegex("foo", "bar", lower=lower, upper=upper, lazy=lazy)
        if lower is None and upper is None:
            assert regex.quantifier is None
            return
        assert regex.quantifier == Quantifier(lower, upper, lazy=lazy)

    def test_from_quantifier(self, valid_quantifier_params, valid_patterns):
        valid_quantifier = Quantifier(**valid_quantifier_params)
        regex = EzRegex.from_quantifier(*valid_patterns, quantifier=valid_quantifier)
        assert regex.quantifier == valid_quantifier

    def test_as_charset(self, pattern_expected):
        pattern, expected = pattern_expected
        regex = EzRegex(*pattern)
        regex = regex.as_charset()
        assert isinstance(regex, CharacterSet)
        assert str(regex) == rf"[{expected}]"
