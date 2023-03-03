from __future__ import annotations

import pytest

from ezr import CharacterSet


class TestCharset:
    @pytest.mark.parametrize(
        "patterns, expected",
        [
            (["abc"], "[abc]"),
            (["a"], "[a]"),
            (["a", "b"], "[ab]"),
            (["a", "b", "c"], "[abc]"),
        ],
    )
    def test_charset(self, patterns, expected):
        regex = CharacterSet(*patterns)
        assert str(regex) == expected

    def test_charset_quantifier(self):
        regex = CharacterSet("abc")
        regex = regex.one_or_more()
        assert str(regex) == "[abc]+"
