#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# __init__.py

import logging
from pathlib import Path
import os
import sys

import metobs_toolkit


# Create the Logger
loggers = logging.getLogger(__name__)
loggers.setLevel(logging.DEBUG)
loggers.info("Logger initiated")


BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_PATH)


# DO not change this manually!
__version__ = "0.5.0a0"

from metobs_gui.main import main
main()


# =============================================================================
# Version
# =============================================================================



