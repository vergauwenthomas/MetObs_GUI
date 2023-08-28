#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 31 16:26:11 2023

@author: thoverga
"""

from pathlib import Path
import copy
import os
import pytz
from PyQt5.QtWidgets import QFileDialog, QComboBox
from metobs_gui.errors import Error, Notification

from metobs_gui.path_handler import template_dir
from metobs_gui.data_func import isvalidfile

import metobs_gui.path_handler as path_handler
from metobs_gui.template_func import get_all_templates
from metobs_gui.json_save_func import get_saved_vals, update_json_file

import metobs_gui.tlk_scripts as tlk_scripts
import metobs_gui.log_displayer as log_displayer

from metobs_gui.extra_windows import _show_metadf, _show_obsspace, _show_timeseries

from metobs_toolkit import loggers as toolkit_logger

# =============================================================================
# Initialise values
# =============================================================================
def init_import_page(MW):

    MW.session['importing'] = {}
    # MW.session['importing']['started'] = False

    # add all files in the cache to the selector spinner
    # ----- init spinners ------
    set_possible_templates(MW)
    set_possible_pickles(MW)
    # select template name from builder page if it is an item of the spinner
    buildname = MW.templatename.text()
    possible_templ = [MW.select_temp.itemText(i) for i in range(MW.select_temp.count())]
    if buildname in possible_templ:
        MW.select_temp.setCurrentText(buildname)

    # set freq method spinners
    freq_estim_methods = ['median', 'highest']
    MW.freq_est_method.addItems(freq_estim_methods)
    MW.freq_est_method.setCurrentText('median') #default

    MW.resample_method.addItems(['nearest', 'bfill'])
    MW.resample_method.setCurrentText('nearest') #default


    # init the same data path links
    MW.data_file_T_2.setText(MW.data_file_T.text())
    MW.metadata_file_T_2.setText(MW.metadata_file_T.text())

    # init pkl path if saved
    saved_vals = get_saved_vals()
    if 'input_pkl_file_path' in saved_vals:
        MW.pkl_path.setText(saved_vals['input_pkl_file_path'])

    # # Setup the logger handle to stream to the prompt
    # log_handler = log_displayer.QPlainTextEditLogger(MW.prompt)
    # toolkit_logger.addHandler(log_handler)




# =============================================================================
# Triggers
# =============================================================================
# ----- browse files -------#

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
        pkl_path = MW.pkl_path.text()
        savedict = {'input_pkl_file_path' : str(pkl_path)}
        update_json_file(savedict)



# =============================================================================
# Setups
# =============================================================================
#  Setups are functions to activate/deactivate widgets when one widget is triggered
#  It is handy to sort groups of widgets to use them in the stup functioncs

def _get_datapath_templ_widgets(MW):
    return[
           MW.Browse_data_B_2,
           MW.Browse_metadata_B_2,
           MW.data_file_T_2,
           MW.metadata_file_T_2,
           MW.use_metadata_2]

def _get_specific_templ_widgets(MW):
    return [MW.specific_temp_path,
            MW.Browse_specific_temp]

def _get_input_pkl_widgets(MW):
    return [MW.upload_ext_checkbox, MW.pkl_path, MW.pkl_browser, MW.pkl_path_save]

def _get_input_settings(MW):
    return [MW.gap_def_spinner, MW.freq_est_method,
            MW.freq_simpl,MW.freq_simpl_spinner,
            MW.data_kwargs, MW.metadata_kwargs,
            MW.sync_obs, MW.sync_obs_tol_spinner,
            MW.sync_obs_force, MW.sync_obs_force_spinner
            ]


def setup_use_input_pkl(MW):
    if MW.use_pkl.isChecked():
        boolval = False
    else:
        boolval=True
    MW.use_specific_temp.setChecked(False)
    MW.select_temp.setEnabled(False)
    for i in _get_datapath_templ_widgets(MW): i.setEnabled(boolval)
    for j in  _get_specific_templ_widgets(MW): j.setEnabled(boolval)
    for k in  _get_input_pkl_widgets(MW): k.setEnabled(not boolval)
    for p in _get_input_settings(MW): p.setEnabled(boolval)

    setup_default_template(MW)


def setup_use_specific_temp(MW):
    # when the use specific temp is triggered
    if MW.use_specific_temp.isChecked():
        boolval = False
    else:
        boolval = True
    MW.use_pkl.setChecked(False)
    MW.select_temp.setEnabled(False)
    for i in _get_datapath_templ_widgets(MW): i.setEnabled(not boolval)
    for j in  _get_specific_templ_widgets(MW): j.setEnabled(not boolval)
    for k in  _get_input_pkl_widgets(MW): k.setEnabled(boolval)
    for p in _get_input_settings(MW): p.setEnabled(not boolval)

    setup_default_template(MW)

def setup_default_template(MW):
    if (not MW.use_specific_temp.isChecked()) & (not MW.use_pkl.isChecked()) :
        MW.select_temp.setEnabled(True)
        for i in _get_datapath_templ_widgets(MW): i.setEnabled(True)
        for j in  _get_specific_templ_widgets(MW): j.setEnabled(False)
        for k in  _get_input_pkl_widgets(MW): k.setEnabled(False)
        for p in _get_input_settings(MW): p.setEnabled(True)

def setup_resample_timeres(MW):
    resample_widgets = [MW.resample_spinbox, MW.resample_method, MW.use_origin,
                        MW.origin_dt]
    if MW.resample.isChecked():
        for widg in resample_widgets: widg.setEnabled(True)
    else:
        for widg in resample_widgets: widg.setEnabled(False)
    setup_origin(MW)


def setup_freq_simplification(MW):
    if MW.freq_simpl.isChecked():
        boolval = True
    else:
        boolval=False
    MW.freq_simpl_spinner.setEnabled(boolval)

def setup_origin(MW):
    if MW.use_origin.isChecked():
        MW.origin_dt.setEnabled(True)
    else:
        MW.origin_dt.setEnabled(False)

def setup_syncronize(MW):
    if MW.sync_obs.isChecked():
        boolval = True
    else:
        boolval=False
    MW.sync_obs_tol_spinner.setEnabled(boolval)
    MW.sync_obs_force.setEnabled(boolval)
    MW.sync_obs_force_spinner.setEnabled(boolval)



def make_dataset(MW):

    # clear prompt
    MW.prompt.clear()

    # 3 options: using default template, using specific template, using pkl

    def _get_data_metadata_paths(MW):
        ok=True
        #get data and metadata path
        data_path = str(MW.data_file_T_2.text())
        if MW.use_metadata_2.isChecked():
            metadata_path = str(MW.metadata_file_T_2.text())
            isvalid, _msg = isvalidfile(metadata_path, filetype='.csv')
            if not isvalid:
                Error('Invalid file', _msg)
                ok = False
        else:
            metadata_path = None

        # check if they are valid
        isvalid, _msg = isvalidfile(data_path, filetype='.csv')
        if not isvalid:
            Error('Invalid file', _msg)
            ok = False
        return data_path, metadata_path, ok

    def _make_dataset_from_files(data_path, metadata_path, template_path,
                                 argdict, MW):
        # create dataset
        MW.prompt.appendPlainText('---- Import data from file ---- \n')

        dataset, isvalid, err_msg = tlk_scripts.import_dataset_from_file(
            data_path = data_path,
            metadata_path = metadata_path,
            template_path = template_path,
            freq_est_method = argdict['freq_est_method'],
            freq_est_simplyfy = argdict['freq_simpl_bool'],
            freq_est_simplyfy_toll = argdict['freq_simpl_tol'],
            kwargs_data = argdict['datafile_kwargs'],
            kwargs_metadata = argdict['metadatafile_kwargs'],
            gap_def = argdict['gap_def'],
            sync = argdict['sync_bool'],
            sync_tol = argdict['sync_tol'],
            sync_force = argdict['force_bool'],
            sync_force_freq = argdict['sync_force_freq']
            )
        if not isvalid:
            Error(err_msg[0], err_msg[1])
            return None, False

        MW.prompt.appendPlainText('\n---- Import data from file ---> Done! ---- \n')


        # coarsen if needed
        if argdict['resample_bool']:
            MW.prompt.appendPlainText('\n---- Coarsen time resolution ---- \n')
            dataset, isvalid, err_msg = tlk_scripts.coarsen_timeres(dataset = dataset,
                                                            target_freq = argdict['resample_freq'],
                                                            origin = argdict['resample_origin'],
                                                            method = argdict['resample_method'])
            if not isvalid:
                Error(err_msg[0], err_msg[1])
                return None, False

            MW.prompt.appendPlainText('\n---- Coarsen time resolution ---> Done! ---- \n')

        return dataset, True

    if (not MW.use_specific_temp.isChecked()) & (not MW.use_pkl.isChecked()):
        # A: using default template

        # get template path
        template_name = str(MW.select_temp.currentText())
        if not template_name.endswith('.csv'):
            filename = template_name + '.csv'
        else:
            filename = template_name
        template_path = os.path.join(template_dir, filename)
        data_path, metadata_path, isvalid = _get_data_metadata_paths(MW)
        if not isvalid:
            return
        # get arguments for importing
        argdict, _cont = extract_input_values_for_dataset(MW)
        if not _cont:
            return
        # make dataset
        dataset, _cont = _make_dataset_from_files(data_path, metadata_path, template_path,
                                     argdict, MW)
        if not _cont:
            return
        # store dataset as attribute
        MW.dataset = dataset

    elif (MW.use_specific_temp.isChecked()):
        # B: using specifig template
        # get template path
        template_path = str(MW.specific_temp_path.text())

        # test the file
        isvalid, _msg = isvalidfile(template_path, filetype='.csv')
        if not isvalid:
            Error('Invalid file', _msg)
            return

        data_path, metadata_path, isvalid = _get_data_metadata_paths(MW)
        if not isvalid:
            return

        # get arguments for importing
        argdict, _cont = extract_input_values_for_dataset(MW)
        if not _cont:
            return
        # make dataset
        dataset, _cont = _make_dataset_from_files(data_path, metadata_path, template_path,
                                     argdict, MW)
        if not _cont:
            return
        # store dataset as attribute
        MW.dataset = dataset

    else:
        # import from pkl
        pkl_filename, pkl_folder =  get_pkl_location(MW)
        print('hier')
        # get arguments for importing
        argdict, _cont = extract_input_values_for_dataset(MW)
        if not _cont:
            return
        MW.prompt.appendPlainText('---- Import data from pkl ---- \n')
        dataset, _cont, _msg = tlk_scripts.import_dataset_from_pkl(pkl_name=pkl_filename,
                                                                   pkl_folder=pkl_folder)
        if not _cont:
            Error(_msg[0], _msg[1])
            return

        MW.prompt.appendPlainText('\n---- Import data from pkl ---> Done! ---- \n')

        if argdict['resample_bool']:
            MW.prompt.appendPlainText('\n---- Coarsen time resolution ---- \n')
            dataset, _cont, _msg = tlk_scripts.coarsen_timeres(dataset = dataset,
                                                   target_freq = argdict['resample_freq'],
                                                   origin = argdict['resample_origin'],
                                                   method = argdict['resample_method'])
            if not _cont:
                Error(_msg[0], _msg[1])
                return
            MW.prompt.appendPlainText('\n---- Coarsen time resolution ---> Done! ---- \n')

        # store dataset as attribute
        MW.dataset = dataset



    # enable inspect buttons
    MW.get_info.setEnabled(True)
    MW.show_metadata.setEnabled(True)
    MW.show_dataset.setEnabled(True)
    MW.plot_dataset.setEnabled(True)
    MW.save_pkl_B.setEnabled(True)

    Notification('Dataset is created!')

def show_info(MW):
    # check if dataset exists
    if MW.dataset is None:
        Error('Dataset does not exist', 'No information can be shown because the dataset does not exist.')
        return

    # clear prompt
    MW.prompt.clear()
    MW.prompt.appendPlainText('\n---- Dataset information ---- \n')
    info = tlk_scripts.get_dataset_info(dataset = MW.dataset)
    for line in info:
        MW.prompt.appendPlainText(line)

def save_dataset(MW):
    # check if dataset is available
    if MW.dataset is None:
        Error('Save error', 'There is no dataset.')
        return

    pkl_name = str(MW.pkl_save_filename.text())
    if not pkl_name.endswith('.pkl'):
        pkl_name = pkl_name + '.pkl'

    # check if file already exists
    pkl_path = os.path.join(path_handler.dataset_dir, pkl_name)
    if path_handler.file_exist(pkl_path):
        Error('Save error', f'The file {pkl_path} already exist. Change the filename.')
        return

    # save dataset
    _, _cont, _msg = tlk_scripts.save_dataset_to_pkl(dataset=MW.dataset,
                                                     pkl_name=pkl_name,
                                                     pkl_folder=path_handler.dataset_dir)
    if not _cont:
        Error(_msg[0], _msg[1])
        return
    Notification(f'Dataset is sucesfully saved as a pkl ({pkl_path})')

    # update pkl spinner
    set_possible_pickles(MW)



# =============================================================================
# Open extra windows
# =============================================================================

def make_obsspace(MW):
    _show_obsspace(MW)

def show_metadf(MW):
    _show_metadf(MW)


def make_dataset_plot(MW):
   _show_timeseries(MW)









# =============================================================================
#  Helper
# =============================================================================
def get_pkl_location(MW):
    # either from the cache or form external:

    if ((MW.use_pkl.isChecked()) & (not MW.upload_ext_checkbox.isChecked())):
        # from external
        filename=str(MW.pkl_selector.currentText())
        folder=path_handler.dataset_dir

    elif ((MW.use_pkl.isChecked()) & (MW.upload_ext_checkbox.isChecked())):
        # from cache
        filepath = str(MW.pkl_path.text())
        # check if file exist
        if not path_handler.file_exist(filepath):
            Error('file not exist', f' The file {filepath} does not exist.')
            return
        folder = os.path.dirname(filepath)
        filename = filepath.replace(folder, '')[1:] #This hopefully works on windows
    else:
        Error('CODE 101')

    return filename, folder

def extract_input_values_for_dataset(MW):
    from datetime import datetime
    import json

    argdict = {}

    # resample arguments
    argdict['resample_bool'] = True if MW.resample.isChecked() else False
    argdict['resample_freq'] = str(int(MW.resample_spinbox.value())) + 'T'
    argdict['resample_method'] = str(MW.resample_method.currentText())
    if MW.use_origin.isChecked():
        origstr = str(MW.origin_dt.textFromDateTime(MW.origin_dt.dateTime()))
        origdt = datetime.strptime(origstr, '%d/%m/%Y %H:%M')
        argdict['resample_origin'] = origdt
    else:
        argdict['resample_origin'] = None

    # Gap arguments
    argdict['gap_def'] = int(MW.gap_def_spinner.value())

    # Specials:
    argdict['freq_est_method'] = str(MW.freq_est_method.currentText())
    argdict['freq_simpl_bool'] = True if MW.freq_simpl.isChecked() else False
    argdict['freq_simpl_tol'] = str(int(MW.freq_simpl_spinner.value())) + 'T'

    argdict['sync_bool'] = True if MW.sync_obs.isChecked() else False
    argdict['sync_tol'] = str(int(MW.sync_obs_tol_spinner.value())) + 'T'
    argdict['force_bool'] = True if MW.sync_obs_force.isChecked() else False
    argdict['sync_force_freq'] = int(MW.sync_obs_force_spinner.value()) #in minutes!

    # convert to dictionary
    datakwargstr = str(MW.data_kwargs.text()).replace("'", '"')
    metadatakwargstr = str(MW.metadata_kwargs.text()).replace("'", '"')

    try:
        argdict["datafile_kwargs"]  = json.loads(datakwargstr)
    except:
        Error('Datafile kwargs', f'{datakwargstr} could not be converted to a dictionary. Use this structure: "sep": ";", "engine":"python" (inside the brackets)')
        return {}, False
    try:
        argdict["metadatafile_kwargs"]  = json.loads(metadatakwargstr)
    except:
        Error('Metadatafile kwargs', f'{datakwargstr} could not be converted to a dictionary. Use this structure: "sep": ";", "engine":"python" (inside the brackets)')
        return {}, False

    argdict["datafile_kwargs"] = json.loads(str(MW.data_kwargs.text()).replace("'", '"')) #use double quotes
    argdict["metadatafile_kwargs"] = json.loads(str(MW.metadata_kwargs.text()).replace("'", '"'))



    return argdict, True

def set_possible_pickles(MW):
    pkl_names, pkl_paths = path_handler.list_filenames(folderpath=path_handler.dataset_dir, fileextension='.pkl')
    #update spinner
    MW.pkl_selector.clear()
    MW.pkl_selector.addItems(pkl_names)


def set_possible_templates(MW):
    templ_dict = get_all_templates()
    # remove .csv for presenting
    templ_names = [name.replace('.csv', '') for name in templ_dict.keys()]

    #update spinner
    MW.select_temp.clear()
    MW.select_temp.addItems(templ_names)

    # Store information to pass between triggers
    # self.template_dict = templ_dict #dict templname : templpath