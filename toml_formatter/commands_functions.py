#!/usr/bin/env python3
"""Implement the package's commands."""
import difflib
import itertools
import sys

import tomli_w

from toml_formatter import GeneralConstants

from .logs import logger
from .toml_formatter import FormattedToml


def show_configs(args, config):  # noqa: ARG001
    """Implement the 'show_config' command.

    Args:
        args (argparse.Namespace): Parsed command line arguments.
        config (.config_parser.ParsedConfig): Parsed config file contents.

    """
    logger.info("Printing requested configs...")
    formatted_toml = FormattedToml.from_string(
        toml_string=tomli_w.dumps(config.model_dump()), formatting_options=config
    )
    sys.stdout.write(str(formatted_toml) + "\n")


def check_toml_files_format(args, config):  # noqa: PLR0912
    """Implement the `check` command."""

    def _exclude_if_hidden(fpath):
        if args.include_hidden:
            return False
        return any(part.startswith(".") for part in fpath.parts)

    file_iterators = []
    for path in args.file_paths:
        if path.is_dir():
            file_iterators.append(
                fpath
                for fpath in path.rglob("*")
                if fpath.suffix.lower() == ".toml" and not _exclude_if_hidden(fpath)
            )
        else:
            file_iterators.append([path])

    n_files = 0
    files_in_need_of_formatting = []
    for fpath in itertools.chain.from_iterable(file_iterators):
        n_files += 1

        formatted_toml = FormattedToml.from_file(path=fpath, formatting_options=config)
        actual_toml = fpath.read_text()

        file_needs_formatting = False
        for diff_line in difflib.unified_diff(
            actual_toml.split("\n"),
            str(formatted_toml).split("\n"),
            fromfile="Original",
            tofile="Formatted",
            lineterm="",
        ):
            file_needs_formatting = True
            logger.warning(diff_line)

        if file_needs_formatting:
            if not args.fix_inplace:
                logger.error("File <{}> needs formatting, see diff above.", fpath)
            files_in_need_of_formatting.append(fpath)

            if args.show_formatted:
                logger.info("The formatted version will now be printed to the stdout.")
                sys.stdout.write(str(formatted_toml) + "\n")

            if args.fix_inplace:
                logger.debug("Fixing format of file <{}> in-place.", fpath)
                with open(fpath, "w") as f:
                    f.write(str(formatted_toml))

        else:
            logger.debug("File <{}> seems to be well-formatted.", fpath)

    if files_in_need_of_formatting:
        if args.fix_inplace:
            logger.info("TOML formatter: {} (out of {}) file(s) formatted:")
            for fpath in files_in_need_of_formatting:
                logger.info("    {}", fpath)
        else:
            logger.error(
                "TOML formatter: {} (out of {}) file(s) seem to need formatting:",
                len(files_in_need_of_formatting),
                n_files,
            )
            for fpath in files_in_need_of_formatting:
                logger.error("    {}", fpath)
            logger.info(
                "HINT: You may run `{} --fix-inplace SOME/PATH` to have "
                + 'all TOML files located at "SOME/PATH" formatted automatically.',
                GeneralConstants.PACKAGE_NAME.replace("_", "-"),
            )
            raise SystemExit(1)
