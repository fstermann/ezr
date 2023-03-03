from __future__ import annotations

import pytest

from ezr import Group
from ezr import Pattern


class TestGroup:
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
        group = Group(*patterns)
        assert str(group) == expected

    @pytest.mark.parametrize(
        "group, expected",
        [
            (Group("abc"), "(abc)"),
            (Group("a", Group("abc")), "(a(abc))"),
            (Group(Group("abc"), "a", "b"), "((abc)ab)"),
            (Group("a", Group("abc"), "c"), "(a(abc)c)"),
        ],
    )
    def test_nested_group(self, group, expected):
        assert str(group) == expected

    def test_group_quantifier(self):
        group = Group("abc")
        print(repr(group))
        group = group.one_or_more()
        print(repr(group))
        assert str(group) == "(abc)+"

    def test_group_quantifier_nested(self):
        group = Group(Pattern("a").one_or_more(), Group("abc"))
        assert str(group) == "(a+(abc))"
