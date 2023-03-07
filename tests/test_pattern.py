from __future__ import annotations

import itertools
import re

import pytest

from ezr import Pattern
from ezr import Quantifier


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

    @pytest.mark.parametrize(
        "pattern",
        [1, 1.0, True, None, [], {}, (), set()],
    )
    def test_invalid_pattern_type(self, pattern):
        with pytest.raises(TypeError, match=r"Pattern must be a string"):
            Pattern(pattern)

    @pytest.mark.parametrize(
        "lower, upper, lazy",
        list(
            itertools.product(
                (None, 0, 1, 2),
                (None, 0, 1, 2),
                (False, True),
            ),
        ),
    )
    def test_pattern_with_quantifier(self, lower, upper, lazy):
        if lower and upper and lower > upper:
            with pytest.raises(
                ValueError,
                match=r"Lower bound cannot be greater than upper bound",
            ):
                Pattern("a", lower=lower, upper=upper, lazy=lazy)
            return

        pattern_init = Pattern("a", lower=lower, upper=upper, lazy=lazy)
        if lower is None and upper is None:
            assert pattern_init.quantifier is None
            assert str(pattern_init) == "a"
            return

        quantifier_expected = Quantifier(lower=lower, upper=upper, lazy=lazy)
        pattern_expected = Pattern("a")._quantify(quantifier_expected)

        assert pattern_init == pattern_expected
        assert pattern_init.quantifier == quantifier_expected
        assert str(pattern_init) == str(pattern_expected)

    def test_pattern_from_quantifier(self):
        quantifier = Quantifier(lower=0, upper=1, lazy=True)
        pattern = Pattern.from_quantifier("a", quantifier)
        expected = Pattern("a", lower=0, upper=1, lazy=True)

        assert pattern == expected
        assert pattern.quantifier == quantifier
        assert str(pattern) == "a??"

    def test_get_pattern(self):
        pattern = Pattern("a")
        assert pattern.pattern == "a"

    def test_get_annotation(self):
        pattern = Pattern("a")
        assert pattern.annotation == "Pattern"

    @pytest.mark.parametrize(
        "pattern, expected",
        [
            ("a", "Lowercase letter. Matches 'a'"),
            ("A", "Uppercase letter. Matches 'A'"),
            ("1", "Digit. Matches '1'"),
            (" ", "Whitespace. Matches ' '"),
            ("|", "Alternation (OR). Matches expression on either side of the '|'"),
        ],
    )
    def test_get_explanation(self, pattern, expected):
        pattern = Pattern(pattern)
        assert pattern.explanation == expected

    def test_explain(self):
        pattern = Pattern("a")
        expected = r".*?a.*?Lowercase letter. Matches 'a'"
        assert re.match(expected, pattern.explain)

    def test_explain_with_quantifier(self):
        pattern = Pattern("a", lower=1)
        expected = (
            r".*?a.*?Lowercase letter. Matches 'a'\n"
            r".*?└─.*?Quantifier\. Matches one or more of the preceding token"
        )
        assert re.match(expected, pattern.explain)

    def test_pattern_optional(self):
        pattern = Pattern("a").optional()
        expected = Pattern("a", lower=0, upper=1)

        assert pattern == expected
        assert pattern.quantifier == expected.quantifier
        assert str(pattern) == str(expected)

    def test_pattern_equal(self):
        pattern = Pattern("a")
        assert pattern == pattern
        assert pattern == Pattern("a")
        assert pattern != Pattern("b")
        assert pattern != Pattern("a", lower=1)
        assert pattern != Pattern("a", upper=1)
        assert pattern != Pattern("a", lower=1, lazy=True)
        assert pattern != Pattern("a", lower=1, upper=1)
        assert pattern != "a"
