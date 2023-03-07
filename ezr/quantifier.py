from __future__ import annotations

from ezr.ezregex import Quantifier


def zero_or_more(lazy: bool = False) -> Quantifier:
    return Quantifier(lower=0, lazy=lazy)


def one_or_more(lazy: bool = False) -> Quantifier:
    return Quantifier(lower=1, lazy=lazy)


def zero_or_one(lazy: bool = False) -> Quantifier:
    return Quantifier(lower=0, upper=1, lazy=lazy)


def exactly(n: int, lazy: bool = False) -> Quantifier:
    return Quantifier(lower=n, upper=n, lazy=lazy)


def between(
    n: int | None = None,
    m: int | None = None,
    lazy: bool = False,
) -> Quantifier:
    return Quantifier(lower=n, upper=m, lazy=lazy)


def at_least(n: int, lazy: bool = False) -> Quantifier:
    return Quantifier(lower=n, lazy=lazy)


def at_most(n: int, lazy: bool = False) -> Quantifier:
    return Quantifier(upper=n, lazy=lazy)
