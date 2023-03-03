from __future__ import annotations

import pytest

from ezr import CharacterSet
from ezr import EzRegex
from ezr import Group


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
