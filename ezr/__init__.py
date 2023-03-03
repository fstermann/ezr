# flake8: noqa
from __future__ import annotations

from ezr.ezregex import CharacterSet
from ezr.ezregex import EzRegex
from ezr.ezregex import Group
from ezr.ezregex import Pattern
from ezr.ezregex import Quantifier
from ezr.helper import *
from ezr.quantifier import *

digit = Pattern(r"\d")
whitespace = Pattern(r"\s")
word = Pattern(r"\w")
non_digit = Pattern(r"\D")
non_whitespace = Pattern(r"\S")
non_word = Pattern(r"\W")
any_char = Pattern(r".")
start_of_string = Pattern(r"^")
end_of_string = Pattern(r"$")
start_of_word = Pattern(r"\b")
end_of_word = Pattern(r"\B")
