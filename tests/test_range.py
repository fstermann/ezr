from __future__ import annotations

import pytest

from ezr import Pattern


class TestEzRange:
    @pytest.mark.parametrize(
        "pattern",
        ["a-z", "A-Z", "0-9", "b-q", "B-M", "1-8"],
    )
    def test_character_range(self, pattern):
        range_ = Pattern(pattern)
        assert str(range_) == pattern
