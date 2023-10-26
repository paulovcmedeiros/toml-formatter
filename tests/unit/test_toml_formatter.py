#!/usr/bin/env python3
"""Tests for the toml formatting routines."""
import pytest

from toml_formatter.formatter import FormattedToml


@pytest.fixture()
def toml_file_as_string():
    return """


waldo   =   "bar"  #  This name should stay at the top, otherwise it will endup in a table

[    foobar . foo  ]
 C = 3
     A = 0    #    Indentation should become standardised, and spaces around comments too
F = 6
  # This comment should prevent the previous and following keys from being sorted together
  D = 4
        E = 5   # Multiple spaces between the keys should be trimmed to a single space
      B = 2

J = 10       # Spaces should also work as separators for sorting blocks, like comments
 foo   =     { bar  = [ "baz" ], version  = "^0.0.0"   } # Inline table should stay inline


H = 8
G =7
I = 9
a_long_inline_array_becomes_multiline = ["foo", {bar = "foo"}, 42, "qux", "baz", "A", "B", "C"]
a_long_multiline_array_remains_multiline = [
"foo",
    { bar   =   "foo"   },
        42  ,
        "qux", "baz",
      "foobar",
      "qux"
     ]
        a_short_multiline_array_becomes_inline = [
"foo",
    { bar   =   "foo"   },
        42  ,
        "qux", "baz",

     ]

# These comments are attached to the [qux.quux] table and
# should remain so when the order of the tables is altered.
[qux.quux]
 bar = [  "C"  ,  "Z",    "A"] # We won't sort values, as the order may be meaningful
 times. another_list =     ["2020-01-01T12:00:00Z"   ] # It seems tomlkit loses this comment
 times.  list."*.py"   =     ["2020-01-01T12:00:00Z"   ] # It seems tomlkit loses this comment

   # Now, this comment block should serve as a separator between different
   # section-sorting groups, i.e., sorting of table names should not mix
   # tables above and below this separator. Indentation of comment blocks is not altered.



[[AOT2]]
a=1
[[AOT1]]
b=2

multiline_value_2 = '''
[A.B.C]
all_inline_1  =      true   #    This line should not be formatted

'''

# The code should not confuse values with keys or tables.
multiline_value_1 = '''
[A.Z.C]
all_inline_2  =   false   #    This line should not be formatted

'''

"""


@pytest.fixture()
def expected_formatted_string():
    return """\
waldo = "bar" # This name should stay at the top, otherwise it will endup in a table

[foobar.foo]
  A = 0 # Indentation should become standardised, and spaces around comments too
  C = 3
  F = 6
  # This comment should prevent the previous and following keys from being sorted together
  B = 2
  D = 4
  E = 5 # Multiple spaces between the keys should be trimmed to a single space

  foo = {bar = ["baz"], version = "^0.0.0"} # Inline table should stay inline
  J = 10 # Spaces should also work as separators for sorting blocks, like comments

  a_long_inline_array_becomes_multiline = [
    "foo",
    {bar = "foo"},
    42,
    "qux",
    "baz",
    "A",
    "B",
    "C",
  ]
  a_long_multiline_array_remains_multiline = [
    "foo",
    {bar = "foo"},
    42,
    "qux",
    "baz",
    "foobar",
    "qux",
  ]
  a_short_multiline_array_becomes_inline = ["foo", {bar = "foo"}, 42, "qux", "baz"]
  G = 7
  H = 8
  I = 9

# These comments are attached to the [qux.quux] table and
# should remain so when the order of the tables is altered.
[qux.quux]
  bar = ["C", "Z", "A"] # We won't sort values, as the order may be meaningful
  times.another_list = ["2020-01-01T12:00:00Z"]
  times.list."*.py" = ["2020-01-01T12:00:00Z"]

   # Now, this comment block should serve as a separator between different
   # section-sorting groups, i.e., sorting of table names should not mix
   # tables above and below this separator. Indentation of comment blocks is not altered.

[[AOT1]]
  b = 2

  multiline_value_2 = '''
[A.B.C]
all_inline_1  =      true   #    This line should not be formatted

'''

  # The code should not confuse values with keys or tables.
  multiline_value_1 = '''
[A.Z.C]
all_inline_2  =   false   #    This line should not be formatted

'''

[[AOT2]]
  a = 1
\
"""


@pytest.fixture()
def formatted_toml_obj(toml_file_as_string):
    return FormattedToml.from_string(toml_file_as_string)


def test_toml_formatting_handles_expected_cases(
    formatted_toml_obj, expected_formatted_string
):
    assert str(formatted_toml_obj) == expected_formatted_string


def test_formatting_is_projection(expected_formatted_string):
    should_not_change = FormattedToml.from_string(expected_formatted_string)
    assert str(should_not_change) == expected_formatted_string
