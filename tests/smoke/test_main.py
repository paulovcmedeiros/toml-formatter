#!/usr/bin/env python3
"""Smoke tests."""
import itertools
import shutil
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from unittest import mock

import pytest
import tomli
import tomli_w

from toml_formatter import GeneralConstants
from toml_formatter.__main__ import main


def test_package_executable_is_in_path():
    assert shutil.which(GeneralConstants.PACKAGE_NAME.replace("_", "-"))


@pytest.mark.parametrize("argv", [[], None])
def test_cannot_run_without_arguments(argv):
    with redirect_stderr(StringIO()):
        with pytest.raises(SystemExit, match="2"):
            main(argv)


class TestMainShowCommands:
    def test_show_config_command(self):
        with redirect_stdout(StringIO()):
            main(["configs"])

    def test_show_config_command_stretched_time(self):
        """Test again, mocking time.time so the total elapsed time is greater than 60s."""

        def fake_time():
            for new in itertools.count():
                yield 100 * new

        with mock.patch("time.time", mock.MagicMock(side_effect=fake_time())):
            with redirect_stdout(StringIO()):
                main(["configs"])


def test_toml_formatter_command(tmp_path_factory):
    dummy_toml = tomli.loads(
        """
        [foo]
        bar = "baz"
        """
    )
    toml_file = tmp_path_factory.mktemp("toml_fmt_tests") / "tmp.toml"
    with open(toml_file, "w") as f:
        f.write(tomli_w.dumps(dummy_toml))

    with pytest.raises(SystemExit):
        main(["check", "--include-hidden", toml_file.parent.as_posix()])

    main(["check", toml_file.as_posix(), "--fix-inplace", "--show-formatted"])

    with redirect_stdout(StringIO()):
        main(["check", GeneralConstants.PACKAGE_DIRECTORY.parent.as_posix()])
