from __future__ import annotations

import pytest

from ezr.util import are_valid_quantifier_params


class TestUtil:
    @pytest.mark.parametrize(
        "params, expected",
        [
            ((0, None, False), True),
            ((1, None, False), True),
            ((2, None, False), True),
            ((None, 0, False), True),
            ((None, 1, False), True),
            ((None, 2, False), True),
            ((0, 0, False), True),
            ((0, 1, False), True),
            ((0, 2, False), True),
            ((1, 1, False), True),
            ((1, 2, False), True),
            ((None, None, False), False),
            ((3, 2, False), False),
            ((2, 1, False), False),
            ((1, 0, False), False),
            ((-1, 0, False), False),
            ((-1, -1, False), False),
            ((-2, -1, False), False),
            ((-1, None, False), False),
            ((None, -1, False), False),
        ],
    )
    def test_are_valid_quantifier_params(self, params, expected):
        assert are_valid_quantifier_params(params) == expected
