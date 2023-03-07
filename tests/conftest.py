from __future__ import annotations

import itertools

import pytest


quantifier_params = itertools.product(
    (None, 0, 1, 2),
    (None, 0, 1, 2),
    (False, True),
)


@pytest.fixture(params=list(quantifier_params))
def lower_upper_lazy(request):
    return request.param


def is_valid_quantifier(x):
    lower, upper, _ = x
    if lower is None and upper is None:
        return False
    if lower is None and upper is not None:
        return upper >= 0
    if lower is not None and upper is None:
        return lower >= 0
    return lower >= 0 and upper >= 0 and lower <= upper


@pytest.fixture(params=list(filter(is_valid_quantifier, quantifier_params)))
def valid_quantifier(request):
    return request.param


@pytest.fixture(
    params=list(filter(lambda x: not is_valid_quantifier(x), quantifier_params)),
)
def invalid_quantifier(request):
    return request.param


@pytest.fixture(params=["a", "b", "1", "2"])
def valid_pattern(request):
    return request.param


@pytest.fixture(params=[("a", "b"), ("1", "2")])
def valid_patterns(request):
    return request.param


@pytest.fixture(
    params=[
        (("a",), "a"),
        (("b",), "b"),
        (("a", "b"), "ab"),
    ],
)
def pattern_expected(request):
    return request.param
