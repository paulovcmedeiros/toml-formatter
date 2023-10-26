"""Configuration file for the Sphinx documentation builder."""
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import datetime
import sys
from pathlib import Path

sys.path.insert(0, Path("..").resolve().as_posix())

project = "TOML Formatter"
project_copyright = "2023, Paulo V C Medeiros"
author = "Paulo V C Medeiros <paulo.medeiros@smhi.se>"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinxcontrib.autodoc_pydantic",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
suppress_warnings = ["myst.xref_missing"]

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_last_updated_fmt = (
    datetime.datetime.now(datetime.timezone.utc)
    .isoformat(timespec="seconds")
    .replace("+00:00", "Z")
)
add_module_names = False
html_show_sourcelink = False

# See <https://sphinx-rtd-theme.readthedocs.io/en/stable/configuring.html>
html_theme_options = {"collapse_navigation": False}

# Further customisation
html_static_path = ["_static"]
html_css_files = ["css/custom.css"]
