from __future__ import annotations

import pytest

from ezr import Pattern


class TestPattern:
    @pytest.mark.parametrize(
        "pattern, error",
        [
            ("abc", r"Pattern must be a single character or a valid range"),
            ("a-Z", r"Pattern must be a single character or a valid range"),
            ("a-9", r"Pattern must be a single character or a valid range"),
            ("Z-a", r"Pattern must be a single character or a valid range"),
            ("z-a", r"Range must be in ascending order"),
            ("Z-A", r"Range must be in ascending order"),
            ("9-1", r"Range must be in ascending order"),
            ("a-a", r"Range must specify distinct values"),
            ("A-A", r"Range must specify distinct values"),
            ("1-1", r"Range must specify distinct values"),
        ],
    )
    def test_invalid_pattern(self, pattern, error):
        with pytest.raises(ValueError, match=error):
            Pattern(pattern)
