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

    @pytest.mark.parametrize("name", ["foo", "bar", "foo1", "foo_bar"])
    def test_group_named(self, name):
        group = Group("abc", name=name)
        assert str(group) == rf"(?P<{name}>abc)"

    def test_group_named_None(self):
        group = Group("abc", name=None)
        assert str(group) == "(abc)"

    @pytest.mark.parametrize(
        "name",
        ["", " ", "1", "1foo", "foo bar", "foo-bar", "foo.bar"],
    )
    def test_group_named_invalid(self, name):
        with pytest.raises(ValueError, match=r"Invalid group name"):
            Group("abc", name=name)

    @pytest.mark.parametrize("name", [1, 1.0, True, False, [], (), {}])
    def test_group_named_invalid_type(self, name):
        with pytest.raises(ValueError, match=r"Group name must be a string"):
            Group("abc", name=name)

    def test_group_named_noncapture(self):
        with pytest.raises(ValueError, match=r"Cannot name a non-capturing group"):
            Group("abc", name="foo", capture=False)

    def test_set_capture(self):
        group = Group("abc", capture=False)
        assert str(group) == "(?:abc)"
        group.capture = True
        assert str(group) == "(abc)"

    def test_set_capture_named(self):
        group = Group("abc", name="foo", capture=True)
        assert str(group) == "(?P<foo>abc)"
        with pytest.raises(ValueError, match=r"cannot be non-capturing"):
            group.capture = False
