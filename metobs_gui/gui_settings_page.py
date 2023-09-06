#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep  6 13:01:22 2023

@author: thoverga
"""

from pathlib import Path
import os

import metobs_gui.path_handler as path_handler




def clear_cache(MW):
    path_handler.clear_dir(path_handler.template_dir)
    path_handler.clear_dir(path_handler.dataset_dir)
    path_handler.clear_dir(path_handler.modeldata_dir)


    # update spinners pointing to these direcotries
    MW.select_temp.clear()
    MW.pkl_selector.clear()
    MW.select_pkl.clear()