[![GitHub](https://img.shields.io/badge/github-%23121011.svg?style=for-the-badge&logo=github&logoColor=white)](https://github.com/paulovcmedeiros/toml-formatter)
[![Github Pages](https://img.shields.io/badge/github%20pages-121013?style=for-the-badge&logo=github&logoColor=white)](https://paulovcmedeiros.github.io/toml-formatter-docs/)


[![Contributors Welcome](https://img.shields.io/badge/Contributors-welcome-<COLOR>.svg)](https://github.com/paulovcmedeiros/toml-formatter/pulls)
[![Linting](https://github.com/paulovcmedeiros/toml-formatter/actions/workflows/linting.yaml/badge.svg)](https://github.com/paulovcmedeiros/toml-formatter/actions/workflows/linting.yaml)
[![Tests](https://github.com/paulovcmedeiros/toml-formatter/actions/workflows/tests.yaml/badge.svg)](https://github.com/paulovcmedeiros/toml-formatter/actions/workflows/tests.yaml)
[![codecov](https://codecov.io/gh/paulovcmedeiros/toml-formatter/graph/badge.svg?token=XI8G1WH9O6)](https://codecov.io/gh/paulovcmedeiros/toml-formatter)

# TOML Formatter

An unpretentious formatter for TOML files written in Python.

See also the [online documentation](https://paulovcmedeiros.github.io/toml-formatter-docs).

## Configuration
To modify the default options for the package, add a `[tool.toml-formatter]` section in your project's `pyproject.toml` file. Alternatively, you can pass the `--config-file-path` option to select a different config file.  Please take a look at the [online documentation](https://paulovcmedeiros.github.io/toml-formatter-docs/toml_formatter.html#toml_formatter.formatter_options.FormatterOptions) for more information about the supported configuration options.

To see the configs in use, please run
```bash
toml-formatter configs
```

## Basic Usage
### CLI Usage
Upon succesfull installation, you should be able to run
```shell
toml-formatter [opts] SUBCOMMAND [subcommand_opts]
```
where `[opts]` and `[subcommand_opts]` denote optional command line arguments
that apply, respectively, to `toml-formatter` in general and to `SUBCOMMAND`
specifically.

**Please run `toml-formatter -h` for information** about the supported subcommands
and general `toml-formatter` options. For info about specific subcommands and the
options that apply to them only, **please run `toml-formatter SUBCOMMAND -h`** (note
that the `-h` goes after the subcommand in this case).

#### Check if file(s) are formatted
```bash
toml-formatter check path/to/toml/files/or/directory/containing/them
```
#### Fix the formatting
```bash
toml-formatter check --fix-inplace path/to/toml/files/or/directory/containing/them
```

### Use as Module
```python
from toml_formatter.formatter import FormattedToml
```

See the [API documentation](https://paulovcmedeiros.github.io/toml-formatter-docs/toml_formatter.html#toml_formatter.formatter.FormattedToml) for information about the `FormattedToml` class and how to configure the [formatter options](https://paulovcmedeiros.github.io/toml-formatter-docs/toml_formatter.html#toml_formatter.formatter_options.FormatterOptions) it uses.
