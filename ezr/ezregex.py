from __future__ import annotations

import re
from typing import Sequence

from ezr.util import bold

INDENT = "  "


class ForbiddenError(Exception):
    pass


class EzPattern:
    _pattern: str

    def __init__(self, pattern, times: int | tuple[int, int] | None = None):
        self._pattern = pattern
        if times is None:
            return
        if isinstance(times, int):
            self = self._quantify(exactly(times))
        elif isinstance(times, tuple):
            if len(times) > 2:
                raise ValueError("Can only specify a minimum and maximum")
            if len(times) == 0:
                return
            # TODO: Refactor this, mypy complains
            # Argument 2 to "between" has incompatible type
            # "Union[int, Tuple[int, int]]"; expected "Optional[int]"
            if len(times) == 1:
                self = self._quantify(at_least(times[0]))
            else:
                self = self._quantify(between(times[0], times[1]))

    def compile(self):
        return re.compile(str(self))

    def pretty(self, explain: bool = True) -> str:
        base = f"{self._pattern!s:<4}"
        if not explain:
            return base
        return f"{bold(base)}{INDENT*2} Character. Matches {self._pattern}"

    def zero_or_more(self):
        return self._quantify(zero_or_more)

    def one_or_more(self):
        return self._quantify(one_or_more)

    def zero_or_one(self):
        return self._quantify(zero_or_one)

    def optional(self, n: int | tuple[int, int] = 1):
        if isinstance(n, tuple):
            if len(n) > 2:
                raise ValueError("Can only specify a minimum and maximum")
            if len(n) == 0:
                quantifier = exactly(0)
            if len(n) == 1:
                quantifier = at_least(n[0])
            else:
                quantifier = between(n[0], n[1])
        else:
            quantifier = between(0, n)
        return self._quantify(quantifier)

    def exactly(self, n):
        return self._quantify(exactly(n))

    def between(self, lower, upper):
        return self._quantify(between(lower, upper))

    def at_least(self, n):
        return self._quantify(at_least(n))

    def at_most(self, n):
        return self._quantify(at_most(n))

    def _quantify(self, quantifier: EzQuantifier):
        return EzRegex(self, quantifier)

    def __str__(self) -> str:
        return self._pattern

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._pattern!r})"

    def __add__(self, other: str | EzPattern | EzRegex) -> EzRegex:
        self_patterns: Sequence[str | EzPattern | EzRegex]
        other_patterns: Sequence[str | EzPattern | EzRegex]
        self_patterns, other_patterns = [self], [other]
        if isinstance(self, EzRegex):
            self_patterns = self._patterns
        if isinstance(other, EzRegex):
            other_patterns = other._patterns
        return EzRegex(*self_patterns, *other_patterns)

    def __radd__(self, other: str | EzPattern | EzRegex) -> EzRegex:
        self_patterns: Sequence[str | EzPattern | EzRegex]
        other_patterns: Sequence[str | EzPattern | EzRegex]
        self_patterns, other_patterns = [self], [other]
        if isinstance(self, EzRegex):
            self_patterns = self._patterns
        if isinstance(other, EzRegex):
            other_patterns = other._patterns
        return EzRegex(*other_patterns, *self_patterns)

    def __mul__(self, other: int | EzPattern | EzRegex) -> EzRegex:
        if not isinstance(other, int):
            raise ValueError("Can only repeat by an integer")
        return self.exactly(other)

    def __rmul__(self, other: int | EzPattern | EzRegex) -> EzRegex:
        if not isinstance(other, int):
            raise ValueError("Can only repeat by an integer")
        return self.exactly(other)

    def __or__(self, other: str | EzPattern | EzRegex) -> EzRegex:
        return EzRegex(self, "|", other)

    def __ror__(self, other: str | EzPattern | EzRegex) -> EzRegex:
        return EzRegex(other, "|", self)


class EzRegex(EzPattern):
    _patterns: list[EzPattern | EzRegex]

    def __init__(self, *patterns):
        self._patterns = [
            EzPattern(str(p)) if not isinstance(p, (EzRegex, EzPattern)) else p
            for p in patterns
        ]

    def compile(self):
        return re.compile(str(self))

    def as_charset(self):
        return EzCharacterSet(*self._patterns)

    def as_group(self):
        return EzGroup(*self._patterns)

    def pretty(self, explain: bool = True) -> str:
        reprs = [p.pretty(explain=explain) for p in self._patterns]
        lines = [f"{INDENT}{s}" for r in reprs for s in r.split("\n")]
        return "\n".join(lines)

    def _quantify(self, quantifier: EzQuantifier):
        if len(self._patterns) > 1:
            self = self.as_charset()
        return super()._quantify(quantifier)

    def __str__(self) -> str:
        return "".join(str(p) for p in self._patterns)

    def __repr__(self) -> str:
        reprs = [repr(p) for p in self._patterns]
        lines = [f"{INDENT}{s}" for r in reprs for s in r.split("\n")]
        _str = "\n".join(lines)
        return f"{self.__class__.__name__}(\n{_str}\n)"

    def __invert__(self):
        p = self._patterns
        if p and str(p[0]) == "^":
            return EzRegex(*p[1:])
        return EzCharacterSet(EzPattern("^"), *p)


class EzCharacterSet(EzRegex):
    def __str__(self) -> str:
        inner = super().__str__()
        if len(self._patterns) <= 1:
            return inner
        return f"[{inner}]"

    def pretty(self, explain: bool = True) -> str:
        if not explain:
            return str(self)
        patterns = super().pretty(explain=explain).splitlines()
        _str = "\n".join(f"{INDENT}{p}" for p in patterns)
        _annotation = "Character set."
        _explanation = f"Matches any of the following\n{_str}\n"
        return f"[{INDENT*2}{_annotation} {_explanation}]"


any_of = EzCharacterSet


class EzGroup(EzRegex):
    def __str__(self) -> str:
        inner = super().__str__()
        return f"({inner})"


class EzQuantifier(EzPattern):
    def __init__(
        self,
        *,
        lower: int | None = None,
        upper: int | None = None,
        exact: int | None = None,
    ):
        if lower is None and upper is None and exact is None:
            raise ValueError("At least one bound must be specified")
        if lower and upper and lower > upper:
            raise ValueError("Lower bound cannot be greater than upper bound")
        lower = 0 if upper == 1 else lower
        self._lower = lower
        self._upper = upper
        self._exact = exact

    def pretty(self, explain: bool = True) -> str:
        prefix = f"{self!s:<4}"
        prefix = f"{INDENT}{bold(prefix)}"
        if not explain:
            return prefix
        prefix += f"{INDENT*2}Quantifier. Matches"
        suffix = "of the preceding token"
        if self._exact is not None:
            return f"{prefix} exactly {self._exact} {suffix}"
        low, upp = self._lower, self._upper
        if low == upp:
            return f"{prefix} exactly {low} {suffix}"
        if low == 0 and upp is None:
            return f"{prefix} zero or more {suffix}"
        if low == 1 and upp is None:
            return f"{prefix} one or more {suffix}"
        if low == 0 and upp == 1:
            return f"{prefix} zero or one {suffix}"
        if low is None:
            return f"{prefix} at most {upp} {suffix}"
        if upp is None:
            return f"{prefix} at least {low} {suffix}"
        return f"{prefix} between {low} and {upp} {suffix}"

    def __str__(self) -> str:
        if self._exact is not None:
            return f"{{{self._exact}}}"
        low, upp = self._lower, self._upper
        lookup = {
            (0, 1): "?",
            (0, None): "*",
            (1, None): "+",
        }
        if (low, upp) not in lookup:
            return f"{{{low or ''},{upp or ''}}}"
        return lookup[(low, upp)]  # type: ignore

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({str(self)})"


digit = EzPattern(r"\d")
whitespace = EzPattern(r"\s")
word = EzPattern(r"\w")
non_digit = EzPattern(r"\D")
non_whitespace = EzPattern(r"\S")
non_word = EzPattern(r"\W")
any_char = EzPattern(r".")
start_of_string = EzPattern(r"^")
end_of_string = EzPattern(r"$")
start_of_word = EzPattern(r"\b")
end_of_word = EzPattern(r"\B")

zero_or_more = EzQuantifier(lower=0)
one_or_more = EzQuantifier(lower=1)
zero_or_one = EzQuantifier(lower=0, upper=1)


def exactly(n: int) -> EzQuantifier:
    return EzQuantifier(exact=n)


def between(n: int | None = None, m: int | None = None) -> EzQuantifier:
    return EzQuantifier(lower=n, upper=m)


def at_least(n: int) -> EzQuantifier:
    return EzQuantifier(lower=n)


def at_most(n: int) -> EzQuantifier:
    return EzQuantifier(upper=n)


# ---


def optional(
    *patterns: str | EzPattern | EzRegex,
    n: int | tuple[int, int] = 1,
) -> EzRegex:
    return EzRegex(*patterns).optional(n)
