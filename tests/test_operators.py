from __future__ import annotations

import pytest

from ezr import CharacterSet
from ezr import EzRegex
from ezr import Group
from ezr import Pattern
from ezr import Quantifier


class TestOperators:
    @pytest.mark.parametrize(
        "a, b, expected",
        [
            ("foo", EzRegex("bar"), "foobar"),
            (EzRegex("foo"), "bar", "foobar"),
            (EzRegex("foo"), EzRegex("bar"), "foobar"),
        ],
    )
    def test_add(self, a, b, expected):
        regex = a + b
        assert str(regex) == expected
        assert isinstance(regex, EzRegex)
        assert len(regex._patterns) == 6

    @pytest.mark.parametrize(
        "a, b, expected",
        [
            (EzRegex("foo", Group("baz")), "bar", "foo(baz)bar"),
            ("foo", EzRegex("bar", Group("baz")), "foobar(baz)"),
            (EzRegex("foo", CharacterSet("baz")), "bar", "foo[baz]bar"),
        ],
    )
    def test_add_nested(self, a, b, expected):
        regex = EzRegex(a + b)
        assert str(regex) == expected
        assert isinstance(regex, EzRegex)

    @pytest.mark.parametrize(
        "multiplier, expected",
        [
            (0, Quantifier(0, 0)),
            (1, Quantifier(1, 1)),
            (2, Quantifier(2, 2)),
            ((0, 1), Quantifier(0, 1)),
            ((1, 2), Quantifier(1, 2)),
            ((0, None), Quantifier(0, None)),
            ((None, 1), Quantifier(None, 1)),
        ],
    )
    def test_mul(self, multiplier, expected):
        pattern = Pattern("a")
        assert str(pattern) == "a"
        pattern_multiplied = pattern * multiplier
        pattern_rmultiplied = multiplier * pattern
        assert pattern_multiplied._quantifier == expected
        assert pattern_rmultiplied._quantifier == expected
        assert pattern_multiplied == pattern_rmultiplied

    @pytest.mark.parametrize(
        "multiplier",
        [1.0, "b", (1, 2, 3), (1.1, 1)],
    )
    def test_mul_invalid(self, multiplier):
        pattern = Pattern("a")
        with pytest.raises(
            ValueError,
            match=r"Can only repeat by an integer or a tuple of two integers",
        ):
            pattern * multiplier

    @pytest.mark.parametrize(
        "multiplier, expected",
        [
            (0, Quantifier(1, None)),
            (1, Quantifier(2, None)),
            (2, Quantifier(3, None)),
        ],
    )
    def test_gt(self, multiplier, expected):
        pattern = Pattern("a") > multiplier
        assert pattern._quantifier == expected

    @pytest.mark.parametrize(
        "multiplier, expected",
        [
            (0, Quantifier(0, None)),
            (1, Quantifier(1, None)),
            (2, Quantifier(2, None)),
        ],
    )
    def test_ge(self, multiplier, expected):
        pattern = Pattern("a") >= multiplier
        assert pattern._quantifier == expected

    @pytest.mark.parametrize(
        "multiplier, expected",
        [
            (1, Quantifier(None, 0)),
            (2, Quantifier(None, 1)),
        ],
    )
    def test_lt(self, multiplier, expected):
        pattern = Pattern("a") < multiplier
        assert pattern._quantifier == expected

    def test_lt_invalid(self):
        pattern = Pattern("a")
        with pytest.raises(ValueError, match=r"Can only repeat by a positive integer"):
            pattern < 0

    @pytest.mark.parametrize(
        "multiplier, expected",
        [
            (0, Quantifier(None, 0)),
            (1, Quantifier(None, 1)),
            (2, Quantifier(None, 2)),
        ],
    )
    def test_le(self, multiplier, expected):
        pattern = Pattern("a") <= multiplier
        assert pattern._quantifier == expected

    @pytest.mark.parametrize(
        "multiplier",
        [1.0, "b", (1, 2, 3), (1.1, 1), -1],
    )
    def test_comparison_invalid(self, multiplier):
        pattern = Pattern("a")
        with pytest.raises(ValueError, match=r"Can only repeat by a positive integer"):
            pattern > multiplier
        with pytest.raises(ValueError, match=r"Can only repeat by a positive integer"):
            pattern < multiplier
        with pytest.raises(ValueError, match=r"Can only repeat by a positive integer"):
            pattern >= multiplier
        with pytest.raises(ValueError, match=r"Can only repeat by a positive integer"):
            pattern <= multiplier
