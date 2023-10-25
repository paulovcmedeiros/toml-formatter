#!/usr/bin/env python3
"""Code for a rudimentary TOML formatter, hopefully covering the most common use cases."""
import collections.abc
import contextlib
import csv
import itertools
import re
from functools import cached_property
from pathlib import Path
from typing import Sequence, Tuple, Union

import tomli
import tomlkit
from tomlkit.exceptions import UnexpectedCharError, UnexpectedEofError
from tomlkit.items import AoT, Comment, Item, Key, Table, Whitespace

from .config_parser import ParsedConfig

DEFAULT_CONFIG = ParsedConfig()


class BaseTomlContentsSequence(collections.abc.Sequence):
    """Basic functionality for the `Sequence`-type classes in the module."""

    @property
    def data(self) -> tuple:
        """Return data stored in the container. Parsing is performed upon assignment."""
        return getattr(self, "_data", ())

    @property
    def indentation(self) -> int:
        """Return the indentation applied for each scope level change."""
        return self._indentation

    @indentation.setter
    def indentation(self, new):
        self._indentation = new
        self.data = self.data  # Trigger data restructuring

    def __repr__(self):
        return "\n".join(str(entry) for entry in self)

    # Implement abstract methods
    def __getitem__(self, item):
        return self.data[item]

    def __len__(self):
        return len(self.data)


class ParsedTomlFileEntry:
    """A single, atomic parsed entry in a TOML file."""

    def __init__(self, single_entry_string: str):
        """Initialise instance."""
        self.toml_doc_obj = tomlkit.loads(single_entry_string)

    @property
    def toml_doc_obj(self):
        """Return the `tomlkit.TOMLDocument` obj underneath the instance."""
        return self._toml_doc_obj

    @toml_doc_obj.setter
    def toml_doc_obj(self, new):
        self._toml_doc_obj = new

        if isinstance(self.item, Whitespace):
            trivia = None
        else:
            trivia = self.item.trivia

        try:
            key, value = tomlkit.key_value(str(self))
        except tomlkit.exceptions.EmptyKeyError:
            self._defined_as_key_value = False
            if isinstance(self.item, (Table, AoT)):
                self._toml_doc_obj = tomlkit.loads(tomlkit.dumps(self.toml_doc_obj.value))
        else:
            self._defined_as_key_value = True
            self.toml_doc_obj.clear()
            if isinstance(value, tomlkit.items.InlineTable):
                new_table = tomlkit.inline_table()
                new_table.update(value.unwrap())
                value = new_table
            elif not isinstance(value, str):
                value = value.unwrap()

            stripped_key_components = [
                sub_k.strip()
                for sub_k in next(
                    csv.reader([key.as_string()], delimiter=".", skipinitialspace=True)
                )
            ]

            new_key = tomlkit.key(stripped_key_components)
            self.toml_doc_obj.append(new_key, value)

        if trivia is not None:
            self.item.trivia.__dict__ = trivia.__dict__

        self._fix_spaces_around_comments()

    @property
    def key(self) -> Key:
        """Return the `Key` associated with the atomic entry."""
        return self._tomlkit_doc_obj_body[-1][0]

    @property
    def defined_as_key_value(self):
        try:
            return self._defined_as_key_value
        except:
            return False

    @property
    def item(self) -> Item:
        """Return the `Item` associated with the atomic entry."""
        return self._tomlkit_doc_obj_body[-1][1]

    def indent(self, indent: int = 0):
        """Set the number of spaces for the indentation of the atomic entry."""
        self._indent_level = indent
        _indent_atomic_toml_entry(entry=self, indent=indent)

    @property
    def _tomlkit_doc_obj_body(self):
        return [
            (k, v)
            for k, v in self.toml_doc_obj.body
            if not isinstance(v, tomlkit.items.Null)
        ]

    def _fix_spaces_around_comments(self):
        if not isinstance(self.item, (Whitespace, Comment)):
            if self.item.trivia.comment:
                comment_text = self.item.trivia.comment.split("#", 1)[1].strip()
                if not comment_text.startswith("#"):
                    self.item.trivia.comment = f"# {comment_text}"
                    self.item.trivia.comment_ws = " "

    def __eq__(self, other):
        if isinstance(other, ParsedTomlFileEntry):
            return self.toml_doc_obj == other.toml_doc_obj
        return False

    def __repr__(self):
        str_repr = self.toml_doc_obj.as_string().rstrip()
        if isinstance(self.item, AoT) and self.defined_as_key_value:
            str_repr = _get_aot_repr(self.item, self.key)
            if len(str_repr) > 90:
                str_repr = _get_aot_repr(self.item, self.key, multiline=True)
        with contextlib.suppress(AttributeError):
            if str_repr.startswith((self._indent_level + 1) * " "):
                str_repr = self._indent_level * " " + str_repr.lstrip()
        return str_repr

    def __hash__(self):
        return hash(self.toml_doc_obj.as_string())


class TomlFileEntriesContainer(BaseTomlContentsSequence):
    """Container for parsed TOML file entries."""

    def __init__(self, data: Sequence[str]):
        """Initialise instance with `data` formatted as in a file's `readlines` method."""
        self.data = data

    @BaseTomlContentsSequence.data.setter
    def data(self, new: Sequence[str]):
        """Parse passed data and store validated TOML atomic entries."""
        atomic_entries = []
        previous_lines_failed_to_parse = []
        for line in new:
            str_to_parse = "".join([*previous_lines_failed_to_parse, line])
            try:
                new_entry = ParsedTomlFileEntry(str_to_parse)
            except (UnexpectedEofError, UnexpectedCharError):
                previous_lines_failed_to_parse.append(line)
            else:
                atomic_entries.append(new_entry)
                previous_lines_failed_to_parse = []

        self._data = tuple(atomic_entries)


class FormattedTomlFileSection(BaseTomlContentsSequence):
    """Class that holds and formats data for a single section of a TOML file."""

    def __init__(
        self, data: Sequence[str], formatting_options: ParsedConfig = DEFAULT_CONFIG
    ):
        """Initialise instance."""
        self.formatting_options = formatting_options
        self.data = data

    @BaseTomlContentsSequence.data.setter
    def data(self, new: Sequence[ParsedTomlFileEntry]) -> Tuple[ParsedTomlFileEntry]:
        """Set the data for the instance, applying formatting routines."""
        if new:
            new = _remove_consecutive_blanks(new)
            new = _adjust_empty_lines(new)
            new = _sort_keys(new)
        self._data = tuple(new)
        if not self.is_comment:
            self._normalise_indentation()

    @cached_property
    def name(self) -> str:
        """Return the name of the table."""
        for entry in self:
            if isinstance(entry.item, (Table, AoT)):
                return str(entry).strip().strip("[]")
        return ""

    @property
    def is_comment(self) -> bool:
        """Return True if the table only contains comments, and False otherwise."""
        for entry in self:
            if isinstance(entry.item, (Comment, Whitespace)):
                continue
            return False
        return True

    def _normalise_indentation(self):
        level_number = 0
        for entry in self:
            indent_int = level_number * self.formatting_options.indentation
            entry.indent(indent_int)
            if isinstance(entry.item, (Table, AoT)) and not entry.defined_as_key_value:
                level_number += 1


class FormattedToml:
    """Class to help format the contents of a TOML file."""

    def __init__(
        self, raw_data: Sequence[str], formatting_options: ParsedConfig = DEFAULT_CONFIG
    ):
        """Initialise, with `raw_data` being like the output of a file's `readlines`."""
        self.formatting_options = formatting_options
        self.sections = _split_data_in_sections(
            TomlFileEntriesContainer(data=raw_data),
            formatting_options=self.formatting_options,
        )

    @classmethod
    def from_file(cls, path: Union[Path, str], **kwargs):
        """Return a class instance with info read from file located at `path`."""
        with open(path, "r") as f:
            raw_data = f.readlines()
        return cls(raw_data=raw_data, **kwargs)

    @classmethod
    def from_string(cls, toml_string: str, **kwargs):
        """Return a class instance with info retrieved from `toml_string`."""
        raw_data = [f"{line}\n" for line in toml_string.split("\n")]
        return cls(raw_data=raw_data, **kwargs)

    @property
    def sections(self) -> Tuple[FormattedTomlFileSection]:
        """Return the sections present in the file."""
        return getattr(self, "_sections", ())

    @sections.setter
    def sections(self, new: Sequence[FormattedTomlFileSection]):
        for section in new:
            section.formatting_options = self.formatting_options
        self._sections = _get_sorted_sequence_of_sections(
            new, override_sorting=self.formatting_options.section_order_overrides
        )
        self.data = tomli.loads(str(self))

    @property
    def indentation(self) -> int:
        """Return the indentation applied for each scope level change."""
        return self.formatting_options.indentation

    @indentation.setter
    def indentation(self, new):
        """Set the indentation and update the sections accordingly."""
        self.formatting_options.indentation = new
        self.sections = self.sections

    def __repr__(self):
        return "\n".join(str(section) for section in self.sections)


def _indent_atomic_toml_entry(entry: ParsedTomlFileEntry, indent: int = 0):
    if isinstance(entry.item, Whitespace):
        return
    indent_str = indent * " "
    if isinstance(entry.item, (Table, AoT)) and entry.defined_as_key_value:
        # For whatever reason, tomlkit treats this as a special case
        entry.key._original = indent_str + entry.key._original.strip()
    else:
        entry.item.indent(indent)

    if isinstance(entry.item, tomlkit.items.Array):
        # Convert to multiline all inline arrays whose str len is > 90 characters
        is_multiline = any(
            isinstance(value, Whitespace) and value.value.strip(" ") == "\n"
            for value in itertools.chain.from_iterable(entry.item._value)
        )
        should_be_multiline = False
        if not is_multiline:
            str_repr = indent_str + str(entry)
            for line in str_repr.split("\n"):
                if len(line.rstrip()) > 90:
                    should_be_multiline = True
                    break

        # There is a bug in v0.12.1 of tomlkit that will cause a "has no attribute
        # is_bolean" to be raised if we use the item's own getitem here.
        values = [list.__getitem__(entry.item, i) for i in range(len(entry.item))]
        entry.item.clear()
        if is_multiline or should_be_multiline:
            # It seems that tomlkit doesn't keep comments in multi-line arrays.
            # we'll just reset the array to get the correct indentation. The
            # comments are kept for inline arrays though -- even after data reset.
            # TODO: Keep an eye in tomlkit updates to see if there is a
            #       better alternative to this.
            for value in values:
                entry.item.add_line(value.unwrap())
            entry.item.add_line(indent=indent_str)
        else:
            for ivalue, value in enumerate(values):
                entry.item.insert(ivalue, value.unwrap())


def _adjust_empty_lines(
    section: Sequence[ParsedTomlFileEntry],
) -> Tuple[ParsedTomlFileEntry]:
    """Add/rm empty lines so sections start with a non-empty and end with 1 empty line."""
    toml_newline = ParsedTomlFileEntry("\n")
    try:
        first_non_blank = next(
            ix for ix, x in enumerate(section) if not isinstance(x.item, Whitespace)
        )
        last_non_blank = next(
            ix
            for ix, x in reversed(list(enumerate(section)))
            if not isinstance(x.item, Whitespace)
        )
    except StopIteration:
        return (toml_newline,)

    return (*tuple(section[first_non_blank : last_non_blank + 1]), toml_newline)


def _remove_consecutive_blanks(
    entries: Sequence[ParsedTomlFileEntry],
) -> Tuple[ParsedTomlFileEntry]:
    new_entries = []
    for ientry, entry in enumerate(entries):
        if isinstance(entry.item, Whitespace):
            i_next = ientry + 1
            if i_next != len(entries) and isinstance(entries[i_next].item, Whitespace):
                continue
        new_entries.append(entry)
    return tuple(new_entries)


def _sort_keys(
    section_entries: Sequence[ParsedTomlFileEntry],
) -> Tuple[ParsedTomlFileEntry]:
    section_entries = list(section_entries)
    sorted_section_entries = []
    current_sorting_block = []
    for ientry, entry in enumerate(section_entries):
        if isinstance(entry.item, (Table, AoT)) and not entry.defined_as_key_value:
            sorted_section_entries.append(entry)
        elif (
            isinstance(entry.item, (Comment, Whitespace))
            or ientry == len(section_entries) - 1
        ):
            # Found blanks/spaces separating blocks, or the section ended. Let's flush.
            sorted_section_entries += sorted(
                current_sorting_block, key=lambda entry: entry.key.key.strip().lower()
            )
            sorted_section_entries.append(entry)
            current_sorting_block = []
        else:
            current_sorting_block.append(entry)

    return tuple(sorted_section_entries)


def _split_data_in_sections(
    entries: TomlFileEntriesContainer, formatting_options: ParsedConfig = DEFAULT_CONFIG
) -> Tuple[FormattedTomlFileSection]:
    sections = []
    new_section = []
    new_section_start = True
    for entry in entries:
        new_section_start = (
            isinstance(entry.item, (Table, AoT)) and not entry.defined_as_key_value
        )
        if new_section_start:
            # Find comments that should be attached to next section
            backwards_enumerate = reversed(list(enumerate(new_section)))
            i_last_valid = next(
                (ix for ix, x in backwards_enumerate if not isinstance(x.item, Comment)),
                -1,
            )
            comments_that_belong_to_next_section = new_section[i_last_valid + 1 :]
            new_section = new_section[: i_last_valid + 1]

            if new_section:
                sections.append(new_section)
            new_section = [*comments_that_belong_to_next_section, entry]
        else:
            new_section.append(entry)
    if not new_section_start:
        sections.append(new_section)

    rtn = []
    for section in sections:
        # Find eventual orphan comments and separate them from section
        i_last_valid = next(
            (
                ix
                for ix, x in reversed(list(enumerate(section)))
                if not isinstance(x.item, (Comment, Whitespace))
            ),
            -1,
        )

        actual_section = section[: i_last_valid + 1]
        dangling_comments = section[i_last_valid + 1 :]
        for sec in [actual_section, dangling_comments]:
            if all(isinstance(entry.item, Whitespace) for entry in sec):
                continue
            rtn.append(
                FormattedTomlFileSection(sec, formatting_options=formatting_options)
            )

    return tuple(rtn)


def _get_sorted_sequence_of_sections(
    sections: Sequence[FormattedTomlFileSection], override_sorting: Sequence[str] = ()
) -> Tuple[FormattedTomlFileSection]:
    sorting_blocks = []
    current_block = []

    # Put the overriden sections at the front manually
    manual_order_section_names = [""]
    for manual_order_section_name in override_sorting:
        regex = re.compile(manual_order_section_name)
        section_names_for_match = [
            s.name for s in sections if s.name not in manual_order_section_names
        ]
        matched_section_names = sorted(filter(regex.match, section_names_for_match))
        manual_order_section_names += matched_section_names

    manual_order_sections = []
    for section_name in manual_order_section_names:
        for section in sections:
            if section.is_comment:
                continue
            if section.name == section_name:
                manual_order_sections.append(section)
                break

    sections_to_enter_sorting = [s for s in sections if s not in manual_order_sections]
    for section in sections_to_enter_sorting:
        if section.is_comment:
            # This is a dangling comment section, marking the split between blocks
            sorting_blocks.append(current_block)
            sorting_blocks.append([section])
            current_block = []
        else:
            current_block.append(section)

    if current_block:
        sorting_blocks.append(current_block)

    for iblock, block in enumerate(sorting_blocks):
        sorting_blocks[iblock] = sorted(
            block, key=lambda section: section.name.strip().lower()
        )

    return tuple(
        manual_order_sections + [section for block in sorting_blocks for section in block]
    )


def _get_aot_repr(aot: AoT, key: tomlkit.items.Key, multiline: bool = False):
    """Return a formatted representation of an AoT."""
    indent = len(aot.trivia.indent)
    new_array = tomlkit.array().multiline(multiline).indent(indent)
    for table in aot:
        new_table = tomlkit.inline_table()
        new_table.update(table.unwrap())
        new_array.append(new_table)

    toml_doc_obj = tomlkit.toml_document.TOMLDocument()
    toml_doc_obj.append(key.as_string().strip(), new_array)
    str_repr = toml_doc_obj.as_string()
    if multiline:
        # Fix indentation of AoT items
        import io

        buf = io.StringIO(str_repr)
        lines = buf.read().splitlines()
        for iline in range(1, len(lines) - 1):
            lines[iline] = 2 * aot.trivia.indent + lines[iline].strip()
        str_repr = "\n".join(lines)

    str_repr += f"{aot.trivia.comment_ws}{aot.trivia.comment}"

    return str_repr.rstrip()
