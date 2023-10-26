#!/usr/bin/env python3
"""Logging-related classes, functions and definitions."""
import os
import pprint
import sys
import time
from collections.abc import Sequence
from dataclasses import dataclass
from functools import wraps
from pathlib import Path

import humanize
from loguru import logger

from . import GeneralConstants


class LogDefaults:
    """Defaults used for the logging system."""

    LOGLEVEL_ENVVAR = f"{GeneralConstants.PACKAGE_NAME.upper()}_LOGLEVEL"
    LEVEL = os.environ.get(LOGLEVEL_ENVVAR, os.environ.get("LOGURU_LEVEL", "INFO"))
    DIRECTORY = Path().home() / ".logs" / GeneralConstants.PACKAGE_NAME
    RETENTION_TIME = "1 week"
    SINKS = {
        "console": sys.stderr,
        "logfile": DIRECTORY / f"{GeneralConstants.PACKAGE_NAME}_{{time}}.log",
    }


@dataclass
class LogFormatter:
    """Helper class to setup logging without poluting the module's main scope."""

    datetime: str = "<green>{time:YYYY-MM-DD HH:mm:ss}</green>"
    level: str = "<level>{level: <8}</level>"
    code_location: str = (
        "<cyan>@{name}</cyan>:<cyan>{function}</cyan> "
        + "<cyan><{file.path}</cyan>:<cyan>{line}>:</cyan>"
    )
    message: str = "<level>{message}</level>"

    def format_string(self, loglevel: str):
        """Return the appropriate fmt string according to log level and fmt opts."""
        rtn = f"{self.datetime} | {self.level} | "

        loglevel = logger.level(loglevel.upper())
        if loglevel.no < 20:  # noqa: PLR2004
            # More detail than just "INFO"
            rtn = f"{self.code_location}\n{rtn}"

        rtn += f"{self.message}"
        return rtn


class LoggerHandlers(Sequence):
    """Helper class to configure logger handlers when using `loguru.logger.configure`."""

    def __init__(self, default_level: str = LogDefaults.LEVEL, **sinks):
        """Initialise instance with default loglevel and sinks."""
        self.default_level = default_level.upper()
        self.handlers = {}
        for name, sink in {**LogDefaults.SINKS, **sinks}.items():
            self.add(name=name, sink=sink)

    def add(self, name, sink, **configs):
        """Add handler to instance."""
        configs["level"] = configs.pop("level", self.default_level).upper()
        configs["format"] = configs.pop(
            "format", LogFormatter().format_string(configs["level"])
        )

        try:
            configs["sink"] = Path(sink)
            configs["retention"] = configs.get("retention", LogDefaults.RETENTION_TIME)
        except TypeError:
            configs["sink"] = sink

        self.handlers[name] = configs

    def __repr__(self):
        return pprint.pformat(self.handlers)

    # Implement abstract methods
    def __getitem__(self, item):
        return tuple(self.handlers.values())[item]

    def __len__(self):
        return len(self.handlers)


def log_elapsed_time(**kwargs):
    """Return a decorator that logs beginning, exit and elapsed time of function."""

    def log_elapsed_time_decorator(function):
        """Wrap `function` and log beginning, exit and elapsed time."""
        name = kwargs.get("name", function.__name__)
        if function.__name__ == "main":
            name = f"{GeneralConstants.PACKAGE_NAME} v{GeneralConstants.VERSION}"
            cmd = f"{' '.join([GeneralConstants.PACKAGE_NAME, *sys.argv[1:]])}"
            name = f'{name} --> "{cmd}"'

        @wraps(function)
        def wrapper(*args, **kwargs):
            logger.opt(colors=True).info("<blue>Start {}</blue>", name)

            t_start = time.time()
            function_rtn = function(*args, **kwargs)
            elapsed = time.time() - t_start

            if elapsed < 60:  # noqa: PLR2004
                logger.opt(colors=True).info(
                    "<blue>Leaving {}. Total runtime: {:.2f}s.</blue>", name, elapsed
                )
            else:
                logger.opt(colors=True).info(
                    "<blue>Leaving {}. Total runtime: {}s (~{}).</blue>",
                    name,
                    elapsed,
                    humanize.precisedelta(elapsed),
                )

            return function_rtn

        return wrapper

    return log_elapsed_time_decorator


logger.configure(handlers=LoggerHandlers())
# Disable logger by defalt in case the project is used as a library. Leave it for the user
# to enable it if they so wish.
logger.disable(GeneralConstants.PACKAGE_NAME)
