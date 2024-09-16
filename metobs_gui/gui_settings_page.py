#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep  6 13:01:22 2023

@author: thoverga
"""

from pathlib import Path
import os

import metobs_gui.path_handler as path_handler




def setup_triggers(MW):
    MW.clear_saved.clicked.connect(lambda: clear_cached_toolkit_objects(MW))
    MW.clear_saved_paths.clicked.connect(lambda: clear_saved_paths(MW))

def clear_cached_toolkit_objects(MW):
    path_handler.clear_dir(path_handler.template_dir)
    path_handler.clear_dir(path_handler.dataset_dir)
    path_handler.clear_dir(path_handler.modeldata_dir)


    # update spinners pointing to these direcotries
    MW.select_temp.clear()
    MW.pkl_selector.clear()
    MW.select_pkl.clear()
    
    
    
def clear_saved_paths(MW):
    path_handler._clear_default_paths_file()
    

    # update spinners pointing to these direcotries
    #TODO: aanvullen
    MW.data_file_T.clear()
    MW.metadata_file_T.clear()