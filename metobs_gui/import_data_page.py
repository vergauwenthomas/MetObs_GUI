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

    MW.session['importing'] = {}
    # MW.session['importing']['started'] = False

    # add all files in the cache to the selector spinner
    # ----- init spinners ------
    _setup_select_template_spinner(MW)
    _setup_select_dataset_pkl_spinner(MW)
   
    
    _setup_saved_paths(MW)
    

    # init the same data path links
    MW.data_file_T_2.setText(MW.data_file_T.text())
    MW.metadata_file_T_2.setText(MW.metadata_file_T.text())

    # init pkl path if saved
    # saved_vals = path_handler.read_json(path_handler.saved_paths)
    # if 'input_pkl_file_path' in saved_vals:
        # MW.pkl_path.setText(saved_vals['input_pkl_file_path'])

    # # Setup the logger handle to stream to the prompt
    # log_handler = log_displayer.QPlainTextEditLogger(MW.prompt)
    # toolkit_logger.addHandler(log_handler)


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





# def _get_datapath_templ_widgets(MW):
#     return[
#            MW.Browse_data_B_2,
#            MW.Browse_metadata_B_2,
#            MW.data_file_T_2,
#            MW.metadata_file_T_2,
#            MW.use_metadata_2]

# def _get_specific_templ_widgets(MW):
#     return [MW.specific_temp_path,
#             MW.Browse_specific_temp]

# def _get_input_pkl_widgets(MW):
#     return [MW.upload_ext_checkbox, MW.pkl_path, MW.pkl_browser, MW.pkl_path_save]

# def _get_input_settings(MW):
#     return [MW.gap_def_spinner, MW.freq_est_method,
#             MW.freq_simpl,MW.freq_simpl_spinner,
#             MW.data_kwargs, MW.metadata_kwargs,
#             MW.sync_obs, MW.sync_obs_tol_spinner,
#             MW.sync_obs_force, MW.sync_obs_force_spinner
#             ]


# def setup_use_input_pkl(MW):
#     if MW.use_pkl.isChecked():
#         boolval = False
#     else:
#         boolval=True
#     MW.use_specific_temp.setChecked(False)
#     MW.select_temp.setEnabled(False)
#     for i in _get_datapath_templ_widgets(MW): i.setEnabled(boolval)
#     for j in  _get_specific_templ_widgets(MW): j.setEnabled(boolval)
#     for k in  _get_input_pkl_widgets(MW): k.setEnabled(not boolval)
#     for p in _get_input_settings(MW): p.setEnabled(boolval)

#     setup_default_template(MW)


# def setup_use_specific_temp(MW):
#     # when the use specific temp is triggered
#     if MW.use_specific_temp.isChecked():
#         boolval = False
#     else:
#         boolval = True
#     MW.use_pkl.setChecked(False)
#     MW.select_temp.setEnabled(False)
#     for i in _get_datapath_templ_widgets(MW): i.setEnabled(not boolval)
#     for j in  _get_specific_templ_widgets(MW): j.setEnabled(not boolval)
#     for k in  _get_input_pkl_widgets(MW): k.setEnabled(boolval)
#     for p in _get_input_settings(MW): p.setEnabled(not boolval)

#     setup_default_template(MW)

# def setup_default_template(MW):
#     if (not MW.use_specific_temp.isChecked()) & (not MW.use_pkl.isChecked()) :
#         MW.select_temp.setEnabled(True)
#         for i in _get_datapath_templ_widgets(MW): i.setEnabled(True)
#         for j in  _get_specific_templ_widgets(MW): j.setEnabled(False)
#         for k in  _get_input_pkl_widgets(MW): k.setEnabled(False)
#         for p in _get_input_settings(MW): p.setEnabled(True)

# def setup_resample_timeres(MW):
#     resample_widgets = [MW.resample_spinbox, MW.resample_method, MW.use_origin,
#                         MW.origin_dt]
#     if MW.resample.isChecked():
#         for widg in resample_widgets: widg.setEnabled(True)
#     else:
#         for widg in resample_widgets: widg.setEnabled(False)
#     setup_origin(MW)


# def setup_freq_simplification(MW):
#     if MW.freq_simpl.isChecked():
#         boolval = True
#     else:
#         boolval=False
#     MW.freq_simpl_spinner.setEnabled(boolval)

# def setup_origin(MW):
#     if MW.use_origin.isChecked():
#         MW.origin_dt.setEnabled(True)
#     else:
#         MW.origin_dt.setEnabled(False)

# def setup_syncronize(MW):
#     if MW.sync_obs.isChecked():
#         boolval = True
#     else:
#         boolval=False
#     MW.sync_obs_tol_spinner.setEnabled(boolval)
#     MW.sync_obs_force.setEnabled(boolval)
#     MW.sync_obs_force_spinner.setEnabled(boolval)



# def make_dataset(MW):

#     # clear prompt
#     MW.prompt.clear()

#     # 3 options: using default template, using specific template, using pkl

#     def _get_data_metadata_paths(MW):
#         ok=True
#         #get data and metadata path
#         data_path = str(MW.data_file_T_2.text())
#         if MW.use_metadata_2.isChecked():
#             metadata_path = str(MW.metadata_file_T_2.text())
#             isvalid, _msg = isvalidfile(metadata_path, filetype='.csv')
#             if not isvalid:
#                 Error('Invalid file', _msg)
#                 ok = False
#         else:
#             metadata_path = None

#         # check if they are valid
#         isvalid, _msg = isvalidfile(data_path, filetype='.csv')
#         if not isvalid:
#             Error('Invalid file', _msg)
#             ok = False
#         return data_path, metadata_path, ok

#     def _make_dataset_from_files(data_path, metadata_path, template_path,
#                                  argdict, MW):
#         # create dataset
#         MW.prompt.appendPlainText('---- Import data from file ---- \n')

#         dataset, isvalid, err_msg = tlk_scripts.import_dataset_from_file(
#             data_path = data_path,
#             metadata_path = metadata_path,
#             template_path = template_path,
#             freq_est_method = argdict['freq_est_method'],
#             freq_est_simplyfy = argdict['freq_simpl_bool'],
#             freq_est_simplyfy_toll = argdict['freq_simpl_tol'],
#             kwargs_data = argdict['datafile_kwargs'],
#             kwargs_metadata = argdict['metadatafile_kwargs'],
#             gap_def = argdict['gap_def'],
#             sync = argdict['sync_bool'],
#             sync_tol = argdict['sync_tol'],
#             sync_force = argdict['force_bool'],
#             sync_force_freq = argdict['sync_force_freq']
#             )
#         if not isvalid:
#             Error(err_msg[0], err_msg[1])
#             return None, False

#         MW.prompt.appendPlainText('\n---- Import data from file ---> Done! ---- \n')


#         # coarsen if needed
#         if argdict['resample_bool']:
#             MW.prompt.appendPlainText('\n---- Coarsen time resolution ---- \n')
#             dataset, isvalid, err_msg = tlk_scripts.coarsen_timeres(dataset = dataset,
#                                                             target_freq = argdict['resample_freq'],
#                                                             origin = argdict['resample_origin'],
#                                                             method = argdict['resample_method'])
#             if not isvalid:
#                 Error(err_msg[0], err_msg[1])
#                 return None, False

#             MW.prompt.appendPlainText('\n---- Coarsen time resolution ---> Done! ---- \n')

#         return dataset, True

#     if (not MW.use_specific_temp.isChecked()) & (not MW.use_pkl.isChecked()):
#         # A: using default template

#         # get template path
#         template_name = str(MW.select_temp.currentText())
#         if not template_name.endswith('.csv'):
#             filename = template_name + '.csv'
#         else:
#             filename = template_name
#         template_path = os.path.join(template_dir, filename)
#         data_path, metadata_path, isvalid = _get_data_metadata_paths(MW)
#         if not isvalid:
#             return
#         # get arguments for importing
#         argdict, _cont = extract_input_values_for_dataset(MW)
#         if not _cont:
#             return
#         # make dataset
#         dataset, _cont = _make_dataset_from_files(data_path, metadata_path, template_path,
#                                      argdict, MW)
#         if not _cont:
#             return
#         # store dataset as attribute
#         MW.dataset = dataset

#     elif (MW.use_specific_temp.isChecked()):
#         # B: using specifig template
#         # get template path
#         template_path = str(MW.specific_temp_path.text())

#         # test the file
#         isvalid, _msg = isvalidfile(template_path, filetype='.csv')
#         if not isvalid:
#             Error('Invalid file', _msg)
#             return

#         data_path, metadata_path, isvalid = _get_data_metadata_paths(MW)
#         if not isvalid:
#             return

#         # get arguments for importing
#         argdict, _cont = extract_input_values_for_dataset(MW)
#         if not _cont:
#             return
#         # make dataset
#         dataset, _cont = _make_dataset_from_files(data_path, metadata_path, template_path,
#                                      argdict, MW)
#         if not _cont:
#             return
#         # store dataset as attribute
#         MW.dataset = dataset

#     else:
#         # import from pkl
#         pkl_filename, pkl_folder =  get_pkl_location(MW)
#         print('hier')
#         # get arguments for importing
#         argdict, _cont = extract_input_values_for_dataset(MW)
#         if not _cont:
#             return
#         MW.prompt.appendPlainText('---- Import data from pkl ---- \n')
#         dataset, _cont, _msg = tlk_scripts.import_dataset_from_pkl(pkl_name=pkl_filename,
#                                                                    pkl_folder=pkl_folder)
#         if not _cont:
#             Error(_msg[0], _msg[1])
#             return

#         MW.prompt.appendPlainText('\n---- Import data from pkl ---> Done! ---- \n')

#         if argdict['resample_bool']:
#             MW.prompt.appendPlainText('\n---- Coarsen time resolution ---- \n')
#             dataset, _cont, _msg = tlk_scripts.coarsen_timeres(dataset = dataset,
#                                                    target_freq = argdict['resample_freq'],
#                                                    origin = argdict['resample_origin'],
#                                                    method = argdict['resample_method'])
#             if not _cont:
#                 Error(_msg[0], _msg[1])
#                 return
#             MW.prompt.appendPlainText('\n---- Coarsen time resolution ---> Done! ---- \n')

#         # store dataset as attribute
#         MW.dataset = dataset



#     # enable inspect buttons
#     MW.get_info.setEnabled(True)
#     MW.show_metadata.setEnabled(True)
#     MW.show_dataset.setEnabled(True)
#     MW.plot_dataset.setEnabled(True)
#     MW.save_pkl_B.setEnabled(True)

#     Notification('Dataset is created!')

# def show_info(MW):
#     # check if dataset exists
#     if MW.dataset is None:
#         Error('Dataset does not exist', 'No information can be shown because the dataset does not exist.')
#         return

#     # clear prompt
#     MW.prompt.clear()
#     MW.prompt.appendPlainText('\n---- Dataset information ---- \n')
#     info = tlk_scripts.get_dataset_info(dataset = MW.dataset)
#     for line in info:
#         MW.prompt.appendPlainText(line)

# def save_dataset(MW):
#     # check if dataset is available
#     if MW.dataset is None:
#         Error('Save error', 'There is no dataset.')
#         return

#     pkl_name = str(MW.pkl_save_filename.text())
#     if not pkl_name.endswith('.pkl'):
#         pkl_name = pkl_name + '.pkl'

#     # check if file already exists
#     pkl_path = os.path.join(path_handler.dataset_dir, pkl_name)
#     if path_handler.file_exist(pkl_path):
#         Error('Save error', f'The file {pkl_path} already exist. Change the filename.')
#         return

#     # save dataset
#     _, _cont, _msg = tlk_scripts.save_dataset_to_pkl(dataset=MW.dataset,
#                                                      pkl_name=pkl_name,
#                                                      pkl_folder=path_handler.dataset_dir)
#     if not _cont:
#         Error(_msg[0], _msg[1])
#         return
#     Notification(f'Dataset is sucesfully saved as a pkl ({pkl_path})')

#     # update pkl spinner
#     set_possible_pickles(MW)








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

# def get_pkl_location(MW):
#     # either from the cache or form external:

#     if ((MW.use_pkl.isChecked()) & (not MW.upload_ext_checkbox.isChecked())):
#         # from external
#         filename=str(MW.pkl_selector.currentText())
#         folder=path_handler.dataset_dir

#     elif ((MW.use_pkl.isChecked()) & (MW.upload_ext_checkbox.isChecked())):
#         # from cache
#         filepath = str(MW.pkl_path.text())
#         # check if file exist
#         if not path_handler.file_exist(filepath):
#             Error('file not exist', f' The file {filepath} does not exist.')
#             return
#         folder = os.path.dirname(filepath)
#         filename = filepath.replace(folder, '')[1:] #This hopefully works on windows
#     else:
#         Error('CODE 101')

#     return filename, folder

# def extract_input_values_for_dataset(MW):
#     from datetime import datetime
#     import json

#     argdict = {}

#     # resample arguments
#     argdict['resample_bool'] = True if MW.resample.isChecked() else False
#     argdict['resample_freq'] = str(int(MW.resample_spinbox.value())) + 'T'
#     argdict['resample_method'] = str(MW.resample_method.currentText())
#     if MW.use_origin.isChecked():
#         origstr = str(MW.origin_dt.textFromDateTime(MW.origin_dt.dateTime()))
#         origdt = datetime.strptime(origstr, '%d/%m/%Y %H:%M')
#         argdict['resample_origin'] = origdt
#     else:
#         argdict['resample_origin'] = None

#     # Gap arguments
#     argdict['gap_def'] = int(MW.gap_def_spinner.value())

#     # Specials:
#     argdict['freq_est_method'] = str(MW.freq_est_method.currentText())
#     argdict['freq_simpl_bool'] = True if MW.freq_simpl.isChecked() else False
#     argdict['freq_simpl_tol'] = str(int(MW.freq_simpl_spinner.value())) + 'T'

#     argdict['sync_bool'] = True if MW.sync_obs.isChecked() else False
#     argdict['sync_tol'] = str(int(MW.sync_obs_tol_spinner.value())) + 'T'
#     argdict['force_bool'] = True if MW.sync_obs_force.isChecked() else False
#     argdict['sync_force_freq'] = int(MW.sync_obs_force_spinner.value()) #in minutes!

#     # convert to dictionary
#     datakwargstr = str(MW.data_kwargs.text()).replace("'", '"')
#     metadatakwargstr = str(MW.metadata_kwargs.text()).replace("'", '"')

#     try:
#         argdict["datafile_kwargs"]  = json.loads(datakwargstr)
#     except:
#         Error('Datafile kwargs', f'{datakwargstr} could not be converted to a dictionary. Use this structure: "sep": ";", "engine":"python" (inside the brackets)')
#         return {}, False
#     try:
#         argdict["metadatafile_kwargs"]  = json.loads(metadatakwargstr)
#     except:
#         Error('Metadatafile kwargs', f'{datakwargstr} could not be converted to a dictionary. Use this structure: "sep": ";", "engine":"python" (inside the brackets)')
#         return {}, False

#     argdict["datafile_kwargs"] = json.loads(str(MW.data_kwargs.text()).replace("'", '"')) #use double quotes
#     argdict["metadatafile_kwargs"] = json.loads(str(MW.metadata_kwargs.text()).replace("'", '"'))



#     return argdict, True

# def set_possible_pickles(MW):
#     pkl_names, pkl_paths = path_handler.list_filenames(folderpath=path_handler.dataset_dir, fileextension='.pkl')
#     #update spinner
#     MW.pkl_selector.clear()
#     MW.pkl_selector.addItems(pkl_names)


# def set_possible_templates(MW):
#     templ_dict = get_all_templates()
#     # remove .csv for presenting
#     templ_names = [name.replace('.csv', '') for name in templ_dict.keys()]

#     #update spinner
#     MW.select_temp.clear()
#     MW.select_temp.addItems(templ_names)

#     # Store information to pass between triggers
#     # self.template_dict = templ_dict #dict templname : templpath