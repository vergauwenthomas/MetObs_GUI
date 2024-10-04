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

# from metobs_gui.json_save_func import get_saved_vals
from metobs_gui.extra_windows import DataDialog, DatasetTimeSeriesDialog
import metobs_gui.tlk_scripts as tlk_scripts
import metobs_gui.path_handler as path_handler
from metobs_gui.errors import Error, Notification
import metobs_gui.pretty_formatter as pretty_formatter
import metobs_toolkit

# =============================================================================
# init page
# =============================================================================
def init_modeldata_page(MW):
    
    dynamic_geemodels = [modname for modname, mod in MW.Dataset.gee_datasets.items() if isinstance(mod, metobs_toolkit.GeeDynamicModelData)]
    MW.gee_modelname.addItems(dynamic_geemodels)
    MW.gee_modelname_2.addItems(dynamic_geemodels)
    MW.gee_modelname_3.addItems(dynamic_geemodels)
    MW.gee_modelname_4.addItems(dynamic_geemodels)
    
    MW.gee_modelname.currentIndexChanged.connect(MW.gee_modelname_2.setCurrentIndex)
    MW.gee_modelname.currentIndexChanged.connect(MW.gee_modelname_3.setCurrentIndex)
    MW.gee_modelname.currentIndexChanged.connect(MW.gee_modelname_4.setCurrentIndex)
  
    
    _setup_found_pkl_spinner(MW)
    _setup_external_pkl_path(MW)
    
    #cascade enable/disable triggers
    _react_input_method_change(MW)
    _react_modelname_change(MW)
    
    


# =============================================================================
# setup page
# =============================================================================
def setup_triggers(MW):
    
    
    MW.model_method.activated.connect(lambda: _react_input_method_change(MW))
    # extract from GEE API
   
    MW.gee_modelname.activated.connect(lambda: _react_modelname_change(MW))
    MW.get_gee_modeldata.clicked.connect(lambda: _react_extract_gee_data(MW))
    MW.get_all_bands_box.stateChanged.connect(lambda: _react_get_all_bands(MW))
    MW.gee_similar_timespan.stateChanged.connect(lambda: _react_use_simil_timespan(MW))
    
    # extract from saved pkl
    MW.import_modeldata_saved_pkl.clicked.connect(lambda: _react_import_modeldata_from_saved_pkl(MW))
    
    # extract from target pkl
    MW.external_mod_browse.clicked.connect(lambda: _react_browse_external_mod(MW))
    MW.external_mod_save_path.stateChanged.connect(lambda: _react_save_external_mod(MW))
    MW.import_mod_from_pkl_button.clicked.connect(lambda: _react_import_modeldata_from_target_pkl(MW))
    
    
    # extract from csv
    MW.browse_drive.clicked.connect(lambda: _react_browse_csv_mod(MW))
    MW.import_modeldata_button.clicked.connect(lambda: _react_import_modeldata_from_csv(MW))
    
    
    
    #analysing
    MW.get_modeldata_info.clicked.connect(lambda: _react_get_modeldata_info(MW))
    MW.show_modeldata.clicked.connect(lambda: _react_show_modeldata(MW))
    MW.plot_modeldata.clicked.connect(lambda: _react_plot_modeldata(MW))
    
    #saving
    MW.model_save.clicked.connect(lambda: _react_save_model(MW))


def _setup_found_pkl_spinner(MW):
    #get a list of all found pkl in the model folder of cache
    files = [f for f in os.listdir(path_handler.modeldata_dir) if f.endswith('.pkl')]
    display_names = [f[:-4] for f in files]
    MW.select_pkl.clear()
    MW.select_pkl.addItems(display_names)
    
def _setup_external_pkl_path(MW):
    savedpaths = path_handler.read_json(path_handler.saved_paths)
    if savedpaths['external_modeldata_path'] != '':
        MW.external_path_mod.setText(savedpaths)
    

# =============================================================================
# Reactions
# =============================================================================
def _react_import_modeldata_from_saved_pkl(MW):
    pretty_formatter.set_prompt_subsection(f' ---- Importing Modeldata from saved pkl --------',
                                           MW.prompt_modeldata)

    trgfile = f'{MW.select_pkl.currentText()}.pkl'
    Modl, succes, stout = tlk_scripts.gui_wrap(metobs_toolkit.import_modeldata_from_pkl,
                                               {'folder_path':path_handler.modeldata_dir,
                                                'filename': trgfile})    
    
    if not succes:
        Error('An error occured when importing modeldata from pkl', stout)
        return
    
    
    MW.prompt_modeldata.appendPlainText(str(stout))
    
    MW.Dataset.gee_datasets[Modl.name] = Modl #overload the modl
    Notification(f'{Modl.name} Modeldata imported from PKL file.')
    
def _react_import_modeldata_from_target_pkl(MW):
    pretty_formatter.set_prompt_subsection(f' ---- Importing Modeldata from target pkl --------',
                                           MW.prompt_modeldata)
    
    trgpath = MW.external_path_mod.text()
    #check if file exist
    if not path_handler.file_exist(trgpath):
        Error(f'The target file does not exist: {trgpath}')
    
    trgfile=path_handler.get_filename_from_path(trgpath)
    trgdir=path_handler.get_parent_dir(trgpath)
    
    Modl, succes, stout = tlk_scripts.gui_wrap(metobs_toolkit.import_modeldata_from_pkl,
                                               {'folder_path':trgdir,
                                                'filename': trgfile})    
    
    if not succes:
        Error('An error occured when importing modeldata from pkl', stout)
        return
    
    
    MW.prompt_modeldata.appendPlainText(str(stout))
    
    MW.Dataset.gee_datasets[Modl.name] = Modl #overload the modl
    Notification(f'{Modl.name} Modeldata imported from PKL file.')

def _react_import_modeldata_from_csv(MW):
    
    modelname=MW.gee_modelname_4.currentText()
    pretty_formatter.set_prompt_subsection(f' ---- Import {modelname} data from CSV file----',
                                           MW.prompt_modeldata)
    #get filepath
    filepath = MW.drive_path.text()
    #check if file exist
    if not path_handler.file_exist(filepath):
        Error(f'{filepath} does not exist.')
        return
    
    #read csv file
    _ret, succes, stout = tlk_scripts.gui_wrap(
                MW.Dataset.gee_datasets[modelname].set_modeldata_from_csv,
                {'csvpath': filepath})
    if not succes:
        Error('Error in importing modeldata from csv.', stout)
    
    MW.prompt_modeldata.appendPlainText(str(stout))

    Notification(f'{modelname} modeldata is imported.')
    

def _react_browse_csv_mod(MW):
    fname=QFileDialog.getOpenFileName(MW, 'Select Modeldata (csv) file', str(Path.home()))
    MW.drive_path.setText(fname[0]) #update text

def _react_save_model(MW):
    modelname = MW.gee_modelname_3.currentText()
    pretty_formatter.set_prompt_subsection(f' ---- Saving {modelname} data to pkl ----',
                                           MW.prompt_modeldata)
    
    # check if there is data
    if MW.Dataset.gee_datasets[modelname].modeldf.empty:
        Error(f'There is no data to save in the {modelname} ModelData.')
        return
    
    trgfile = MW.save_model_pkl.text()
    if not trgfile.endswith('.pkl'):
        Error('The target file must have an ".pkl" extension')
        return

    #check if file already exists
    trgpath = os.path.join(path_handler.modeldata_dir, trgfile)
    if path_handler.file_exist(trgpath):
        Error(f'The target file already exists: {trgpath}')
        return
    
    #save the modeldata to a pkl
    _ret, succes, stout = tlk_scripts.gui_wrap(
                MW.Dataset.gee_datasets[modelname].save_modeldata,
                {'outputfolder': path_handler.modeldata_dir,
                 'filename':trgfile,
                 'overwrite':False})
    if not succes:
        Error('Error in saving modeldata as pkl.', stout)
    
    MW.prompt_modeldata.appendPlainText(str(stout))
    
    Notification(f'{modelname} modeldata is saved.')
    _setup_found_pkl_spinner(MW)

def _react_save_external_mod(MW):
    if MW.external_mod_save_path.isChecked():
        trgpath = MW.external_path_mod.text()
        path_handler.update_json_file({'external_modeldata_path':trgpath},
                                      path_handler.saved_paths)
    else:
        return

def _react_browse_external_mod(MW):
    fname=QFileDialog.getOpenFileName(MW, 'Select Modeldata file', str(Path.home()))
    MW.external_path_mod.setText(fname[0]) #update text

def _react_plot_modeldata(MW):
  
    modelname = MW.gee_modelname_2.currentText()
    MW._dlg = DatasetTimeSeriesDialog(MW.Dataset,
                                       MW.Dataset.gee_datasets[modelname])

def _react_show_modeldata(MW):
    #TODO: WHat modeldata to select??
    modelname = MW.gee_modelname_2.currentText()
    modeldf = MW.Dataset.gee_datasets[modelname].modeldf
    if modeldf.empty:
        Error(f'There is no data in the {modelname}.')
        return     
    
    MW._dlg = DataDialog(df=MW.Dataset.gee_datasets[modelname].modeldf)
    
def _react_modelname_change(MW):
    modelname = MW.gee_modelname.currentText()
    model=MW.Dataset.gee_datasets[modelname]
    known_obstypes = list(model.modelobstypes.keys())
    
    MW.obstypesselect.clear()
    MW.obstypesselect.addItems(known_obstypes)
    
def _react_get_modeldata_info(MW):
    modelname = MW.gee_modelname_2.currentText()
    pretty_formatter.set_prompt_subsection(f' ---- Info of {modelname} ----',
                                           MW.prompt_modeldata)
    _ret, succes, stout = tlk_scripts.gui_wrap(MW.Dataset.gee_datasets[modelname].get_info,
                                               {})
    if not succes:
        Error(f'Error occured when getting info of {modelname}')
        return
    MW.prompt_modeldata.appendPlainText(str(stout))
    MW.prompt_modeldata.centerCursor()
    
def _react_extract_gee_data(MW):
    kwargsdict = {}
    modelname = MW.gee_modelname.currentText()
    pretty_formatter.set_prompt_subsection(f' ---- Download {modelname} data from GEE ----',
                                           MW.prompt_modeldata)
    #Modelname
    modelname = MW.gee_modelname.currentText()
    kwargsdict['Model'] = MW.Dataset.gee_datasets[modelname]
    
    #Obstypes/all bands
    if MW.get_all_bands_box.isChecked():
        kwargsdict['get_all_bands'] = True 
        kwargsdict['obstypes'] = []
    else: 
        obstypes=[obs.text() for obs in MW.obstypesselect.selectedItems()]
        if not bool(obstypes):
            Error('Select at least one observationtype to extract.')
            return
        kwargsdict['get_all_bands'] = False 
        kwargsdict['obstypes'] = obstypes
        
    if MW.gee_similar_timespan.isChecked():
        kwargsdict['startdt'] = None 
        kwargsdict['enddt'] = None
    else:
        startdtstr = str(MW.gee_startdt.textFromDateTime(MW.gee_startdt.dateTime()))
        startdt = datetime.strptime(startdtstr, '%d/%m/%Y %H:%M')
        kwargsdict['startdt'] = startdt
        enddtstr = str(MW.gee_enddt.textFromDateTime(MW.gee_enddt.dateTime()))
        enddt = datetime.strptime(enddtstr, '%d/%m/%Y %H:%M')
        kwargsdict['enddt'] = enddt
        
    kwargsdict['drive_folder'] = MW.gee_drive_folder.text()
    
    model, succes, stout = tlk_scripts.gui_wrap(MW.Dataset.get_modeldata,
                                            kwargsdict)
    if not succes:
        Error('Error occured when extracting data from GEE.', stout)
        return
    
    MW.prompt_modeldata.appendPlainText(str(stout))
    
    #test if model has data of google drive method
    if MW.Dataset.gee_dataset[modelname].modeldf.empty:
        Notification(f'The Data amout is to big for direct transfer. It is written to your google Drive! ')
    else:
        Notification(f'Data extracted from {modelname} on GEE.')
    
    
        
        
    
    
# =============================================================================
# Enable/disable reactions
# =============================================================================

def _react_input_method_change(MW):
    method = MW.model_method.currentText()
    
    gee_widgets=[MW.gee_modelname, MW.obstypesselect,
                 MW.get_all_bands_box, MW.gee_startdt,
                 MW.gee_enddt, MW.gee_similar_timespan,
                 MW.gee_drive_folder, MW.get_gee_modeldata]
    
    csv_widgets=[MW.drive_path, MW.browse_drive,
                 MW.import_modeldata_button]
    
    pkl_saved_widgets=[MW.select_pkl, MW.import_modeldata_saved_pkl]
    pkl_target_widgets=[ MW.external_path_mod,
                 MW.external_mod_browse, MW.external_mod_save_path,
                 MW.import_mod_from_pkl_button, MW.gee_modelname_4]
    
    if method == 'GEE - API':
        for widg in gee_widgets:widg.setEnabled(True)
        for widg in csv_widgets:widg.setEnabled(False)
        for widg in pkl_saved_widgets: widg.setEnabled(False)
        for widg in pkl_target_widgets: widg.setEnabled(False)
        
        _react_get_all_bands(MW)
        _react_use_simil_timespan(MW)
    elif method == 'CSV (downloaded from Google Drive)':
        for widg in gee_widgets:widg.setEnabled(False)
        for widg in csv_widgets:widg.setEnabled(True)
        for widg in pkl_saved_widgets: widg.setEnabled(False)
        for widg in pkl_target_widgets: widg.setEnabled(False)
        
    elif method == 'PKL (saved modeldata)':
        for widg in gee_widgets:widg.setEnabled(False)
        for widg in csv_widgets:widg.setEnabled(False)
        for widg in pkl_saved_widgets: widg.setEnabled(True)
        for widg in pkl_target_widgets: widg.setEnabled(False)
    elif method == 'PKL (local file)':
        for widg in gee_widgets:widg.setEnabled(False)
        for widg in csv_widgets:widg.setEnabled(False)
        for widg in pkl_saved_widgets: widg.setEnabled(False)
        for widg in pkl_target_widgets: widg.setEnabled(True)
    else:
        Error(f'{method} is not known')



def _react_get_all_bands(MW):
    if MW.get_all_bands_box.isChecked():
        MW.obstypesselect.setEnabled(False)
    else: 
        MW.obstypesselect.setEnabled(True)
def _react_use_simil_timespan(MW):
    if MW.gee_similar_timespan.isChecked():
        MW.gee_startdt.setEnabled(False)
        MW.gee_enddt.setEnabled(False)
    else: 
        MW.gee_startdt.setEnabled(True)
        MW.gee_enddt.setEnabled(True)
    
