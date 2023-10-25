#!/usr/bin/env python3
"""Registration and validation of options passed in the config file."""
from functools import reduce
from typing import Literal

import tomli
from pydantic import BaseModel, NonNegativeInt, PositiveInt


class ParsedConfig(BaseModel):
    line_length: PositiveInt = 90
    indentation: NonNegativeInt = 2
    section_order_overrides: tuple[str, ...] = ()
    loglevel: Literal["INFO", "DEBUG", "WARNING", "ERROR", "CRITICAL"] = "INFO"

    @classmethod
    def from_toml_file(cls, path):
        with open(path, "rb") as config_file:
            try:
                configs = tomli.load(config_file)["tool"]["toml_formatter"]
            except KeyError:
                configs = {}
        return cls(**configs)

    def __getitem__(self, item):
        """Get items from container.

        The behaviour is similar to a `dict`, except for the fact that
        `self["A.B.C.D. ..."]` will behave like `self["A"]["B"]["C"]["D"][...]`.

        Args:
            item (str): Item to be retrieved. Use dot-separated keys to retrieve a nested
                item in one go.

        Raises:
            KeyError: If the item is not found.

        Returns:
            Any: Value of the item.
        """
        try:
            # Try regular getitem first in case "A.B. ... C" is actually a single key
            return getattr(self, item)
        except AttributeError:
            try:
                return reduce(getattr, item.split("."), self)
            except AttributeError as error:
                raise KeyError(item) from error
