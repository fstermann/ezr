from __future__ import annotations

import re
from typing import Sequence

from ezr.util import bold

INDENT = "  "


class ForbiddenError(Exception):
    pass


class EzPattern:
    _pattern: str
    _quantifier: EzQuantifier | None = None

    def __init__(
        self,
        pattern,
        lower: int | None = None,
        upper: int | None = None,
    ):
        self._pattern = pattern
        self._lower = lower
        self._upper = upper
        if lower is not None or upper is not None:
            self._quantifier = EzQuantifier(lower=lower, upper=upper)

    @classmethod
    def from_quantifier(cls, pattern, quantifier: EzQuantifier):
        return cls(pattern, lower=quantifier.lower, upper=quantifier.upper)

    @property
    def pattern(self) -> str:
        return self._pattern

    @property
    def quantifier(self) -> EzQuantifier | None:
        return self._quantifier

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

    def optional(self):
        return self._quantify(at_most(1))

    def exactly(self, n):
        return self._quantify(exactly(n))

    def between(self, lower, upper):
        return self._quantify(between(lower, upper))

    def at_least(self, n):
        return self._quantify(at_least(n))

    def at_most(self, n):
        return self._quantify(at_most(n))

    def _quantify(self, quantifier: EzQuantifier):
        return self.from_quantifier(self._pattern, quantifier)

    def __str__(self) -> str:
        quant = str(self.quantifier) if self.quantifier else ""
        return f"{self._pattern}{quant}"

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

    def __init__(
        self,
        *patterns,
        lower: int | None = None,
        upper: int | None = None,
    ):
        self._patterns = [
            EzPattern(str(p)) if not isinstance(p, (EzRegex, EzPattern)) else p
            for p in patterns
        ]
        self._lower = lower
        self._upper = upper
        if lower is not None or upper is not None:
            self._quantifier = EzQuantifier(lower=lower, upper=upper)

    @classmethod
    def from_quantifier(cls, patterns, quantifier: EzQuantifier):
        return cls(*patterns, lower=quantifier.lower, upper=quantifier.upper)

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
        return self.from_quantifier(self._patterns, quantifier)
        # return super()._quantify(quantifier)

    def __str__(self) -> str:
        quant = str(self.quantifier) if self.quantifier else ""
        patterns = "".join(str(p) for p in self._patterns)
        return f"{patterns}{quant}"

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
        if len(self._patterns) <= 1:
            return super().__str__()
        quant = str(self.quantifier) if self.quantifier else ""
        patterns = "".join(str(p) for p in self._patterns)
        return f"[{patterns}]{quant}"

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
    ):
        if lower is None and upper is None:
            raise ValueError("At least one bound must be specified")
        if lower and upper and lower > upper:
            raise ValueError("Lower bound cannot be greater than upper bound")
        lower = 0 if upper == 1 else lower
        self._lower = lower
        self._upper = upper

    @property
    def lower(self) -> int | None:
        return self._lower

    @property
    def upper(self) -> int | None:
        return self._upper

    def pretty(self, explain: bool = True) -> str:
        prefix = f"{self!s:<4}"
        prefix = f"{INDENT}{bold(prefix)}"
        if not explain:
            return prefix
        prefix += f"{INDENT*2}Quantifier. Matches"
        suffix = "of the preceding token"
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
        low, upp = self._lower, self._upper
        if low == upp and low is not None:
            return f"{{{low}}}"
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
    return EzQuantifier(lower=n, upper=n)


def between(n: int | None = None, m: int | None = None) -> EzQuantifier:
    return EzQuantifier(lower=n, upper=m)


def at_least(n: int) -> EzQuantifier:
    return EzQuantifier(lower=n)


def at_most(n: int) -> EzQuantifier:
    return EzQuantifier(upper=n)


# ---


def optional(
    *patterns: str | EzPattern | EzRegex,
) -> EzRegex:
    return EzRegex(*patterns).optional()
