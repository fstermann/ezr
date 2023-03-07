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


class Pattern:
    _annotation: str = "Pattern"
    _pattern: str
    _quantifier: Quantifier | None = None

    def __init__(
        self,
        pattern,
        lower: int | None = None,
        upper: int | None = None,
        lazy: bool = False,
    ):
        if not isinstance(pattern, str):
            raise TypeError(f"Pattern must be a string, not {type(pattern)}")
        if not self.is_valid_pattern(pattern):
            err = "Pattern must be a single character or a valid range"
            raise ValueError(err)
        if re.match(ANY_RANGE, pattern):
            left, right = pattern.split("-")
            if left == right:
                raise ValueError("Range must specify distinct values")
            if left > right:
                raise ValueError("Range must be in ascending order")
            self._annotation = "Range: "
            self._annotation += f"Matches a character in the range {pattern}"
        self._pattern = pattern
        self._lower = lower
        self._upper = upper
        if lower is not None or upper is not None:
            self._quantifier = Quantifier(lower=lower, upper=upper, lazy=lazy)

    @classmethod
    def from_quantifier(cls, *pattern, quantifier: Quantifier):
        if len(pattern) != 1:
            raise ValueError("Pattern must be a single string")
        return cls(
            pattern[0],
            lower=quantifier.lower,
            upper=quantifier.upper,
            lazy=quantifier.is_lazy,
        )

    @staticmethod
    def is_valid_pattern(pattern: str) -> bool:
        return re.match(rf"^(\\?[a-zA-Z]|{ANY_RANGE}|.)$", pattern) is not None

    @property
    def pattern(self) -> str:
        return self._pattern

    @property
    def quantifier(self) -> Quantifier | None:
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
            return "Lowercase letter"
        if self.pattern in string.ascii_uppercase:
            return "Uppercase letter"
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
        return self._quantify(Quantifier(lower=0, lazy=lazy))

    def one_or_more(self, lazy: bool = False):
        return self._quantify(Quantifier(lower=1, lazy=lazy))

    def zero_or_one(self, lazy: bool = False):
        return self._quantify(Quantifier(lower=1, upper=1, lazy=lazy))

    def optional(self, lazy: bool = False):
        return self._quantify(Quantifier(upper=1, lazy=lazy))

    def exactly(self, n: int, lazy: bool = False):
        return self._quantify(Quantifier(lower=n, upper=n, lazy=lazy))

    def between(
        self,
        lower: int | None = None,
        upper: int | None = None,
        lazy: bool = False,
    ):
        return self._quantify(Quantifier(lower=lower, upper=upper, lazy=lazy))

    def at_least(self, n: int, lazy: bool = False):
        return self._quantify(Quantifier(lower=n, lazy=lazy))

    def at_most(self, n: int, lazy: bool = False):
        return self._quantify(Quantifier(upper=n, lazy=lazy))

    def _quantify(self, quantifier: Quantifier):
        self._quantifier = quantifier
        return self

    def __str__(self) -> str:
        return f"{self._pattern}{self.quantifier_as_str}"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._pattern!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Pattern):
            return False
        return self._pattern == other._pattern and self._quantifier == other._quantifier

    def __add__(self, other: str | Pattern | EzRegex) -> EzRegex:
        self_patterns = self.__get_patterns(self)
        other_patterns = self.__get_patterns(other)
        return EzRegex(*self_patterns, *other_patterns)

    def __radd__(self, other: str | Pattern | EzRegex) -> EzRegex:
        self_patterns = self.__get_patterns(self)
        other_patterns = self.__get_patterns(other)
        return EzRegex(*other_patterns, *self_patterns)

    @staticmethod
    def is_special_set(x) -> bool:
        return isinstance(x, (Group, CharacterSet))

    @staticmethod
    def __get_patterns(
        x: str | Pattern | EzRegex,
    ) -> Sequence[Pattern | Group | CharacterSet | str]:
        if isinstance(x, EzRegex) and not Pattern.is_special_set(x):
            return x._patterns
        return [x]

    def __mul__(self, other: int) -> EzRegex:
        if isinstance(other, int):
            return self.exactly(other)
        if (
            isinstance(other, tuple)
            and len(other) == 2
            and all(isinstance(x, (int, type(None))) for x in other)
        ):
            return self.between(*other)
        err = "Can only repeat by an integer or a tuple of two integers"
        raise ValueError(err)

    def __rmul__(self, other: int) -> EzRegex:
        return self.__mul__(other)

    def __or__(self, other: str | Pattern | EzRegex) -> EzRegex:
        self_patterns = self.__get_patterns(self)
        other_patterns = self.__get_patterns(other)
        return EzRegex(*self_patterns, "|", *other_patterns)

    def __ror__(self, other: str | Pattern | EzRegex) -> EzRegex:
        self_patterns = self.__get_patterns(self)
        other_patterns = self.__get_patterns(other)
        return EzRegex(*other_patterns, "|", *self_patterns)

    def __gt__(self, other: int) -> EzRegex:
        if not isinstance(other, int) or other < 0:
            raise ValueError("Can only repeat by a positive integer")
        return self.at_least(other + 1)

    def __ge__(self, other: int) -> EzRegex:
        if not isinstance(other, int) or other < 0:
            raise ValueError("Can only repeat by a positive integer")
        return self.at_least(other)

    def __lt__(self, other: int) -> EzRegex:
        if not isinstance(other, int) or other < 1:
            raise ValueError("Can only repeat by a positive integer")
        return self.at_most(other - 1)

    def __le__(self, other: int) -> EzRegex:
        if not isinstance(other, int) or other < 0:
            raise ValueError("Can only repeat by a positive integer")
        return self.at_most(other)


class EzRegex(Pattern):
    _annotation: str = "Regular Expression. Matches the following."
    _enclosing: tuple[str, str] = ("", "")
    _patterns: list[Pattern | Group | CharacterSet]

    def __init__(
        self,
        *patterns,
        lower: int | None = None,
        upper: int | None = None,
        lazy: bool = False,
    ):
        self._patterns = []
        for pat in patterns:
            if not isinstance(pat, (EzRegex, Pattern)):
                self._patterns += [Pattern(p) for p in list(str(pat))]
            else:
                self._patterns += [pat]
        self._lower = lower
        self._upper = upper
        if lower is not None or upper is not None:
            self._quantifier = Quantifier(lower=lower, upper=upper, lazy=lazy)

    @classmethod
    def from_quantifier(cls, *patterns, quantifier: Quantifier):
        return cls(
            *patterns,
            lower=quantifier.lower,
            upper=quantifier.upper,
            lazy=quantifier.is_lazy,
        )

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
        return CharacterSet(*self._patterns)

    def as_group(self):
        return Group(*self._patterns)

    def _quantify(self, quantifier: Quantifier):
        if not isinstance(self, CharacterSet) and len(self._patterns) > 1:
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
        return CharacterSet(Pattern("^"), *p)


class CharacterSet(EzRegex):
    _annotation: str = "Character Set. Matches any of the following."
    _enclosing: tuple[str, str] = ("[", "]")


class Group(EzRegex):
    _annotation: str = "Group"
    _enclosing: tuple[str, str] = ("(", ")")
    _capture: bool = True
    _name: str | None = None

    def __init__(
        self,
        *patterns,
        name: str | None = None,
        capture: bool = True,
        lower: int | None = None,
        upper: int | None = None,
    ):
        super().__init__(*patterns, lower=lower, upper=upper)
        if name and not capture:
            raise ValueError("Cannot name a non-capturing group")
        self.name = name
        self.capture = capture

    @property
    def name(self) -> str | None:
        return self._name

    @name.setter
    def name(self, name: str | None):
        if name and not re.match(r"\w+", name):
            err = "Invalid group name. "
            err += "Please use only alphanumeric characters."
            raise ValueError(err)
        self._name = name

    @property
    def capture(self) -> bool:
        return self._capture

    @capture.setter
    def capture(self, capture: bool):
        if self.name and not capture:
            raise ValueError("Named group cannot be non-capturing")
        self._capture = capture

    @property
    def annotation(self) -> str:
        prefix = "Capturing" if self.capture else "Non-capturing"
        return f"{prefix} {self._annotation}"

    def __str__(self) -> str:
        name = f"?P<{self.name}>" if self.name else ""
        capture = "" if self.capture else "?:"
        prefix = f"{name}{capture}"
        return f"({prefix}{self.patterns_as_str}){self.quantifier_as_str}"


class Quantifier(Pattern):
    _lower: int | None
    _upper: int | None
    _lazy: bool = False
    _special_cases: dict[tuple[int | None, int | None], str] = {
        (0, 1): "?",
        (0, None): "*",
        (1, None): "+",
    }

    def __init__(
        self,
        lower: int | None = None,
        upper: int | None = None,
        *,
        lazy: bool = False,
    ):
        if lower is None and upper is None:
            raise ValueError("At least one bound must be specified")
        if lower is not None and upper is not None and lower > upper:
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

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Quantifier):
            return False
        return (
            self._lower == other._lower
            and self._upper == other._upper
            and self._lazy == other._lazy
        )
