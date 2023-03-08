from __future__ import annotations

from ezr.ezregex import CharacterSet
from ezr.ezregex import EzRegex
from ezr.ezregex import Group
from ezr.ezregex import Pattern


def optional(
    *patterns: str | Pattern | EzRegex,
) -> EzRegex:
    return EzRegex(*patterns).optional()


def any_of(
    *patterns: str | Pattern | EzRegex,
) -> EzRegex:
    """Match any of the given patterns.

    Args:
        patterns (str | Pattern | EzRegex): Any number of patterns.


    Example:
        >>> any_of("a", "b", "c")
        [abc]
        >>> any_of("abc")
        [abc]
        >>> any_of("foo", "bar", "baz")
        (foo|bar|baz)

    Returns:
        EzRegex: EzRegex object.
    """
    if len(patterns) == 1 and isinstance(patterns[0], str):
        return CharacterSet(patterns[0])
    if len(patterns) > 1:
        if any(not Pattern.is_valid_pattern(str(p)) for p in patterns):
            new_patterns: list[str | Pattern | EzRegex]
            new_patterns = ["|"] * (len(patterns) * 2 - 1)
            new_patterns[0::2] = patterns
            return Group(*new_patterns)
        return CharacterSet(*patterns)
    raise ValueError(f"Invalid pattern. Dont know how to handle {patterns}")
