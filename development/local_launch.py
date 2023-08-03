#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 28 13:11:09 2023

@author: thoverga
"""


import os
import sys
from pathlib import Path
import pandas as pd
import time
import math


lib_folder = Path(__file__).resolve().parents[1]

toolkit_folder =os.path.join(str(lib_folder.parents[0]), 'MetObs_toolkit')

sys.path.insert(0,str(toolkit_folder))
sys.path.insert(0,str(lib_folder))




import metobs_toolkit


#%%

import metobs_gui

metobs_gui.launch_gui()