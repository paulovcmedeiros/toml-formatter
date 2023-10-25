#!/usr/bin/env python3
"""Package to run the Destination Earth on Demand Extremes system."""
from importlib.metadata import version
from pathlib import Path


class GeneralConstants:
    """General package-related constants."""

    PACKAGE_NAME = __name__
    VERSION = version(__name__)
    PACKAGE_DIRECTORY = Path(__file__).parent
