#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# __init__.py

import logging
from pathlib import Path
import os, sys

# debug

# print('CHANGE THE TOOLKIT PACKAGE LOCATION !!')
# debug_path = '/home/thoverga/Documents/VLINDER_github/MetObs_toolkit'
# sys.path.insert(0, debug_path)
import metobs_toolkit


# Create the Logger
loggers = logging.getLogger(__name__)  # logger name is <vlinder-toolkit>
loggers.setLevel(logging.DEBUG)

log_path = os.path.join(str(Path(__file__).parent.parent.parent), "logfile.log")

# # Create the Handler for logging data to a file - will be hereted for children
logger_handler = logging.FileHandler(filename=log_path)
logger_handler.setLevel(logging.DEBUG)

# # Create a Formatter for formatting the log messages
logger_formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
logger_handler.setFormatter(logger_formatter)

# Add the Handler to the Logger
loggers.addHandler(logger_handler)
loggers.info("Logger initiated")


BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_PATH)


# import GUI


def launch_gui():
    from metobs_gui.main import main
    main()


# =============================================================================
# Version
# =============================================================================

# DO not change this manually!
__version__ = "0.0.1a0"

