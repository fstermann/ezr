from __future__ import annotations

import pytest

from ezr.helper import any_of
from ezr.helper import optional


class TestHelper:
    @pytest.mark.parametrize(
        "patterns, expected",
        [
            (["a", "b", "c"], "[abc]"),
            (["abc"], "[abc]"),
            (["a", "foo", "b", "c"], "(a|foo|b|c)"),
            (["foo", "bar", "baz"], "(foo|bar|baz)"),
        ],
    )
    def test_any_of(self, patterns, expected):
        assert str(any_of(*patterns)) == expected

    @pytest.mark.parametrize(
        "patterns, expected",
        [
            (["a", "b", "c"], "(abc)?"),
            (["abc"], "(abc)?"),
            (["a", "foo", "b", "c"], "(afoobc)?"),
            (["foo", "bar", "baz"], "(foobarbaz)?"),
        ],
    )
    def test_optional(self, patterns, expected):
        assert str(optional(*patterns)) == expected

    def test_any_of_invalid(self):
        with pytest.raises(ValueError, match=r"Invalid pattern"):
            any_of()
