from __future__ import annotations

import itertools

import pytest

from ezr.util import are_valid_quantifier_params

quantifier_params = list(
    itertools.product(
        (None, 0, 1, 2),
        (None, 0, 1, 2),
        (False, True),
    ),
)


@pytest.fixture(params=list(quantifier_params))
def lower_upper_lazy(request):
    return request.param


@pytest.fixture(params=list(filter(are_valid_quantifier_params, quantifier_params)))
def valid_quantifier_params(request):
    return dict(zip(("lower", "upper", "lazy"), request.param))


# @pytest.fixture(
#     params=list(
#         filter(lambda x: not are_valid_quantifier_params(x), quantifier_params),
#     ),
# )
# def invalid_quantifier_params(request):
#     return dict(zip(("lower", "upper", "lazy"), request.param))


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
