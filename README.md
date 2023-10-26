[![GitHub](https://img.shields.io/badge/github-%23121011.svg?style=for-the-badge&logo=github&logoColor=white)](https://github.com/paulovcmedeiros/toml-formatter)
[![Github Pages](https://img.shields.io/badge/github%20pages-121013?style=for-the-badge&logo=github&logoColor=white)](https://paulovcmedeiros.github.io/toml-formatter-docs/)


[![Contributors Welcome](https://img.shields.io/badge/Contributors-welcome-<COLOR>.svg)](https://shields.io/)
![Linting](https://github.com/paulovcmedeiros/toml-formatter/actions/workflows/linting.yaml/badge.svg)
![Tests](https://github.com/paulovcmedeiros/toml-formatter/actions/workflows/tests.yaml/badge.svg)
[![codecov](https://codecov.io/gh/paulovcmedeiros/toml-formatter/graph/badge.svg?token=XI8G1WH9O6)](https://codecov.io/gh/paulovcmedeiros/toml-formatter)

# TOML Formatter

An unpretentious formatter for TOML files written in Python.

See also the [online documentation](https://paulovcmedeiros.github.io/toml-formatter-docs).

## Configuration
To modify the default options for the package, add a `[tool.toml-formatter]` section in your project's `pyproject.toml` file. Please take a look at the [online documentation](https://paulovcmedeiros.github.io/toml-formatter-docs/toml_formatter.html#toml_formatter.formatter_options.FormatterOptions) for more information about the supported configuration options.

To see the configs in use, please run
```bash
toml-formatter configs
```

## Basic Usage
### CLI Usage
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
