from __future__ import annotations

import pytest

from ezr import EzGroup
from ezr import EzPattern


class TestEzGroup:
    @pytest.mark.parametrize(
        "patterns, expected",
        [
            (["abc"], "(abc)"),
            (["a"], "(a)"),
            (["a", "b"], "(ab)"),
            (["a", "b", "c"], "(abc)"),
        ],
    )
    def test_simple_group(self, patterns, expected):
        group = EzGroup(*patterns)
        assert str(group) == expected

    @pytest.mark.parametrize(
        "group, expected",
        [
            (EzGroup("abc"), "(abc)"),
            (EzGroup("a", EzGroup("abc")), "(a(abc))"),
            (EzGroup(EzGroup("abc"), "a", "b"), "((abc)ab)"),
            (EzGroup("a", EzGroup("abc"), "c"), "(a(abc)c)"),
        ],
    )
    def test_nested_group(self, group, expected):
        assert str(group) == expected

    def test_group_quantifier(self):
        group = EzGroup("abc")
        print(repr(group))
        group = group.one_or_more()
        print(repr(group))
        assert str(group) == "(abc)+"

    def test_group_quantifier_nested(self):
        group = EzGroup(EzPattern("a").one_or_more(), EzGroup("abc"))
        assert str(group) == "(a+(abc))"
