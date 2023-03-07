from __future__ import annotations

import pytest

from ezr import EzRegex
from ezr import Pattern
from ezr import Quantifier


class TestQuantifier:
    def test_zero_or_more(self):
        quant = Quantifier(lower=0)
        assert str(quant) == "*"

    def test_one_or_more(self):
        quant = Quantifier(lower=1)
        assert str(quant) == "+"

    def test_zero_or_one(self):
        quant = Quantifier(lower=0, upper=1)
        assert str(quant) == "?"

    def test_exact(self):
        quant = Quantifier(lower=3, upper=3)
        assert str(quant) == "{3}"

    def test_range(self):
        quant = Quantifier(lower=3, upper=5)
        assert str(quant) == "{3,5}"

    def test_range_no_upper(self):
        quant = Quantifier(lower=3)
        assert str(quant) == "{3,}"

    def test_range_no_lower(self):
        quant = Quantifier(upper=5)
        assert str(quant) == "{,5}"

    def test_upper_1_conversion(self):
        quant = Quantifier(upper=1)
        assert str(quant) == "?"

    def test_lower_greater_than_upper(self):
        with pytest.raises(ValueError):
            Quantifier(lower=5, upper=3)

    def test_no_bounds(self):
        with pytest.raises(ValueError):
            Quantifier()

    def test_set_lazy(self):
        quant = Quantifier(lower=1, lazy=False)
        assert not quant.is_lazy
        quant = quant.lazy()
        assert quant.is_lazy


class TestQuantifierPattern:
    def test_pattern_zero_or_more(self):
        pattern = Pattern("a").zero_or_more()
        assert str(pattern) == "a*"

    def test_pattern_one_or_more(self):
        pattern = Pattern("a").one_or_more()
        assert str(pattern) == "a+"

    def test_pattern_zero_or_one(self):
        pattern = Pattern("a").zero_or_one()
        assert str(pattern) == "a?"

    def test_pattern_exactly(self):
        pattern = Pattern("a").exactly(3)
        assert str(pattern) == "a{3}"

    def test_pattern_between(self):
        pattern = Pattern("a").between(3, 5)
        assert str(pattern) == "a{3,5}"

    def test_pattern_at_least(self):
        pattern = Pattern("a").at_least(3)
        assert str(pattern) == "a{3,}"

    def test_pattern_at_most(self):
        pattern = Pattern("a").at_most(5)
        assert str(pattern) == "a{,5}"


@pytest.fixture(
    params=[
        (["a"], "a"),
        (["a", "b"], "(ab)"),
        (["a", "b", "c"], "(abc)"),
    ],
)
def patterns_expected(request):
    return request.param


class TestQuantifierEzRegex:
    def test_pattern_zero_or_more(self, patterns_expected):
        patterns, expected = patterns_expected
        regex = EzRegex(*patterns).zero_or_more()
        print(regex.quantifier)
        assert str(regex) == f"{expected}*"

    def test_pattern_one_or_more(self, patterns_expected):
        patterns, expected = patterns_expected
        regex = EzRegex(*patterns).one_or_more()
        assert str(regex) == f"{expected}+"

    def test_pattern_zero_or_one(self, patterns_expected):
        patterns, expected = patterns_expected
        regex = EzRegex(*patterns).zero_or_one()
        assert str(regex) == f"{expected}?"

    def test_pattern_exactly(self, patterns_expected):
        patterns, expected = patterns_expected
        regex = EzRegex(*patterns).exactly(3)
        print(regex)
        assert str(regex) == f"{expected}{{3}}"

    def test_pattern_between(self, patterns_expected):
        patterns, expected = patterns_expected
        regex = EzRegex(*patterns).between(3, 5)
        assert str(regex) == f"{expected}{{3,5}}"

    def test_pattern_at_least(self, patterns_expected):
        patterns, expected = patterns_expected
        regex = EzRegex(*patterns).at_least(3)
        assert str(regex) == f"{expected}{{3,}}"

    def test_pattern_at_most(self, patterns_expected):
        patterns, expected = patterns_expected
        regex = EzRegex(*patterns).at_most(5)
        assert str(regex) == f"{expected}{{,5}}"
