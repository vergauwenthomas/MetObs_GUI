#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 30 14:05:22 2023

@author: thoverga
"""

import os
import json
import shutil
from pathlib import Path
from metobs_toolkit import demo_template



# =============================================================================
# Main folders
# =============================================================================

GUI_dir = str( Path(__file__).resolve().parents[0])

# TLK_dir = str( Path(__file__).resolve().parents[1])


# =============================================================================
# Derived locations
# =============================================================================

TMP_dir = os.path.join(GUI_dir, 'tmp') #to use in a single session
CACHE_dir = os.path.join(GUI_dir, 'cache') #to use over multiple sessions

# subfolders
template_dir = os.path.join(CACHE_dir, 'templates')
dataset_dir = os.path.join(CACHE_dir, 'datasets')
modeldata_dir = os.path.join(CACHE_dir, 'modeldata')

# files
cache_data_paths_file = os.path.join(CACHE_dir, 'saved_paths.json')


#Defaults for files


data_path_default = {"data_file_path": "",
                    "metadata_file_path": "",
                    "input_pkl_file_path": "",
                    "external_modeldata_path": ""}




# =============================================================================
# Helper functions
# =============================================================================

def make_dir(dir_path):
    if os.path.isdir(dir_path):
        return
    else:
        os.mkdir(dir_path)
        return


def file_exist(filepath):
    if os.path.isfile(filepath):
        return True
    elif os.path.islink(filepath):
        return True
    else:
        return False


def copy_file(filepath, targetpath):
    shutil.copyfile(filepath, targetpath)

def list_filenames(folderpath, fileextension=None):
    all_stuff = os.listdir(folderpath)
    all_files = [file for file in all_stuff if os.path.isfile(os.path.join(
                                                folderpath, file))]
    if fileextension is None:
        filenames = all_files
    else:
        filenames =[file for file in all_files if file.endswith(fileextension)]
    filepaths =[os.path.join(folderpath, file) for file in filenames]

    return filenames, filepaths


def clear_dir(directory):
    make_dir(directory)
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))


# =============================================================================
# Create the cache and tmp dir if they do not exist
# =============================================================================
def update_json_file(update_dict, filepath=cache_data_paths_file):

    # read the existing JSON data from the file or create an empty dict if it doesn't exist
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}

    # update or add to the JSON data using the update_dict
    for key, value in update_dict.items():
        data[key] = value

    # write the updated JSON data to the file
    with open(filepath, 'w') as f:
        json.dump(data, f, indent = 4)



def read_json(jsonfilename):
    with open(jsonfilename,'r') as file:
          # First we load existing data into a dict.
        file_data = json.load(file)

    return file_data




def _init_cache_dir():
    """ Update the cache dir with target subfolders and files if they do not exist."""
    
    #create folders if they do not exist yet
    _create_paths = [CACHE_dir, template_dir, dataset_dir, modeldata_dir]
    for _dir in _create_paths:
        make_dir(_dir)
        
    #create default (empty) data paths file
    if not file_exist(cache_data_paths_file):
        _clear_default_paths_file()


def _clear_default_paths_file():
    with open(cache_data_paths_file, 'w') as f:
        json.dump(data_path_default, f, indent = 4)
    

def _init_temp_dir():
    """ Create an empty teporary dirctory."""
    make_dir(TMP_dir)
    clear_dir(TMP_dir)

