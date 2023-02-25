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

    def __str__(self) -> str:
        return self._pattern

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._pattern!r})"

    def __add__(self, other: str | EzPattern | EzRegex) -> EzRegex:
        return EzRegex(self, other)

    def __radd__(self, other: str | EzPattern | EzRegex) -> EzRegex:
        return EzRegex(other, self)


class EzRegex:
    _patterns: list[EzPattern | EzRegex]

    def __init__(self, *patterns):
        self._patterns = [
            EzPattern(p) if not isinstance(p, (EzRegex, EzPattern)) else p
            for p in patterns
        ]
        self._pattern = patterns

    def __str__(self) -> str:
        return "".join(str(p) for p in self._patterns)

    def __repr__(self) -> str:
        reprs = [repr(p) for p in self._patterns]
        lines = [f"  {s}" for r in reprs for s in r.split("\n")]
        _str = "\n".join(lines)
        return f"{self.__class__.__name__}(\n{_str}\n)"

    def compile(self):
        return re.compile(str(self))

    def __invert__(self):
        p = self._patterns
        if p and str(p[0]) == "^":
            return EzRegex(*p[1:])
        return EzCharSet(EzPattern("^"), *p)

    def __add__(self, other: str | EzPattern | EzRegex) -> EzRegex:
        return EzRegex(self, other)

    def __radd__(self, other: str | EzPattern | EzRegex) -> EzRegex:
        return EzRegex(other, self)


class EzCharSet(EzRegex):
    def __str__(self) -> str:
        return f"[{super().__str__()}]"


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
