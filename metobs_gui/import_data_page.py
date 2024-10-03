#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 31 16:26:11 2023

@author: thoverga
"""

from pathlib import Path
import copy
import ast
import os
import pytz
from PyQt5.QtWidgets import QFileDialog, QComboBox
from metobs_gui.errors import Error, Notification

from metobs_gui.path_handler import template_dir
from metobs_gui.data_func import isvalidfile

import metobs_gui.path_handler as path_handler
# from metobs_gui.template_func import get_all_templates
# from metobs_gui.json_save_func import get_saved_vals, update_json_file

import metobs_gui.tlk_scripts as tlk_scripts
import metobs_gui.log_displayer as log_displayer

from metobs_gui.extra_windows import MetadataDialog, DataDialog, DatasetTimeSeriesDialog

import metobs_toolkit
from metobs_toolkit import rootlog as toolkit_logger

# =============================================================================
# Initialise values
# =============================================================================
def init_import_page(MW):

    # MW.session['importing'] = {}
   

    # add all files in the cache to the selector spinner
    # ----- init spinners ------
    _setup_select_template_spinner(MW)
    _setup_select_dataset_pkl_spinner(MW)
    
    _setup_saved_paths(MW)
    
    # init the same data path links
    MW.data_file_T_2.setText(MW.data_file_T.text())
    MW.metadata_file_T_2.setText(MW.metadata_file_T.text())


# =============================================================================
# Reactions
# =============================================================================


def _react_use_data(MW):
    if MW.use_data_T_2.isChecked():
        MW.data_file_T_2.setEnabled(True)
        MW.Browse_data_B_2.setEnabled(True)
    else:
        MW.data_file_T_2.setEnabled(False)
        MW.Browse_data_B_2.setEnabled(False)

def _react_use_metadata(MW):
    if MW.use_metadata_2.isChecked():
        MW.metadata_file_T_2.setEnabled(True)
        MW.Browse_metadata_B_2.setEnabled(True)
    else:
        MW.metadata_file_T_2.setEnabled(False)
        MW.Browse_metadata_B_2.setEnabled(False)


def _react_use_specific_template(MW):
    if MW.use_specific_temp.isChecked():
        MW.specific_temp_path.setEnabled(True)
        MW.Browse_specific_temp.setEnabled(True)
        MW.select_temp.setEnabled(False)
    else:
        MW.specific_temp_path.setEnabled(False)
        MW.Browse_specific_temp.setEnabled(False)
        MW.select_temp.setEnabled(True)
    


def browsefiles_data(MW):
    fname=QFileDialog.getOpenFileName(MW, 'Select data file', str(Path.home()))
    MW.data_file_T_2.setText(fname[0]) #update text

def browsefiles_metadata(MW):
    fname=QFileDialog.getOpenFileName(MW, 'Select metadata file', str(Path.home()))
    MW.metadata_file_T_2.setText(fname[0]) #update text

def browsefiles_templatefile(MW):
    fname=QFileDialog.getOpenFileName(MW, 'Select template file', str(Path.home()))
    MW.specific_temp_path.setText(fname[0]) #update text

def browsefiles_pklfile(MW):
    fname=QFileDialog.getOpenFileName(MW, 'Select template file', str(Path.home()))
    MW.pkl_path.setText(fname[0]) #update text



def save_input_pkl_path(MW):
    if MW.use_pkl.isChecked():
        if MW.upload_ext_checkbox.isChecked():
            pkl_path = MW.pkl_path.text()
            savedict = {'input_pkl_file_path' : str(pkl_path)}
            path_handler.update_json_file(savedict, filepath=path_handler.saved_paths)

def _react_dataset_from_pkl(MW):
    
    from_pkl_widgets=[MW.pkl_selector, MW.upload_ext_checkbox, MW.pkl_path, MW.pkl_browser,
                      MW.pkl_path_save]
    
    from_template_widgets=[MW.select_temp, MW.use_specific_temp, MW.specific_temp_path, MW.Browse_specific_temp,
                           MW.data_file_T_2, MW.Browse_data_B_2, MW.use_data_T_2,
                           MW.metadata_file_T_2, MW.Browse_metadata_B_2, MW.use_metadata_2,
                           MW.freq_method_spinner, MW.freq_simpl_tol_spinner, MW.orig_simpl_tol_spinner,
                           MW.timestamp_tol_spinner, MW.data_read_kwargs, MW.metadata_read_kwargs]
    if MW.use_pkl.isChecked():
        for widg in from_pkl_widgets:
            widg.setEnabled(True)
        for widg in from_template_widgets:
            widg.setEnabled(False)
    else:
        for widg in from_pkl_widgets:
            widg.setEnabled(False)
        for widg in from_template_widgets:
            widg.setEnabled(True)
    
    _react_dataset_from_uploaded_pkl(MW)

def _react_dataset_from_uploaded_pkl(MW):
    if MW.upload_ext_checkbox.isChecked():
        MW.pkl_path.setEnabled(True)
        MW.pkl_browser.setEnabled(True)
        MW.pkl_path_save.setEnabled(True)
        
        MW.pkl_selector.setEnabled(False)
    else:
        MW.pkl_path.setEnabled(False)
        MW.pkl_browser.setEnabled(False)
        MW.pkl_path_save.setEnabled(False)        
        MW.pkl_selector.setEnabled(True)

def _react_save_dataset_as_pkl(MW):
    #construct target pkl filepath
    trg_file = MW.pkl_save_filename.text()
    if not trg_file.endswith('.pkl'):
        Error("The filename to save your Dataset to does not end with '.pkl'", f'{trg_file}')
        return
    filepath = os.path.join(path_handler.dataset_dir, trg_file)
    
    #Check if file already exists
    if path_handler.file_exist(filepath):
        Error(f'The file to save your Dataset to already exists: {filepath}')
        return
    
    #save the pickle
    _, succes, stout = tlk_scripts.gui_wrap(MW.Dataset.save_dataset,
                                                   {'outputfolder': path_handler.dataset_dir,
                                                    'filename': trg_file,
                                                    'overwrite': False})
    if not succes:
        Error('An error occured when saving the dataset to a pickle.', stout)
        return
    Notification(f'Your dataset is sucessfully saved as {trg_file}.')
    
    #update the input from pickle spinner
    _setup_select_dataset_pkl_spinner(MW)

# =============================================================================
# Open extra windows
# =============================================================================

def _react_get_info(MW):
    MW.prompt.clear()
    MW.prompt.insertPlainText('------ Get info ---------')
    
    _, succes, stout = tlk_scripts.gui_wrap(MW.Dataset.get_info, {})
    
    # print(stout)
    MW.prompt.insertPlainText(str(stout))
    if not succes:
        Error(f'.get_info() error on {MW.Dataset}. |n{stout}')

def _react_show_metadata(MW):
    MW._dlg = MetadataDialog(df=MW.Dataset.metadf) #launched when created

def _react_show_data(MW):
    
    returndf, succes, stout = tlk_scripts.gui_wrap(MW.Dataset.get_full_status_df, {})
   
    if succes:
        
        MW._dlg = DataDialog(df=returndf) #launched when created
    else:
        Error('Could not create a full status df.', stout)

def _react_plot_dataset(MW):
    MW._dlg = DatasetTimeSeriesDialog(dataset=MW.Dataset)

# =============================================================================
# Link widgets
# =============================================================================


# =============================================================================
# Triggers
# =============================================================================
def _setup_triggers(MW):
    
    MW.use_data_T_2.stateChanged.connect(lambda: _react_use_data(MW)) 
    MW.use_metadata_2.stateChanged.connect(lambda: _react_use_metadata(MW)) 
    MW.use_specific_temp.stateChanged.connect(lambda: _react_use_specific_template(MW))
    
    MW.use_pkl.stateChanged.connect(lambda: _react_dataset_from_pkl(MW))
    MW.upload_ext_checkbox.stateChanged.connect(lambda: _react_dataset_from_uploaded_pkl(MW))
    
    MW.Browse_data_B_2.clicked.connect(lambda: browsefiles_data(MW)) #browse datafile
    MW.Browse_metadata_B_2.clicked.connect(lambda: browsefiles_metadata(MW)) #browse metadatafile
    MW.Browse_specific_temp.clicked.connect(lambda: browsefiles_templatefile(MW)) #browse template
    MW.pkl_browser.clicked.connect(lambda: browsefiles_pklfile(MW)) #browse pkl file
    MW.pkl_path_save.stateChanged.connect(lambda: save_input_pkl_path(MW))


    MW.make_dataset.clicked.connect(lambda: make_dataset(MW))
    
    #buttons when dataset is loaded
    MW.get_info_T2.clicked.connect(lambda: _react_get_info(MW))
    MW.show_metadata_T2.clicked.connect(lambda: _react_show_metadata(MW))
    MW.show_dataset_T2.clicked.connect(lambda: _react_show_data(MW))
    MW.plot_dataset_T2.clicked.connect(lambda: _react_plot_dataset(MW))
  
    MW.save_pkl_B.clicked.connect(lambda: _react_save_dataset_as_pkl(MW))



def make_dataset(MW):
    
    if MW.use_pkl.isChecked():
        if MW.upload_ext_checkbox.isChecked():
            trg_pkl=MW.pkl_path.text()
        else:
            trg_pkl_file=MW.pkl_selector.currentText()
            trg_pkl=os.path.join(path_handler.dataset_dir, f'{trg_pkl_file}.pkl')
        
        #test if pkl exist
        if not path_handler.file_exist(trg_pkl):
            Error(f'The path to the pkl file does not exist: {trg_pkl}')
            return
        
        #import dataset from PKL
        import_the_dataset_from_pkl(MW, trg_pkl)       
        
    else:
        make_dataset_from_files(MW)


def import_the_dataset_from_pkl(MW, pklpath):
    #get parent directory
    parentdir = path_handler.get_parent_dir(pklpath)
    
    #get name of the file
    filename = path_handler.get_filename_from_path(pklpath)

    #import to the dataset 
    _return, succes, stout = tlk_scripts.gui_wrap(metobs_toolkit.import_dataset,
                                                  func_kwargs={
                                                      'folder_path': parentdir,
                                                      "filename": filename})
    if not succes:
        Error(f'Error when importint the Dataset from pkl ({filename}) in dir: {parentdir} ')
        return
    
    MW.Dataset=_return
    MW._Dataset_imported=True
    _setup_when_dataset_is_loaded(MW)
    Notification("Dataset imported!")
    
    
    



def make_dataset_from_files(MW):
    
    #get datafile
    if MW.use_data_T_2.isChecked():
        datafile=MW.data_file_T_2.text()
    else:
        datafile=None
    
    #get metadatafile
    if MW.use_metadata_2.isChecked():
        metadatafile=MW.metadata_file_T_2.text()
    else:
        metadatafile=None
    
    #get templatefile
    if MW.use_specific_temp.isChecked():
        #use specific template
        templatefile = MW.specific_temp_path.text()
    else:
        #use templated saved in cache
        temp_name = MW.select_temp.currentText()
        tempfile_dict = _list_saved_templates()
        templatefile = tempfile_dict[temp_name]
    
    #check paths
    for path in [datafile, metadatafile, templatefile]:
        if not path_handler.file_exist(path):
            Error(f'{path} is not a file!')
    
    #get arguments
    freq_method = MW.freq_method_spinner.currentText()
    
    freq_simpl_tol = f'{MW.freq_simpl_tol_spinner.value()}min'
    origin_simpl_tol = f'{MW.orig_simpl_tol_spinner.value()}min'
    timestamp_tol = f'{MW.timestamp_tol_spinner.value()}min'
    try:
        data_kwargs = ast.literal_eval(MW.data_read_kwargs.text())
    except SyntaxError as e:
        Error('Error in data_kwargs')
    
    try:
        metadata_kwargs = ast.literal_eval(MW.metadata_read_kwargs.text())
    except SyntaxError as e:
        Error('Error in metadata_kwargs')
        
    
    metadataonly_case = False
    if not MW.use_data_T_2.isChecked():
        metadataonly_case = True
    
    #Try creating a dataset
    MW._Dataset_imported=False
    
    dataset = metobs_toolkit.Dataset()
    if metadataonly_case:
        _return, succes, stout = tlk_scripts.gui_wrap(dataset.import_only_metadata_from_file,
                                                      {'input_metadata_file':metadatafile,
                                                       'template_file':templatefile,
                                                       'kwargs_metadata_read':metadata_kwargs,
                                                       'templatefile_is_url':False})
    else:
        _return, succes, stout = tlk_scripts.gui_wrap(dataset.import_data_from_file,
                                                      {'input_data_file':datafile,
                                                       'input_metadata_file':metadatafile,
                                                       'template_file':templatefile,
                                                       'freq_estimation_method':freq_method,
                                                       'freq_estimation_simplify_tolerance':freq_simpl_tol,
                                                       'origin_simplify_tolerance':origin_simpl_tol,
                                                       'timestamp_tolerance':timestamp_tol,
                                                       'kwargs_data_read':data_kwargs,
                                                       'kwargs_metadata_read':metadata_kwargs,
                                                       'templatefile_is_url':False})
    if succes:
        MW.Dataset=dataset
        MW._Dataset_imported=True
        _setup_when_dataset_is_loaded(MW)
        Notification("Dataset imported!")
    
    else:
        _setup_when_dataset_is_loaded(MW)
        Error(f'Cannot import the data into a Dataset.', stout)
        
   


# =============================================================================
# Setups
# =============================================================================
def _setup_when_dataset_is_loaded(MW):
    MW.update_all_obstype_spinners()
    if MW._Dataset_imported:
        MW.get_info_T2.setEnabled(True)
        MW.plot_dataset_T2.setEnabled(True)
        MW.show_dataset_T2.setEnabled(True)
        MW.show_metadata_T2.setEnabled(True)
        MW.save_pkl_B.setEnabled(True)
    else:
        MW.get_info_T2.setEnabled(False)
        MW.plot_dataset_T2.setEnabled(False)
        MW.show_dataset_T2.setEnabled(False)
        MW.show_metadata_T2.setEnabled(False)
        MW.save_pkl_B.setEnabled(False)
        
        
        
def _setup_select_template_spinner(MW):
    """ Set select template spinner values with tempalte names from Cache."""
    
    template_cache_dict = _list_saved_templates()
    MW.select_temp.clear()
    MW.select_temp.addItems(template_cache_dict.keys())
    

def _setup_select_dataset_pkl_spinner(MW):
    """ Set select dataset spinner with values from the Cache. """
    
    #get all files in the dataset dir
    files = os.listdir(path_handler.dataset_dir)
    files = [f for f in files if f.endswith('.pkl')]
    
    #Get rid of the extensions for displaying the name
    displaynames = [f[:-4] for f in files]
    
    #update spinner
    MW.pkl_selector.clear()
    MW.pkl_selector.addItems(displaynames)
    
def _setup_saved_paths(MW):
    #get saved path of target pickle 
    saved_paths = path_handler.read_json(path_handler.saved_paths)
    trg_path = saved_paths["input_pkl_file_path"]
    
    MW.pkl_path.setText(trg_path)



# =============================================================================
#  Helper
# =============================================================================

def _list_saved_templates():
    """List all names of template files stored in cache. """
    templ_names, templ_paths = path_handler.list_filenames(
                    folderpath=path_handler.template_dir)
    return dict(zip(templ_names, templ_paths))
    

def get_templatefile_by_name(name):
    """Returns template path given the name for templates stored in cache."""
    pass

