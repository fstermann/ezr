[![build status](https://github.com/fstermann/ezr/actions/workflows/main.yml/badge.svg)](https://github.com/fstermann/ezr/actions/workflows/main.yml)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/fstermann/ezr/main.svg)](https://results.pre-commit.ci/latest/github/fstermann/ezr/main)
![code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)

# ezr

`/ˈiːzi ar/`

Easier regex creation in Python.

This libray is designed to make easy and self-explanatory regex expressions.
Inspired by the javascript library [magic-regexp](https://github.com/danielroe/magic-regexp).

## Installation

```bash
pip install ezr
```

## Usage

You can create a regular expression by creating a new `EzRegex` object.

```python
import ezr

ezr.EzRegex("Hello World")
# Hello World
```
A few more ways to achieve the same result:
```python
ezr.EzRegex("Hello", "World")
ezr.EzRegex("Hello") + "World"
"Hello" + ezr.EzRegex("World")
ezr.EzRegex("H", "e", "l", "l", "o", " ", "W", "o", "r", "l", "d")
```

`ezr` will break down your input to and store it in a tree structure.
This allows you to easily modify the regex later on.
The structure of the above example would look like this:
```python
EzRegex(
  Pattern('H')
  Pattern('e')
  Pattern('l')
  Pattern('l')
  Pattern('o')
  Pattern(' ')
  Pattern('W')
  Pattern('o')
  Pattern('r')
  Pattern('l')
  Pattern('d')
)
```


### Quantifier

You can use the `*` operator to repeat a pattern.
```python
ezr.Group("Hello") * 3
# (Hello){3}
```

You can also specify a range of repetitions. Below will match the expression "Hello" between 2 and 4 times.
```python
ezr.Group("Hello") * (2, 4)
# (Hello){2,4}
```

If you want to match the expression at least a certain number of times, you can use the `>=` operator or the `.at_least()` method.
```python
ezr.Group("Hello") >= 3
ezr.Group("Hello").at_least(3)
# (Hello){3,}
```

Using `>` will match the expression more than a certain number of times.
```python
ezr.Group("Hello") > 3
# (Hello){4,}
```

The same is possible for the less (or equal) operator `<` (`<=`) and `.at_most()`.
```python
ezr.Group("Hello") < 3
# (Hello){,2}

ezr.Group("Hello") <= 3
ezr.Group("Hello").at_most(3)
# (Hello){,3}
```

## Examples

Create a regex that matches a phone number.
```python
from ezr import any_of


sep = any_of("-", " ").optional()
regex = digit * 3 + sep + digit * 3 + sep + digit * 4

print(regex)
# \d{4}[- ]?\d{4}[- ]?\d{4}
print(regex.explain)
# ┌─  Regular Expression. Matches the following.
# │     \d  Character. Matches '\d'
# │         └─ {4}   Quantifier. Matches exactly 4 of the preceding token
# │  ┌─ [ Character Set. Matches any of the following.
# │  │     -     Punctuation. Matches '-'
# │  │           Whitespace. Matches ' '
# │  └─ ]
# │    └─ ?     Quantifier. Matches zero or one of the preceding token
# │
# │     \d  Character. Matches '\d'
# │         └─ {4}   Quantifier. Matches exactly 4 of the preceding token
# │  ┌─ [ Character Set. Matches any of the following.
# │  │     -     Punctuation. Matches '-'
# │  │           Whitespace. Matches ' '
# │  └─ ]
# │    └─ ?     Quantifier. Matches zero or one of the preceding token
# │
# │     \d  Character. Matches '\d'
# │         └─ {4}   Quantifier. Matches exactly 4 of the preceding token
# └─
```

Create a regex that matches a emails of specific domains.
```python
from ezr import any_of


username = (digit | word | any_of("_.+-")) > 0
domain = any_of("gmail", "yahoo", "hotmail")
extension = any_of("com", "net", "org")
email = username + "@" + domain + "." + extension

print(email)
# (\d{4}|\w|[_.+-])+@(gmail|yahoo|hotmail).(com|net|org)
print(email.explain)
# ┌─  Regular Expression. Matches the following.
# │  ┌─ ( Group
# │  │     \d    Character. Matches '\d'
# │  │         └─ {4}   Quantifier. Matches exactly 4 of the preceding token
# │  │      |     Alternation (OR). Matches expression on either side of the '|'
# │  │     \w    Character. Matches '\w'
# │  │      |     Alternation (OR). Matches expression on either side of the '|'
# │  │  ┌─ [ Character Set. Matches any of the following.
# │  │  │     _     Punctuation. Matches '_'
# │  │  │     .     Punctuation. Matches '.'
# │  │  │     +     Punctuation. Matches '+'
# │  │  │     -     Punctuation. Matches '-'
# │  │  └─ ]
# │  │
# │  └─ )
# │    └─ +     Quantifier. Matches one or more of the preceding token
# │
# │     @     Punctuation. Matches '@'
# │  ┌─ ( Group
# │  │     g     Lowercase letter. Matches 'g'
# │  │     m     Lowercase letter. Matches 'm'
# │  │     a     Lowercase letter. Matches 'a'
# │  │     i     Lowercase letter. Matches 'i'
# │  │     l     Lowercase letter. Matches 'l'
# │  │      |     Alternation (OR). Matches expression on either side of the '|'
# │  │     y     Lowercase letter. Matches 'y'
# │  │     a     Lowercase letter. Matches 'a'
# │  │     h     Lowercase letter. Matches 'h'
# │  │     o     Lowercase letter. Matches 'o'
# │  │     o     Lowercase letter. Matches 'o'
# │  │      |     Alternation (OR). Matches expression on either side of the '|'
# │  │     h     Lowercase letter. Matches 'h'
# │  │     o     Lowercase letter. Matches 'o'
# │  │     t     Lowercase letter. Matches 't'
# │  │     m     Lowercase letter. Matches 'm'
# │  │     a     Lowercase letter. Matches 'a'
# │  │     i     Lowercase letter. Matches 'i'
# │  │     l     Lowercase letter. Matches 'l'
# │  └─ )
# │
# │     .     Punctuation. Matches '.'
# │  ┌─ ( Group
# │  │     c     Lowercase letter. Matches 'c'
# │  │     o     Lowercase letter. Matches 'o'
# │  │     m     Lowercase letter. Matches 'm'
# │  │      |     Alternation (OR). Matches expression on either side of the '|'
# │  │     n     Lowercase letter. Matches 'n'
# │  │     e     Lowercase letter. Matches 'e'
# │  │     t     Lowercase letter. Matches 't'
# │  │      |     Alternation (OR). Matches expression on either side of the '|'
# │  │     o     Lowercase letter. Matches 'o'
# │  │     r     Lowercase letter. Matches 'r'
# │  │     g     Lowercase letter. Matches 'g'
# │  └─ )
# │
# └─
```
