from __future__ import annotations

import pytest

from ezr import EzCharacterSet


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
        regex = EzCharacterSet(*patterns)
        assert str(regex) == expected
