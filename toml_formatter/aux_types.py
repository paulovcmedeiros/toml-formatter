#!/usr/bin/env python3
"""Aux types used in the package."""
import copy
import json
from collections.abc import Mapping
from functools import reduce
from operator import getitem
from typing import Any, Callable, Iterator, Literal, Optional, Union

import tomlkit
import yaml

from .general_utils import get_empty_nested_defaultdict, modify_mappings


class BaseMapping(Mapping):
    """Immutable mapping that will serve as basis for all config-related classes."""

    def __init__(self, *args, **kwargs) -> None:
        """Initialise an instance the same way a `dict` is initialised."""
        self.data = dict(*args, **kwargs)

    @property
    def data(self):
        """Return the underlying data stored by the instance."""
        return getattr(self, "_data", None)

    @data.setter
    def data(self, new, nested_maps_type=None):
        """Set the value of the `data` property."""
        if nested_maps_type is None:
            nested_maps_type = BaseMapping
        self._data = modify_mappings(
            obj=new,
            operator=lambda x: {
                k: nested_maps_type(v) if isinstance(v, Mapping) else v
                for k, v in x.items()
            },
        )

    def dict(self):  # noqa: A003 (class attr shadowing builtin)
        """Return a `dict` representation, converting also nested `Mapping`-type items."""
        return modify_mappings(obj=self, operator=dict)

    def copy(self, update: Optional[Union[Mapping, Callable[[Mapping], Any]]] = None):
        """Return a copy of the instance, optionally updated according to `update`."""
        new = copy.deepcopy(self)
        if update:
            new.data = modify_mappings(obj=self.dict(), operator=update)
        return new

    def dumps(
        self,
        section="",
        style: Literal["toml", "json", "yaml"] = "toml",
        toml_formatting_function: Optional[Callable] = None,
    ):
        """Get a nicely printed version of the container's contents."""
        if section:
            section_tree = section.split(".")
            mapping = get_empty_nested_defaultdict()
            reduce(getitem, section_tree[:-1], mapping)[section_tree[-1]] = self[section]
        else:
            mapping = self

        # Sorting keys, as a json object is an unordered set of name/value pairs, so we
        # can't guarantee a particular order.
        rtn = json.dumps(mapping, indent=2, sort_keys=True, default=dict)
        if style == "toml":
            if toml_formatting_function is None:
                rtn = tomlkit.dumps(json.loads(rtn))
            else:
                rtn = toml_formatting_function(tomlkit.dumps(json.loads(rtn)))
        elif style == "yaml":
            rtn = yaml.dump(json.loads(rtn))

        return rtn

    def __repr__(self):
        return f"{self.__class__.__name__}({self.dumps(style='json')})"

    # Implement the abstract methods __getitem__, __iter__ and __len__ from from Mapping
    def __getitem__(self, item):
        """Get items from container.

        The behaviour is similar to a `dict`, except for the fact that
        `self["A.B.C.D. ..."]` will behave like `self["A"]["B"]["C"]["D"][...]`.

        Args:
            item (str): Item to be retrieved. Use dot-separated keys to retrieve a nested
                item in one go.

        Returns:
            Any: Value of the item.
        """
        try:
            # Try regular getitem first in case "A.B. ... C" is actually a single key
            return getitem(self.data, item)
        except KeyError:
            return reduce(getitem, item.split("."), self.data)

    def __iter__(self) -> Iterator:
        return iter(self.data)

    def __len__(self) -> int:
        return len(self.data)
