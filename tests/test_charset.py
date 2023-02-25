from __future__ import annotations

import pytest

from ezr.ezregex import EzCharset


class TestCharset:
    @pytest.mark.parametrize(
        "patterns, expected",
        [
            (["abc"], "abc"),
            (["a"], "a"),
            (["a", "b"], "[ab]"),
            (["a", "b", "c"], "[abc]"),
        ],
    )
    def test_charset(self, patterns, expected):
        regex = EzCharset(*patterns)
        assert str(regex) == expected
