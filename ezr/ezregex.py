from __future__ import annotations

import re
import string
from typing import Sequence

from ezr.util import bold

INDENT = "  "
TREE_START = "┌─"
TREE_INDENT = "│ "
TREE_BRANCH = "├─"
TREE_END = "└─"
TREE_LINE = "─"

ALNUM = r"a-zA-Z0-9"
LCASE_RANGE = r"[a-z]-[a-z]"
UCASE_RANGE = r"[A-Z]-[A-Z]"
NUM_RANGE = r"[0-9]-[0-9]"
ANY_RANGE = rf"{LCASE_RANGE}|{UCASE_RANGE}|{NUM_RANGE}"


class ForbiddenError(Exception):
    pass


class EzPattern:
    _annotation: str = "Pattern"
    _pattern: str
    _quantifier: EzQuantifier | None = None

    def __init__(
        self,
        pattern,
        lower: int | None = None,
        upper: int | None = None,
    ):
        if not isinstance(pattern, str):
            raise TypeError(f"Pattern must be a string, not {type(pattern)}")
        if not self.is_valid_pattern(pattern):
            raise ValueError("Pattern must be a single character or a range")
        if re.match(ANY_RANGE, pattern):
            left, right = pattern.split("-")
            if left > right:
                raise ValueError("Range must be in ascending order")
            self._annotation = "Range: "
            self._annotation += f"Matches a character in the range {pattern}"
        self._pattern = pattern
        self._lower = lower
        self._upper = upper
        if lower is not None or upper is not None:
            self._quantifier = EzQuantifier(lower=lower, upper=upper)

    @classmethod
    def from_quantifier(cls, pattern, quantifier: EzQuantifier):
        return cls(pattern, lower=quantifier.lower, upper=quantifier.upper)

    @staticmethod
    def is_valid_pattern(pattern: str) -> bool:
        # rf"^\\?({ANY_RANGE}|[{ALNUM}.^$| +_@-])$"
        return re.match(rf"^\\?[a-zA-Z]|{ANY_RANGE}|.$", pattern) is not None

    @property
    def pattern(self) -> str:
        return self._pattern

    @property
    def quantifier(self) -> EzQuantifier | None:
        return self._quantifier

    @property
    def quantifier_as_str(self) -> str:
        if self._quantifier is None:
            return ""
        return str(self._quantifier)

    @property
    def pattern_type(self) -> str:
        if self.pattern in string.digits:
            return "Digit"
        if self.pattern in string.ascii_lowercase:
            return "Lowercase Letter"
        if self.pattern in string.ascii_uppercase:
            return "Uppercase Letter"
        if self.pattern in string.whitespace:
            return "Whitespace"
        if self.pattern == "|":
            return "Alternation"
        if self.pattern in string.punctuation:
            return "Punctuation"
        return "Character"

    @property
    def annotation(self) -> str:
        return self._annotation

    @property
    def explanation(self) -> str:
        if self.pattern == "|":
            return (
                f"{self.pattern_type} (OR). "
                "Matches expression on either side of the '|'"
            )
        return f"{self.pattern_type}. Matches '{self.pattern}'"

    def compile(self):
        return re.compile(str(self))

    @property
    def explain(self) -> str:
        indent = " " if self.pattern == "|" else ""
        base = f"{indent}{self._pattern!s:<4}"
        pattern = f"{bold(base)}{INDENT}{self.explanation}"
        if self.quantifier is None:
            return pattern
        return f"{pattern}\n{INDENT}{self.quantifier.explain}"

    def zero_or_more(self, lazy: bool = False):
        return self._quantify(zero_or_more(lazy=lazy))

    def one_or_more(self, lazy: bool = False):
        return self._quantify(one_or_more(lazy=lazy))

    def zero_or_one(self, lazy: bool = False):
        return self._quantify(zero_or_one(lazy=lazy))

    def optional(self, lazy: bool = False):
        return self._quantify(at_most(1, lazy=lazy))

    def exactly(self, n: int, lazy: bool = False):
        return self._quantify(exactly(n, lazy=lazy))

    def between(
        self,
        lower: int | None = None,
        upper: int | None = None,
        lazy: bool = False,
    ):
        return self._quantify(between(lower, upper, lazy=lazy))

    def at_least(self, n: int, lazy: bool = False):
        return self._quantify(at_least(n, lazy=lazy))

    def at_most(self, n: int, lazy: bool = False):
        return self._quantify(at_most(n, lazy=lazy))

    def _quantify(self, quantifier: EzQuantifier):
        self._quantifier = quantifier
        return self

    def __str__(self) -> str:
        return f"{self._pattern}{self.quantifier_as_str}"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._pattern!r})"

    def __add__(self, other: str | EzPattern | EzRegex) -> EzRegex:
        self_patterns = self.__get_patterns(self)
        other_patterns = self.__get_patterns(other)
        return EzRegex(*self_patterns, *other_patterns)

    def __radd__(self, other: str | EzPattern | EzRegex) -> EzRegex:
        self_patterns = self.__get_patterns(self)
        other_patterns = self.__get_patterns(other)
        return EzRegex(*other_patterns, *self_patterns)

    @staticmethod
    def is_special_set(x) -> bool:
        return isinstance(x, (EzGroup, EzCharacterSet))

    @staticmethod
    def __get_patterns(
        x: str | EzPattern | EzRegex,
    ) -> Sequence[EzPattern | EzGroup | EzCharacterSet | str]:
        if isinstance(x, EzRegex) and not EzPattern.is_special_set(x):
            return x._patterns
        return [x]

    def __mul__(self, other: int) -> EzRegex:
        if isinstance(other, int):
            return self.exactly(other)
        if (
            isinstance(other, tuple)
            and len(other) == 2
            and all(isinstance(x, int) for x in other)
        ):
            return self.between(*other)
        err = "Can only repeat by an integer or a tuple of two integers"
        raise ValueError(err)

    def __rmul__(self, other: int) -> EzRegex:
        return self.__mul__(other)

    def __or__(self, other: str | EzPattern | EzRegex) -> EzRegex:
        self_patterns = self.__get_patterns(self)
        other_patterns = self.__get_patterns(other)
        return EzRegex(*self_patterns, "|", *other_patterns)

    def __ror__(self, other: str | EzPattern | EzRegex) -> EzRegex:
        self_patterns = self.__get_patterns(self)
        other_patterns = self.__get_patterns(other)
        return EzRegex(*other_patterns, "|", *self_patterns)

    def __gt__(self, other: int) -> EzRegex:
        if not isinstance(other, int):
            raise ValueError("Can only repeat by an integer")
        return self.at_least(other + 1)


class EzRegex(EzPattern):
    _annotation: str = "Regular Expression. Matches the following."
    _enclosing: tuple[str, str] = ("", "")
    _patterns: list[EzPattern | EzGroup | EzCharacterSet]

    def __init__(
        self,
        *patterns,
        lower: int | None = None,
        upper: int | None = None,
    ):
        self._patterns = []
        for pat in patterns:
            if not isinstance(pat, (EzRegex, EzPattern)):
                self._patterns += [EzPattern(p) for p in list(str(pat))]
            else:
                self._patterns += [pat]
        self._lower = lower
        self._upper = upper
        if lower is not None or upper is not None:
            self._quantifier = EzQuantifier(lower=lower, upper=upper)

    @classmethod
    def from_quantifier(cls, patterns, quantifier: EzQuantifier):
        return cls(*patterns, lower=quantifier.lower, upper=quantifier.upper)

    @property
    def patterns_as_str(self) -> str:
        return "".join(str(p) for p in self._patterns)

    @property
    def explain(self) -> str:
        lines = []
        for p in self._patterns:
            indent = f"{TREE_INDENT} "
            if not isinstance(p, EzRegex):
                indent += "   "  # INDENT * 2
            lines += [f"{indent}{s}" for s in p.explain.split("\n")]
            if isinstance(p, EzRegex):
                lines += [TREE_INDENT]

        patterns = "\n".join(lines)

        start = f"{TREE_START} {bold(self._enclosing[0])}"
        end = f"{TREE_END} {bold(self._enclosing[1])}"
        quant = "\n" + self.quantifier.explain if self.quantifier else ""

        return f"{start} {self._annotation}\n{patterns}\n{end}{quant}"

    def as_charset(self):
        return EzCharacterSet(*self._patterns)

    def as_group(self):
        return EzGroup(*self._patterns)

    def _quantify(self, quantifier: EzQuantifier):
        if not isinstance(self, EzCharacterSet) and len(self._patterns) > 1:
            self = self.as_group()
        return super()._quantify(quantifier)

    def __str__(self) -> str:
        left, right = self._enclosing
        pattern = f"{left}{self.patterns_as_str}{right}"
        return f"{pattern}{self.quantifier_as_str}"

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
    _annotation: str = "Character Set. Matches any of the following."
    _enclosing: tuple[str, str] = ("[", "]")


class EzGroup(EzRegex):
    _annotation: str = "Group"
    _enclosing: tuple[str, str] = ("(", ")")
    _capture: bool = True

    def __init__(
        self,
        *patterns,
        capture: bool = True,
        lower: int | None = None,
        upper: int | None = None,
    ):
        super().__init__(*patterns, lower=lower, upper=upper)
        self._capture = capture

    @property
    def capture(self) -> bool:
        return self._capture

    @property
    def annotation(self) -> str:
        prefix = "Capturing" if self.capture else "Non-capturing"
        return f"{prefix} {self._annotation}"

    def __str__(self) -> str:
        capture = "" if self.capture else "?:"
        return f"({capture}{self.patterns_as_str}){self.quantifier_as_str}"


class EzQuantifier(EzPattern):
    _lazy = False
    _special_cases: dict[tuple[int | None, int | None], str] = {
        (0, 1): "?",
        (0, None): "*",
        (1, None): "+",
    }

    def __init__(
        self,
        *,
        lower: int | None = None,
        upper: int | None = None,
        lazy: bool = False,
    ):
        if lower is None and upper is None:
            raise ValueError("At least one bound must be specified")
        if lower and upper and lower > upper:
            raise ValueError("Lower bound cannot be greater than upper bound")
        lower = 0 if upper == 1 else lower
        self._lower = lower
        self._upper = upper
        self._lazy = lazy

    @property
    def lower(self) -> int | None:
        return self._lower

    @property
    def upper(self) -> int | None:
        return self._upper

    @property
    def is_lazy(self) -> bool:
        return self._lazy

    @property
    def explain(self) -> str:
        prefix = f"{self!s:<4}"
        prefix = f"{INDENT}{TREE_END} {bold(prefix)}"
        prefix += f"{INDENT}Quantifier. Matches"
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

    def lazy(self):
        self._lazy = True
        return self

    def __str__(self) -> str:
        low, upp = self._lower, self._upper
        assert low is not None or upp is not None

        base = f"{{{low or ''},{upp or ''}}}"
        if low == upp and low is not None:
            base = f"{{{low}}}"
        base = self._special_cases.get((low, upp), base)
        return f"{base}{'?' if self._lazy else ''}"

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


def zero_or_more(lazy: bool = False) -> EzQuantifier:
    return EzQuantifier(lower=0, lazy=lazy)


def one_or_more(lazy: bool = False) -> EzQuantifier:
    return EzQuantifier(lower=1, lazy=lazy)


def zero_or_one(lazy: bool = False) -> EzQuantifier:
    return EzQuantifier(lower=0, upper=1, lazy=lazy)


def exactly(n: int, lazy: bool = False) -> EzQuantifier:
    return EzQuantifier(lower=n, upper=n, lazy=lazy)


def between(
    n: int | None = None,
    m: int | None = None,
    lazy: bool = False,
) -> EzQuantifier:
    return EzQuantifier(lower=n, upper=m, lazy=lazy)


def at_least(n: int, lazy: bool = False) -> EzQuantifier:
    return EzQuantifier(lower=n, lazy=lazy)


def at_most(n: int, lazy: bool = False) -> EzQuantifier:
    return EzQuantifier(upper=n, lazy=lazy)


# ---


def optional(
    *patterns: str | EzPattern | EzRegex,
) -> EzRegex:
    return EzRegex(*patterns).optional()


def any_of(
    *patterns: str | EzPattern | EzRegex,
) -> EzRegex:
    """Match any of the given patterns.

    Args:
        patterns (str | EzPattern | EzRegex): Any number of patterns.


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
        return EzCharacterSet(patterns[0])
    if len(patterns) > 1:
        if any(not EzPattern.is_valid_pattern(str(p)) for p in patterns):
            new_patterns: list[str | EzPattern | EzRegex]
            new_patterns = ["|"] * (len(patterns) * 2 - 1)
            new_patterns[0::2] = patterns
            return EzGroup(*new_patterns)
        return EzCharacterSet(*patterns)
    raise TypeError(f"Dont know how to handle {patterns}")
