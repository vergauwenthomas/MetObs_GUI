#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug  8 12:19:32 2023

@author: thoverga
"""


import os
import copy
from pathlib import Path
from datetime import datetime
from PyQt5.QtWidgets import QFileDialog
# from metobs_gui.extra_windows import _show_metadf, _show_spatial_html

from metobs_gui.json_save_func import get_saved_vals
import metobs_gui.tlk_scripts as tlk_scripts
import metobs_gui.path_handler as path_handler
from metobs_gui.errors import Error, Notification
from metobs_gui.extra_windows import _show_modeldata,  _show_modeldata_dataframe

from metobs_gui.metadata_page import _coordinates_available
# =============================================================================
# init page
# =============================================================================


def init_modeldata_page(MW):


    # modeldata init
    MW.model_method.addItems(['from pkl (GUI)', 'from external pkl', 'from GEE'])
    MW.model_method.setCurrentText('from GEE')
    gee_modelnames = list(_get_all_possible_gee_dataset().keys())
    MW.gee_modelname.addItems(gee_modelnames)

    MW.model_obstype.addItems(['temp'])

    # init pkl files in cache
    pkl_cache_files, _ = path_handler.list_filenames(path_handler.modeldata_dir)
    MW.select_pkl.addItems(pkl_cache_files)

    # init saved external path
    set_datapaths_init(MW)


    # setup model settings
    setup_model_settings(MW)
    setup_model_dt(MW)
    setup_obstype_spinner(MW)



def set_datapaths_init(MW):
    """
    Read saved values to look for a path for the data and metadata file.

    """
    saved_vals = get_saved_vals()

    # set datafile path
    if 'external_modeldata_path' in saved_vals:
        MW.external_path.setText(str(saved_vals['external_modeldata_path']))

# =============================================================================
# Setup
# =============================================================================
def setup_model_settings(MW):
    groups = _widget_grouper(MW)
    if str(MW.model_method.currentText()) == 'from pkl (GUI)':
        from_pkl=True
        from_ext = False
        from_gee = False
    elif str(MW.model_method.currentText()) == 'from external pkl':
        from_pkl=False
        from_ext = True
        from_gee = False
    elif str(MW.model_method.currentText()) == 'from GEE':
        from_pkl=False
        from_ext = False
        from_gee = True
        # enable dt if box is checked

    else:
        Error('GUI error -> contact developers', f'{MW.model_method.currentText()} unknown trigger.')
        return

    for widg in groups['from_pkl']:widg.setEnabled(from_pkl)
    for widg in groups['from_external']:widg.setEnabled(from_ext)
    for widg in groups['from_gee']:widg.setEnabled(from_gee)
    for widg in groups['save_modeldata_pkl']:widg.setEnabled(from_gee)


def setup_model_dt(MW):
    if MW.use_startdt.isChecked(): #startdt is linkt with enddt
        MW.gee_startdt.setEnabled(True)
        MW.gee_enddt.setEnabled(True)

    else:
        MW.gee_startdt.setEnabled(False)
        MW.gee_enddt.setEnabled(False)

def setup_obstype_spinner(MW):
    if str(MW.model_method.currentText()) == 'from GEE':
        avail_gee_datasets = _get_all_possible_gee_dataset()
        modelname=str(MW.gee_modelname.currentText())
        if not modelname in avail_gee_datasets.keys():
            Error('modelname not found', f'The modelname: {modelname} is not found in the list of known GEE (dynamical) datasets.')
            return
        mapped_obstypes = list(avail_gee_datasets[modelname]['band_of_use'].keys())

        MW.model_obstype.clear()
        MW.model_obstype.addItems(mapped_obstypes)


def setup_convertor_widgets(MW):
    # init values
    MW.obstype_convertor.clear()
    MW.obstype_convertor.addItems(list(MW.modeldata.df.columns))


    groups = _widget_grouper(MW)
    for widg in groups['convertor']:widg.setEnabled(True)

    get_tlk_unit(MW)
    setup_conv_expression(MW)

def setup_conv_expression(MW):
    if MW.use_expression.isChecked():
        MW.conv_expression.setEnabled(True)
    else:
        MW.conv_expression.setEnabled(False)


# =============================================================================
# triggers
# =============================================================================

def get_tlk_unit(MW):
    obstype = MW.obstype_convertor.currentText()
    # get current units
    try:
        current_units = MW.modeldata._df_units[obstype]
    except KeyError:
        current_units = 'UNKNOWN'


    try:
        # get default tlk units:
        from metobs_toolkit.convertors import standard_tlk_units
        tlk_unit = standard_tlk_units[obstype]
    except KeyError:
        tlk_unit = 'UNKNOWN'


    # update lable
    MW.convert_to.setText(f'Convert {current_units.upper()} to {tlk_unit.upper()}')


def convert_units(MW):
    if MW.modeldata is None:
        Error('No Modeldata', 'There is no model loaded.')
        return
    if MW.modeldata.df.empty:
        Error('Empty Modeldata', 'The modeldata is empty.')
        return

    obstype = str(MW.obstype_convertor.currentText())
    from metobs_toolkit.convertors import standard_tlk_units
    target_unit_name = standard_tlk_units[obstype]

    if MW.use_expression.isChecked():
        expression = str(MW.conv_expression.text())
    else:
        expression = None

    MW.prompt_modeldata.appendPlainText(f'\n---- Converting modeldata units ---- \n')


    modeldata, _cont, terminal, _msg = tlk_scripts.conv_modeldata_units(
                                        modeldata = MW.modeldata,
                                        obstype=obstype,
                                        target_unit=target_unit_name,
                                        expression=expression)
    if not _cont:
        Error(_msg[0], _msg[1])
        return

    for line in terminal:
        MW.prompt_modeldata.appendPlainText(line)

    MW.prompt_modeldata.appendPlainText(f'\n----  Importing modeldata from pkl file ---> Done! ---- \n')
    MW.modeldata = modeldata
    Notification('The {obstype} units are converted to {target_unit_name}')
    get_tlk_unit(MW)


def import_modeldata(MW):


    if str(MW.model_method.currentText()) == 'from pkl (GUI)':
        pkl_folder = path_handler.modeldata_dir
        file = str(MW.select_pkl.currentText())
        from_pkl=True

    elif str(MW.model_method.currentText()) == 'from external pkl':
        filepath = str(MW.external_path.text())
        # get dir name
        pkl_folder = os.path.dirname(filepath)
        # get filename
        file = filepath.replace(pkl_folder, '')[1:]
        from_pkl=True

    elif str(MW.model_method.currentText()) == 'from GEE':
        # two options: either the file is already imported in the .modeldata_temporar, or import from csv file
        if MW.modeldata_temporar is None:
            csv_path = str(MW.drive_path.text())
            from_pkl=False
        else:
            MW.prompt_modeldata.appendPlainText(f'\n----  Loading modeldata ---- \n')
            MW.modeldata = copy.copy(MW.modeldata_temporar)
            MW.prompt_modeldata.appendPlainText(f'\n----  Loading modeldata ---> Done! ---- \n')
            Notification('The Modeldata is succesfully imported!')
            return
    else:
        Error('ERROR 102')
        return

    # import from pkl files
    if from_pkl:
        # 1. check if file exist
        fullpath = os.path.join(pkl_folder, file)
        if not path_handler.file_exist(fullpath):
            Error('file does not exist', f' The modeldata pkl file ({fullpath}) does not exist.')
            return

        MW.prompt_modeldata.appendPlainText(f'\n----  Importing modeldata from pkl {fullpath} file ---- \n')

        # import the pkl
        modeldata, _cont, terminal, _msg = tlk_scripts.import_modeldata(folder=pkl_folder,
                                                                        pkl_file=file)
        if not _cont:
            Error(_msg[0], _msg[1])
            return

        for line in terminal:
            MW.prompt_modeldata.appendPlainText(line)
        print('just imported modeldata: ', modeldata)
        MW.prompt_modeldata.appendPlainText(f'\n----  Importing modeldata from pkl file ---> Done! ---- \n')
    else:
        # from csv
        # check if file exist
        if not path_handler.file_exist(csv_path):
            Error('file does not exist', f' The modeldata csv file ({csv_path}) does not exist.')
            return

        MW.prompt_modeldata.appendPlainText(f'\n----  Importing modeldata from csv file ---- \n')

        # import the csv
        modelname = str(MW.gee_modelname.currentText())
        modeldata, _cont, terminal, _msg = tlk_scripts.import_modeldata_from_csv(
                                            modelname=str(MW.gee_modelname.currentText()),
                                            csvpath = csv_path)
        if not _cont:
            Error(_msg[0], _msg[1])
            return

        for line in terminal:
            MW.prompt_modeldata.appendPlainText(line)
        MW.prompt_modeldata.appendPlainText(f'\n----  Importing modeldata from csv file ---> Done! ---- \n')

    MW.modeldata = modeldata # store in attributes
    Notification('The Modeldata is succesfully imported!')

    setup_convertor_widgets(MW)

def show_modeldata_info(MW):
    if MW.modeldata is None:
        Error('No modeldata', 'There is no Modeldata imported to show.')
        return
    else:
        MW.prompt_modeldata.appendPlainText(f'\n----  Loaded Modeldata ---- \n')
        terminal = tlk_scripts.get_modeldata_info(MW.modeldata)
        MW.prompt_modeldata.appendPlainText(terminal)



def get_gee_modeldata(MW):
    # check if model has sufficient metadata
    if not _coordinates_available(MW):
        return
    # get modelname
    modelname=str(MW.gee_modelname.currentText())
    obstype =str(MW.model_obstype.currentText())

    # check if obstype is mapped in the GEE dataset
    avail_gee_datasets = _get_all_possible_gee_dataset()
    if not modelname in avail_gee_datasets.keys():
        Error('modelname not found', f'The modelname: {modelname} is not found in the list of known GEE (dynamical) datasets.')
        return
    if not obstype in avail_gee_datasets[modelname]['band_of_use']:
        Error('Obstype not found in GEE dataset', f'{obstype} is not mapped in the {modelname} GEE dataset.')
        return

    MW.prompt_modeldata.appendPlainText(f'\n----  Extracting {obstype} timeseries from {modelname} on GEE ---- \n')
    # get start/end times if needed
    if MW.use_startdt.isChecked():
        # get startdt
        startdtstr = str(MW.gee_startdt.textFromDateTime(MW.gee_startdt.dateTime()))
        startdt = datetime.strptime(startdtstr, '%d/%m/%Y %H:%M')

    else:
        startdt = None

    if MW.use_enddt.isChecked():
        # get startdt
        enddtstr = str(MW.gee_enddt.textFromDateTime(MW.gee_enddt.dateTime()))
        enddt = datetime.strptime(enddtstr, '%d/%m/%Y %H:%M')

        # check if startdt is before enddt
        if startdt >= enddt:
            Error('start - end datetimes', f'{startdt} is not before {enddt}.')
            return
    else:
        enddt = None

    # Get modeldata
    Notification(f'It can take up some time before the modeldata is extracted, or GEE returns a signal. When this is the case, your requested modeldata will probably be writen in your google drive. Read the prompt for more information.')
    modeldata, _cont, terminal, _msg = tlk_scripts.get_modeldata(dataset = MW.dataset,
                                                                 modelname=modelname,
                                                                 modeldata=None,
                                                                 obstype=obstype,
                                                                 stations=None,
                                                                 startdt=startdt,
                                                                 enddt=enddt)
    if not _cont:
        Error(_msg[0], _msg[1])
        return

    for line in terminal:
        MW.prompt_modeldata.appendPlainText(line)

    # it seems that an empty modeldata is returned instead of None, so convert it to None here
    try:
        df = modeldata.df
        if df.empty:
            modeldata_is_empty = True
        else:
            modeldata_is_empty = False
    except:
        modeldata_is_empty = True

    if modeldata_is_empty:
        modeldata = None

    if modeldata is None:
        # storage on google drive
        Notification('The modeldata request was to large, the data will be streamd to your Google Drive. More information can be found in the prompt. Download the file to your device, and set the path in the "Google drive modeldata file".')

    else:
        # store modeldata temorary
        MW.modeldata_temporar = modeldata
        Notification('The modeldata is downloaded succesfully. Click on import modeldata to load it.')

    MW.prompt_modeldata.appendPlainText(f'\n----  Extracting {obstype} timeseries from {modelname} on GEE---> Done! ---- \n')



def browse_google_file(MW):
    fname=QFileDialog.getOpenFileName(MW, 'Select Modeldata file (downloaded from Google drive)', str(Path.home()))
    MW.drive_path.setText(fname[0]) #update text

def browse_external_modeldata_file(MW):
    fname=QFileDialog.getOpenFileName(MW, 'Select Modeldata file.', str(Path.home()))
    MW.external_path.setText(fname[0]) #update text

def save_modeldata(MW):
    if MW.modeldata is None:
        Error('No Modeldata', 'There is no model loaded to save.')
        return

    # create filepath
    filename = str(MW.save_model_pkl.text())
    if not (filename.endswith('.pkl')):
        filename = filename + '.pkl'
        MW.save_model_pkl.setText(filename)


    full_path = os.path.join(path_handler.modeldata_dir, filename)
    print('fp1 : ',full_path)
    print('modeldata just before saing: ', MW.modeldata)

    # check if path exist
    if path_handler.file_exist(full_path):
        Error('file exist', f'The file {full_path} already exists. Change the filename.')
        return

    MW.prompt_modeldata.appendPlainText(f'\n---- Saving the Modeldata ---- \n')

    _cont, terminal, _msg = tlk_scripts.save_modeldata(modeldata=MW.modeldata,
                                                       outputfolder = path_handler.modeldata_dir,
                                                       outputfile=filename)
    if not _cont:
        Error(_msg[0], _msg[1])
        return

    for line in terminal:
        MW.prompt_modeldata.appendPlainText(line)

    MW.prompt_modeldata.appendPlainText(f'\n---- Saving the Modeldata --> Done ---- \n')
    Notification(f'The Modeldata is sucesfully saved as {filename}')

    # updata the pkl spinner
    pkl_cache_files, _ = path_handler.list_filenames(path_handler.modeldata_dir)
    MW.select_pkl.addItems(pkl_cache_files)


def make_plot(MW):
    _show_modeldata(MW)

def show_modeldata_df(MW):
    _show_modeldata_dataframe(MW)




# =============================================================================
# helpers
# =============================================================================


def _widget_grouper(MW):
    dic = {}

    # Modeldata settings
    dic['from_pkl'] = [MW.select_pkl]
    dic['from_external'] = [MW.external_path,
                            MW.external_browse, MW.external_save_path]
    dic['from_gee'] = [MW.gee_modelname, MW.use_startdt, MW.model_obstype,
                       MW.gee_startdt, MW.use_enddt,
                        MW.gee_enddt, MW.get_gee_modeldata, MW.drive_path,
                        MW.browse_drive]
    dic['convertor'] = [MW.obstype_convertor,
                        MW.use_expression,
                        # MW.conv_expression,
                        MW.conv_units]

    dic['save_modeldata_pkl'] = [MW.save_model_pkl, MW.model_save]
    return dic

def _get_all_possible_gee_dataset():
    from metobs_toolkit.settings_files.gee_settings import gee_datasets
    # usefull_gee_dataset = {name: val for name, val in gee_datasets.items() if val["dynamical"]}

    usefull_gee_dataset = {}
    for key, val in gee_datasets.items():
        if val["dynamical"]:
            usefull_gee_dataset[key] = val


    return usefull_gee_dataset