#!/usr/bin/env python3
"""Wrappers for argparse functionality."""
import argparse
import sys
from pathlib import Path

from . import GeneralConstants
from .commands_functions import check_toml_files_format, show_configs


def get_parsed_args(program_name=GeneralConstants.PACKAGE_NAME, argv=None):
    """Get parsed command line arguments.

    Args:
        program_name (str): The name of the program.
        argv (list): A list of passed command line args.

    Returns:
        argparse.Namespace: Parsed command line arguments.

    """
    if argv is None:
        argv = sys.argv[1:]

    ######################################################################################
    # Command line args that will be common to main_parser and possibly other subparsers.#
    #                                                                                    #
    # You should add `parents=[common_parser]` to your subparser definition if you want  #
    # these options to apply there too.                                                  #
    ######################################################################################
    common_parser = argparse.ArgumentParser(add_help=False)

    common_parser.add_argument(
        "--config-file-path",
        default="pyproject.toml",
        type=Path,
        help="Path to the config file.",
    )

    ##########################################
    # Define main parser and general options #
    ##########################################
    main_parser = argparse.ArgumentParser(
        prog=program_name, formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    main_parser.add_argument(
        "--version",
        "-v",
        action="version",
        version="%(prog)s v" + GeneralConstants.VERSION,
    )

    # Configure the main parser to handle the commands
    subparsers = main_parser.add_subparsers(
        title="commands",
        required=True,
        dest="command",
        description=(
            f"Valid commands for {program_name} (note that commands also accept their "
            + "own arguments, in particular [-h]):"
        ),
        help="command description",
    )

    ###########################################
    # Configure parser for the "show" command #
    ###########################################
    parser_show_configs = subparsers.add_parser(
        "configs", help="Display adopted configs and exit.", parents=[common_parser]
    )
    parser_show_configs.add_argument(
        "section", help="The config section (optional)", default="", nargs="?"
    )
    parser_show_configs.set_defaults(run_command=show_configs)

    #############################################
    # Configure parser for the "check" command #
    ############################################
    parser_toml_formatter = subparsers.add_parser(
        "check",
        parents=[common_parser],
        help="Helper to format/standardise TOML files. "
        + "Return error code 1 if any file needs to be formatted.",
    )

    parser_toml_formatter.add_argument(
        "file_paths",
        help="Path(s) to the TOML files to be formatted. If a directory is passed, "
        + "then the code will descent recursively into it looking for TOML files.",
        type=lambda x: Path(x).expanduser().resolve(),
        nargs="+",
    )
    parser_toml_formatter.add_argument(
        "--show-formatted",
        help="Whether to show the formatted file contents for ill-formated files."
        + "If omitted, oly the diff will be shown.",
        action="store_true",
    )
    parser_toml_formatter.add_argument(
        "--fix-inplace",
        help="Modify the file(s) in-place to apply the suggested formatting.",
        action="store_true",
    )
    parser_toml_formatter.add_argument(
        "--include-hidden",
        help="Include hidden files in the recursive search.",
        action="store_true",
    )
    parser_toml_formatter.set_defaults(run_command=check_toml_files_format)

    return main_parser.parse_args(argv)
