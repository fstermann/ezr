from __future__ import annotations

import re


class ForbiddenError(Exception):
    pass


class EzPattern:
    _pattern: str

    def __init__(self, pattern):
        self._pattern = pattern

    def compile(self):
        return re.compile(str(self))

    def zero_or_more(self):
        return self._quantify(zero_or_more)

    def one_or_more(self):
        return self._quantify(one_or_more)

    def zero_or_one(self):
        return self._quantify(zero_or_one)

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
        return EzRegex(self, other)

    def __radd__(self, other: str | EzPattern | EzRegex) -> EzRegex:
        return EzRegex(other, self)

    def __or__(self, other: str | EzPattern | EzRegex) -> EzRegex:
        return EzRegex(self, "|", other)


class EzRegex(EzPattern):
    _patterns: list[EzPattern | EzRegex]

    def __init__(self, *patterns):
        self._patterns = [
            EzPattern(p) if not isinstance(p, (EzRegex, EzPattern)) else p
            for p in patterns
        ]
        self._pattern = patterns

    def compile(self):
        return re.compile(str(self))

    def as_charset(self):
        return EzCharSet(*self._patterns)

    def _quantify(self, quantifier: EzQuantifier):
        if len(self._patterns) > 1:
            self = self.as_charset()
        return super()._quantify(quantifier)

    def __str__(self) -> str:
        return "".join(str(p) for p in self._patterns)

    def __repr__(self) -> str:
        reprs = [repr(p) for p in self._patterns]
        lines = [f"  {s}" for r in reprs for s in r.split("\n")]
        _str = "\n".join(lines)
        return f"{self.__class__.__name__}(\n{_str}\n)"

    def __invert__(self):
        p = self._patterns
        if p and str(p[0]) == "^":
            return EzRegex(*p[1:])
        return EzCharSet(EzPattern("^"), *p)


class EzCharSet(EzRegex):
    def __str__(self) -> str:
        inner = super().__str__()
        if len(self._patterns) <= 1:
            return inner
        return f"[{inner}]"


class EzQuantifier(EzPattern):
    def __init__(
        self,
        *,
        lower: int | None = None,
        upper: int | None = None,
        exact: int | None = None,
    ):
        if lower and upper and lower > upper:
            raise ValueError("Lower bound cannot be greater than upper bound")
        self._lower = lower
        self._upper = upper
        self._exact = exact

    def __str__(self) -> str:
        if self._exact is not None:
            return f"{{{self._exact}}}"
        low, upp = self._lower, self._upper
        if low is None and upp is None:
            raise ValueError("At least one bound must be specified")
        low = 0 if upp == 1 else low

        lookup = {
            (0, 1): "?",
            (0, None): "*",
            (1, None): "+",
        }
        if (low, upp) not in lookup:
            return f"{{{low or ''},{upp or ''}}}"
        return lookup[(low, upp)]  # type: ignore


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


def between(m: int, n: int) -> EzQuantifier:
    return EzQuantifier(lower=m, upper=n)


def at_least(n: int) -> EzQuantifier:
    return EzQuantifier(lower=n)


def at_most(n: int) -> EzQuantifier:
    return EzQuantifier(upper=n)
