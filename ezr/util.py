from __future__ import annotations


def bold(x: str) -> str:
    return f"\033[1m{x}\033[0m"


def are_valid_quantifier_params(x: tuple[int | None, int | None, int | None]) -> bool:
    lower, upper, _ = x
    if lower is None and upper is None:
        return False
    if lower is None and upper is not None:
        return upper >= 0
    if lower is not None and upper is None:
        return lower >= 0
    assert lower is not None and upper is not None
    return lower >= 0 and upper >= 0 and lower <= upper
