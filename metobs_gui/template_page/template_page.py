#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 28 13:30:48 2023

@author: thoverga
"""
from pathlib import Path
import os

import json

from PyQt5.QtWidgets import QFileDialog, QComboBox, QDialog
from PyQt5.uic import loadUi

from metobs_toolkit.template import _get_empty_templ_dict
from metobs_gui.tlk_scripts import gui_wrap, get_function_defaults

import metobs_gui.common_functions as common_func
import metobs_gui.template_page.template_mapping as template_mapping

# import metobs_gui.template_func as template_func
import metobs_gui.path_handler as path_handler

from metobs_gui.errors import Error, Notification


# =============================================================================
# Initialise values
# =============================================================================
def init_page(MW):

    # set data paths to saved files
    set_datapaths_init(MW)

    # init a template json file
    _init_an_empty_template(MW)
   
   

def _init_an_empty_template(MW):
    #Add a the template to the MW as dict    
    MW._templ_dict= _get_empty_templ_dict() 
    MW._template_json_file=os.path.join(path_handler.TMP_dir, 'template.json')

    #create an empty templatejson file
    with open(MW._template_json_file, 'w') as f:
        json.dump(MW._templ_dict, f, indent=4)
   
    #Display the template dict
    common_func.display_jsonfile_in_plaintext(
        plaintext=MW.template_info,
        jsonfile=MW._template_json_file)
    # _display_templ_dict(MW)



def _update_templdict_to_json(MW):
    """Write the current template to a json file"""

    path_handler.update_json_file(update_dict=MW._templ_dict,
                                  filepath=MW._template_json_file)




# =============================================================================
# Reactions
# =============================================================================

def _react_use_data_change(MW):
    if MW.use_data_box.isChecked():
        MW.start_mapping_B.setEnabled(True)
    else:
        MW.start_mapping_B.setEnabled(False)
    
def _react_use_metadata_change(MW):
    if MW.use_metadata_box.isChecked():
        MW.start_mapping_metadata.setEnabled(True)
    else:
        MW.start_mapping_metadata.setEnabled(False)


def _react_to_save_template(MW):
    
    filename = MW.templatename.text()
    
    if not filename.endswith('.json'):
        filename += '.json'
    trg_path = os.path.join(path_handler.template_dir, filename)
    
    if path_handler.file_exist(trg_path):
        Error(f'The path {trg_path} already exists. The template could not be saved.')
        return
    
    #copy the templatefile from tmp to cache
    path_handler.copy_file(MW._template_json_file,
                           trg_path)
    
    Notification(f'The template is saved as {filename}')
    
    
    


# =============================================================================
# Triggers
# =============================================================================

def setup_triggers(MW):
    MW.Browse_data_B.clicked.connect(lambda: browsefiles_data(MW)) #browse datafile
    MW.Browse_metadata_B.clicked.connect(lambda: browsefiles_metadata(MW)) #browse metadatafile
    # save paths when selected
    MW.save_data_path.clicked.connect(lambda: save_path(
                                                            MW=MW,
                                                            savebool=MW.save_data_path.isChecked(),
                                                            savekey='data_file_path',
                                                            saveval=MW.data_file_T.text()))
    MW.save_metadata_path.clicked.connect(lambda: save_path(
                                                            MW=MW,
                                                            savebool=MW.save_metadata_path.isChecked(),
                                                            savekey='metadata_file_path',
                                                            saveval=MW.metadata_file_T.text()))

    # MW.browse_format.currentTextChanged.connect(lambda: enable_format_widgets(MW))

    MW.start_mapping_B.clicked.connect(lambda: launch_data_mapping(MW))
    MW.start_mapping_metadata.clicked.connect(lambda: launch_metadata_mapping(MW))
    
    MW.use_data_box.stateChanged.connect(lambda: _react_use_data_change(MW)) 
    MW.use_metadata_box.stateChanged.connect(lambda: _react_use_metadata_change(MW))
    
    # initiate the start mapping module
    # MW.start_mapping_B.clicked.connect(lambda: prepare_for_mapping(MW))

    # # construnct the mappindict
    MW.build_B.clicked.connect(lambda: build_template(MW))

    # # save template
    MW.save_template.clicked.connect(lambda:_react_to_save_template(MW))

    # # display df's
    MW.preview_data.clicked.connect(lambda: show_data_head(MW))
    MW.preview_metadata.clicked.connect(lambda: show_metadata_head(MW))
   




def set_datapaths_init(MW):
    """
    Read saved values to look for a path for the data and metadata file.

    """
    saved_vals = path_handler.read_json(path_handler.saved_paths)

   
    MW.data_file_T.setText(str(saved_vals['data_file_path']))
    MW.metadata_file_T.setText(str(saved_vals['metadata_file_path']))
       



# =============================================================================
# Launch dialogs
# =============================================================================

def launch_data_mapping(MW):
    """ launch a dialog for mapping the data. """
    dlg = template_mapping.Data_map_Window(
        datafile=MW.data_file_T.text(),
        Dataset = MW.Dataset) #launched when created
    
    if dlg.exec():
        #when pushed the "ok" button
    
        #scrape the info of the closing window
        dlg._read_users_settings_as_template() #get the latest data from dialog
        #capture signals
        templatedict = dlg.template_dict
        
        #subset only to data part (needed when updating)
        datatemplatedict={"data_related": templatedict["data_related"],
                          "single_station_name": templatedict["single_station_name"]}
        
        #update the template dict attribute
        
        MW._templ_dict.update(datatemplatedict)
        _update_templdict_to_json(MW)
        
    else: 
        #When closed or clicked on cancel
        print ('Dialog closed, no mapping is saved.')
    
    #print current templatedict status
    common_func.display_jsonfile_in_plaintext(
                    plaintext=MW.template_info,
                    jsonfile=MW._template_json_file)
        
        
def launch_metadata_mapping(MW):
    """ launch a dialog for mapping the metadata. """
    dlg = template_mapping.Metadata_map_Window(
        metadatafile=MW.metadata_file_T.text()) #launched when created
    
    if dlg.exec():
        #when pushed the "ok" button
        pass
    
        #scrape the info of the closing window
        dlg._read_users_settings_as_template() #get the latest data from dialog
        #capture singlas
        templatedict = dlg.template_dict
        #subset only to metadata part (needed when updating)
        metadatatemplatedict={"metadata_related": templatedict["metadata_related"]}
        
        #update the template dict attribute
        MW._templ_dict.update(metadatatemplatedict)
        _update_templdict_to_json(MW)
       
    else: 
        #When closed or clicked on cancel
        print ('Dialog closed, no mapping is saved.')
    
    #print current templatedict status
    common_func.display_jsonfile_in_plaintext(
                    plaintext=MW.template_info,
                    jsonfile=MW._template_json_file)
                


# =============================================================================
# Toolkit functions
# =============================================================================

def build_template(MW):
    """ Try to build a metobstoolkit.template form the current json file. """
    #get files
    datafile = MW.data_file_T.text()
    metadatafile = MW.metadata_file_T.text()
    templatefile = MW._template_json_file

    #convert to none if needed    
    if (datafile == '') | (not MW.use_data_box.isChecked()):
        datafile=None
        
    if (metadatafile == '') | (not MW.use_metadata_box.isChecked()):
        metadatafile=None
    
    #get default args
    import_kwargs = get_function_defaults(MW.Dataset.import_data_from_file)
    #update the paths
    import_kwargs.update({'input_data_file':datafile,
                     'input_metadata_file':metadatafile,
                     'template_file':templatefile})
    
    
    _ret, succes, msg = gui_wrap(
        func=MW.Dataset.import_data_from_file,
        func_kwargs= import_kwargs,
        )
    if not succes:
        Error('Could not import a Dataset', str(msg))
        
    else:
        Notification(f'Succesfully tested the template: {MW.Dataset.template}')
        MW.save_template.setEnabled(True)
        
        
        
    
    
    
    
    
    



# =============================================================================
# Triggers
# =============================================================================
# ----- browse files -------#

def browsefiles_data(MW):
    fname=QFileDialog.getOpenFileName(MW, 'Select data file', str(Path.home()))
    MW.data_file_T.setText(fname[0]) #update text

def browsefiles_metadata(MW):
    fname=QFileDialog.getOpenFileName(MW, 'Select metadata file', str(Path.home()))
    MW.metadata_file_T.setText(fname[0]) #update text

# ----- save paths --------
def save_path(MW, savebool, savekey, saveval):
    if savebool:
        savedict = {str(savekey): str(saveval)}
        path_handler.update_json_file(savedict, filepath=path_handler.saved_paths)

# ----- enable specific format settings --------




def show_data_head(MW):
    # 1. THe data file
    try:
        df_head = common_func.read_csv_file(
            filepath=MW.data_file_T.text(),
            nrows=20,
        )
    except Exception as e:
        Error(str(e))
    
    # Display
    MW.templmodel.setDataFrame(df_head)

def show_metadata_head(MW):
    try:
        metadf_head = common_func.read_csv_file(
            filepath=MW.metadata_file_T.text(),
            nrows=20,
        )
       
    except Exception as e:
        Error(str(e))
 
    # Display
    MW.templmodel.setDataFrame(metadf_head)

