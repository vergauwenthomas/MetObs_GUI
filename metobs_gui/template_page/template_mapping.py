#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 16 13:34:41 2024

@author: thoverga
"""


import os
import copy
import pprint
import ast
import pandas as pd
import pytz
from PyQt5.QtWidgets import  QDialog
from PyQt5.uic import loadUi

from metobs_gui.tlk_scripts import gui_wrap
import metobs_toolkit
from metobs_toolkit.template import _get_empty_templ_dict
from metobs_toolkit.template_build_prompt import test_unit

import metobs_gui.path_handler as path_handler
from metobs_gui.errors import Error
import metobs_gui.common_functions as common_func


# =============================================================================
# popup dialogs
# =============================================================================

class New_obstype_Window(QDialog):
    """ Create a new obstype window"""
    
    def __init__(self, Dataset):
        super().__init__()
        
        loadUi(os.path.join(path_handler.GUI_dir, 'qt_windows','new_obstype_dialog.ui'),
               self)
        
        self.Dataset = Dataset
        self.new_obs = None

    


# =============================================================================
# Datafile mapping
# =============================================================================
class Metadata_map_Window(QDialog):
    """ create dialog window for mapping the metadata"""
    def __init__(self, metadatafile):
        super().__init__()
        loadUi(os.path.join(path_handler.GUI_dir, 'qt_windows','templ_build_meta_data.ui'),
               self)

        self.open()
        
        
        #data attributes
        metadf = common_func.read_csv_file(metadatafile, nrows=10)        
        self.metacolumns = list(metadf.columns)
        self.template_dict = _get_empty_templ_dict()
        
        self.available_columns = copy.deepcopy(self.metacolumns)
        
        #init spinners
        self.name_spinner.addItems(self.available_columns)
        self.lat_spinner.addItems(self.available_columns)
        self.lon_spinner.addItems(self.available_columns)
        self.alt_spinner.addItems(self.available_columns)
        
        self.setup_triggers()

        #set the other columns by mimic a trigger
        self._set_other_cols()
        
    
    def _set_other_cols(self):
        #get columns already in spinners
        already_mapped = []
        already_mapped.append(self.name_spinner.currentText())

        if self.latbox.isChecked():
            already_mapped.append(self.lat_spinner.currentText())
        if self.lonbox.isChecked():
            already_mapped.append(self.lon_spinner.currentText())
        if self.altbox.isChecked():
            already_mapped.append(self.alt_spinner.currentText())
        
        #subtract all columns from the already selected
        others = list(set(self.metacolumns) - set(already_mapped))
        self.othercols.clear()
        self.othercols.addItems(others)

    def _react_latbox_change(self):
        if self.latbox.isChecked():
            self.lonbox.setChecked(True)
            self.lat_spinner.setEnabled(True)
            self.lon_spinner.setEnabled(True)
        else:
            self.lonbox.setChecked(False)
            self.lat_spinner.setEnabled(False)
            self.lon_spinner.setEnabled(False)
        

    def _react_lonbox_change(self):
        if self.lonbox.isChecked():
            self.latbox.setChecked(True)
            self.lat_spinner.setEnabled(True)
            self.lon_spinner.setEnabled(True)
        else:
            self.latbox.setChecked(False)
            self.lat_spinner.setEnabled(False)
            self.lon_spinner.setEnabled(False)

    def _react_altbox_change(self):
        if self.altbox.isChecked():
            self.alt_spinner.setEnabled(True)
        else:
            self.alt_spinner.setEnabled(False)
            
    
        
    def setup_triggers(self):
        #checkboxes
        self.latbox.stateChanged.connect(lambda: self._react_latbox_change()) 
        self.lonbox.stateChanged.connect(lambda: self._react_lonbox_change()) 
        self.altbox.stateChanged.connect(lambda: self._react_altbox_change())

        #spinners
        self.name_spinner.activated.connect(lambda: self._set_other_cols())
        self.lat_spinner.activated.connect(lambda: self._set_other_cols())
        self.lon_spinner.activated.connect(lambda: self._set_other_cols())
        self.alt_spinner.activated.connect(lambda: self._set_other_cols())
        
    def _read_users_settings_as_template(self):
        self.template_dict['metadata_related']['name_column'] = self.name_spinner.currentText()
        if self.latbox.isChecked():
            self.template_dict['metadata_related']['lat_column'] = self.lat_spinner.currentText()
            self.template_dict['metadata_related']['lon_column'] = self.lon_spinner.currentText()
            
        other_columns = [select.text() for select in self.othercols.selectedItems()]
        self.template_dict['metadata_related']['columns_to_include'] = other_columns
        

class Data_map_Window(QDialog):
    """ Creates new window """

    def __init__(self, datafile, Dataset):
        super().__init__()
        loadUi(os.path.join(path_handler.GUI_dir, 'qt_windows','templ_build_data.ui'),
               self)

        self.open()
        
        #Data attributes
        self.Dataset = Dataset #toolkit Dataset LINK WITH MAIN AS POINTER!! 
        self.datafile = datafile
        self.colnames = []
        self.avail_to_map = [] #columns that are not mapped yet
        self.avail_obstypes = copy.deepcopy(Dataset.obstypes)
        
        self.template_dict = _get_empty_templ_dict()
        
        #initialize values
        self._init_data_mapping_dialog()
        
        # #setup values
        # self._setup_data_mapping_dialog()
        
        #set triggers
        self._set_triggers_data_mapping_dialog()


    def _init_data_mapping_dialog(self):
        """ set default widget values and set data holders"""
        #read columnnames
        
        df = common_func.read_csv_file(self.datafile, nrows=10)        
        self.colnames = list(df.columns)
        self.avail_to_map = copy.copy(self.colnames)
        
        #initiate spinners
        self.timezone_spinner.addItems(pytz.all_timezones)
        self.timezone_spinner.setCurrentText('UTC')
        
        self.column_spinner.addItems(self.avail_to_map)
        
        self.browse_format.clear()
        self.browse_format.addItems(['Long data', 'Wide data', 'Single-station'])
        
        self.name_repr.clear()
        self.name_repr.addItems(['A single column',
                                 'All columns represent stations',
                                 'Not a column (= single station)'])
        
        #Fake reactions for setting widgets compatible 
        self._react_data_structure()
        self._react_timestamp_repr()
        self._react_name_repr()
        self._display_avail_obstypes()
        self._react_to_obstype_change()
        self._print_info()
        
        return

        
        

     
    # =============================================================================
    # Reactions 
    # =============================================================================
    def _react_data_structure(self):
        "triggerd when data changed (long vs wide)"
        datafmt = self.browse_format.currentText()
        
        self.name_repr.clear()
        name_repr_options = ['A single column',
                             'All columns represent stations',
                             'Not a column (= single station)']
       
        if datafmt == 'Wide data':
            self.column_spinner.setEnabled(False)
            self.name_repr.addItems(name_repr_options[1:])
           
            
        elif datafmt == 'Long data':
            self.column_spinner.setEnabled(True)
            name_repr_options.remove('All columns represent stations')
            self.name_repr.addItems(name_repr_options)

        elif datafmt == 'Single-station':
            self.column_spinner.setEnabled(True)
            self.name_repr.addItems([name_repr_options[0], 
                                     name_repr_options[2]])
           
        else:
            print(f'{datafmt} is not a valid format.')
            # Error(f'{datafmt} is not a valid format.')
            
    def _react_timestamp_repr(self):
        "when specified if timestamps are one or two columns "
        #datetime fmt setup
        timestamp_rep = self.timestamp_repr_spinner.currentText()
        if timestamp_rep == 'A single column with datetimes':
            self.dt_label1.setText('Timestamp column')
            self.date_fmt_label.setText('Timestamp format')
            self.dt_col1_spinner.clear()
            self.dt_col1_spinner.addItems(self.avail_to_map)
            
            self.dt_col2_spinner.setEnabled(False)
            self.time_fmt.setEnabled(False)
            self.date_fmt.setText('%Y/%m/%d %H:%M:%S')
           
            
            
        elif timestamp_rep == 'A data column and a time column':
            self.dt_label1.setText('Date column: ')
            self.date_fmt_label.setText('Date format')
            self.dt_col1_spinner.clear()
            self.dt_col1_spinner.addItems(self.avail_to_map)
            
            self.dt_label2.setText('Time column: ')
            self.dt_col2_spinner.setEnabled(True)
            self.date_fmt.setText('%Y/%m/%d')
            self.time_fmt.setEnabled(True)
            self.dt_col2_spinner.clear()
            self.dt_col2_spinner.addItems(self.avail_to_map)
                        
        else:
            print(f'{timestamp_rep} is not a valid format.')
            
        
    def _react_name_repr(self):
        # name col setup
        name_rep = self.name_repr.currentText()
        if name_rep == 'A single column':
            self.name_col_spinner.setEnabled(True)
            self.name_col_spinner.clear()
            self.name_col_spinner.addItems(self.avail_to_map)
            
            self.single_station_name.setEnabled(False)
            
        elif name_rep == 'All columns represent stations':
            self.name_col_spinner.setEnabled(False)
            self.single_station_name.setEnabled(False)
            
        elif name_rep == 'Not a column (= single station)':
            self.name_col_spinner.setEnabled(False)
            self.single_station_name.setEnabled(True)
            
        else:
            print(f'{name_rep} is not a valid format.')
            # Error(f'{name_rep} is not a valid format.')
        self._print_info()
        
        
        
    def _react_to_obstype_change(self):
        cur_obstype_name = self.obs_type.currentText()
        cur_obstype = self.Dataset.obstypes[cur_obstype_name]
        
        #get available units
        self.related_units.clear()
        self.related_units.addItems(cur_obstype.get_compatible_units())
        self.related_units.setCurrentText(cur_obstype.std_unit)
        
        self.cur_unit.setText(cur_obstype.std_unit)

        #description
        self.obs_desc.setText(cur_obstype.description)
        
        self._print_info()
    
    def _map_time(self):
        to_drop_columns = []

        #collect the columns that are mapped
        timestamp_rep = self.timestamp_repr_spinner.currentText()
        if timestamp_rep == 'A single column with datetimes':
            to_drop_columns.append(self.dt_col1_spinner.currentText())
        elif timestamp_rep == 'A data column and a time column':
            to_drop_columns.append(self.dt_col1_spinner.currentText())
            to_drop_columns.append(self.dt_col2_spinner.currentText())
        
        # drop from available columns
        for todropcol in to_drop_columns:
            self.avail_to_map.remove(todropcol)
        self.column_spinner.clear()
        self.column_spinner.addItems(self.avail_to_map)

        #set disabled
        self.dt_col1_spinner.setEnabled(False)
        self.dt_col2_spinner.setEnabled(False)
        self.timestamp_repr_spinner.setEnabled(False)
        self.map_time_but.setEnabled(False)
        self.date_fmt.setEnabled(False)
        self.time_fmt.setEnabled(False)
        self.timezone_spinner.setEnabled(False)

        #update template status
        self._print_info()

    def _map_name(self):
    

        if self.name_repr.currentText() == 'A single column':
            todropcol = self.name_col_spinner.currentText()
            self.avail_to_map.remove(todropcol)

        self.column_spinner.clear()
        self.column_spinner.addItems(self.avail_to_map)

        #set disabled
        self.name_col_spinner.setEnabled(False)
        self.name_repr.setEnabled(False)
        self.map_name_but.setEnabled(False)
        self.single_station_name.setEnabled(False)

        #update template status
        self._print_info()

    def _map_an_obstype(self):
        obsname = str(self.obs_type.currentText())
        columnname = str(self.column_spinner.currentText())
        unitname = str(self.cur_unit.text())

        #test if unit is compatible with the Obstype
        try:
            self.Dataset.obstypes[obsname].original_unit = unitname #this checks compatibility
        except Exception as e:
                Error(str(e), '')
                return
            
        obsmapdict = {
                    "tlk_obstype": obsname,
                    "columnname": columnname,
                    "unit": unitname,
                    "description": str(self.obs_desc.text()),
                }
        #add it to the template dict
        self.template_dict['data_related']['obstype_mapping'].append(obsmapdict)
        #remove obstype from available obstypes
        self.avail_obstypes.pop(obsname)
        #remove column from available columns
        self.avail_to_map.remove(columnname)
        self.column_spinner.clear()
        self.column_spinner.addItems(self.avail_to_map)
        #long wide check
        if self.browse_format == 'Wide data':
            self.column_spinner.setEnabled(False)
            self.obs_type.setEnabled(False)
            self.unit.setEnabled(False)
            self.obs_desc.setEnabled(False)
        
        self._print_info()
        self._display_avail_obstypes()
        
        
    def _react_add_new_obs(self):
        """ the user want to create a new observationtype """
        
        new_obs_dialog = New_obstype_Window(Dataset=self.Dataset)
        new_obs_dialog.setWindowTitle("NEW OBSERVATIONTYPE")
        # new_obs_dialog.exec_()
        if new_obs_dialog.exec():
            #scrape dialog
            newobsname = new_obs_dialog.obsname.text()
            std_unit = new_obs_dialog.unit.text()
            desc = new_obs_dialog.desc.text()
            
            
            try:
                #create obstype
                newobstype = metobs_toolkit.Obstype(
                    obsname=newobsname,
                    std_unit=std_unit,
                    description=desc,
                )
            except Exception as e:
                Error(str(e), '')
                return
            
            #add it to the Dataset
            gui_wrap(self.Dataset.add_new_observationtype, 
                     {'obstype': newobstype})
            
            
            #add it to avail obstypes
            self.avail_obstypes[newobstype.name] = newobstype
            
            #reload the spinners
            self.obs_type.clear()
            self.obs_type.addItems(self.avail_obstypes.keys())
        else:
            #dialog is closed or canceled.
            pass
        
        
        
   
    
    # =============================================================================
    # Setup triggers 
    # =============================================================================
        
        
    def _set_triggers_data_mapping_dialog(self):
        #spinners
        self.browse_format.activated.connect(lambda: self._react_data_structure())
        self.timestamp_repr_spinner.activated.connect(lambda: self._react_timestamp_repr())
        self.name_repr.activated.connect(lambda: self._react_name_repr())
        self.obs_type.activated.connect(lambda: self._react_to_obstype_change())
        
        #button triggers
        self.map_time_but.clicked.connect(lambda: self._map_time())
        self.map_name_but.clicked.connect(lambda: self._map_name())
        self.add_obstype.clicked.connect(lambda: self._react_add_new_obs())
        self.map_obstype_but.clicked.connect(lambda: self._map_an_obstype()) 
   
    
    def _print_info(self):
        self._read_users_settings_as_template() #update template dict
        self.mapping_info.clear()
        self.mapping_info.setPlainText(pprint.pformat(self.template_dict))
        
        
        
            
    # =============================================================================
    # Others
    # =============================================================================
    
    def _read_users_settings_as_template(self):
        """ Read all the fields and update the template dict accordingly"""
        datafmt = self.browse_format.currentText()
        if datafmt == 'Wide data':
            self.template_dict['data_related']['structure'] = 'wide'
        elif datafmt == 'Long data':
            self.template_dict['data_related']['structure'] = 'long'
        
        elif datafmt == 'Single-station':
            self.template_dict['data_related']['structure'] = 'single_station'
        else:
            pass
        
        timestamp_rep = self.timestamp_repr_spinner.currentText()
        self.template_dict['data_related']['timestamp']["timezone"] = self.timezone_spinner.currentText()
        if timestamp_rep == 'A single column with datetimes':
            self.template_dict['data_related']['timestamp']["datetime_column"] = self.dt_col1_spinner.currentText()
            self.template_dict['data_related']['timestamp']["datetime_fmt"] = self.date_fmt.text()
            self.template_dict['data_related']['timestamp']["date_column"] = None
            self.template_dict['data_related']['timestamp']["date_fmt"] = None
            self.template_dict['data_related']['timestamp']["time_column"] = None
            self.template_dict['data_related']['timestamp']["time_fmt"] = None
            
        elif timestamp_rep == 'A data column and a time column':
            self.template_dict['data_related']['timestamp']["datetime_column"] = None
            self.template_dict['data_related']['timestamp']["datetime_fmt"] = None
            self.template_dict['data_related']['timestamp']["date_column"] = self.dt_col1_spinner.currentText()
            self.template_dict['data_related']['timestamp']["date_fmt"] = self.date_fmt.text()
            self.template_dict['data_related']['timestamp']["time_column"] = self.dt_col2_spinner.currentText()
            self.template_dict['data_related']['timestamp']["time_fmt"] = self.time_fmt.text()
        else:
            pass
        
        name_rep = self.name_repr.currentText()
        if name_rep == 'A single column':
            self.template_dict['data_related']['name_column'] = self.name_col_spinner.currentText()
            self.template_dict['single_station_name'] = None
        elif name_rep == 'All columns represent stations':
            self.template_dict['data_related']['name_column'] = None
            self.template_dict['single_station_name'] = None
        elif name_rep == 'Not a column (= single station)':
            self.template_dict['data_related']['name_column'] = None
            self.template_dict['single_station_name'] = self.single_station_name.text()
            
        
        #remove the None (default) obstype
        only_mapped = []
        for obs_map_dict in self.template_dict['data_related']['obstype_mapping']:
            if obs_map_dict['columnname'] is not None:
                only_mapped.append(obs_map_dict)
        
        self.template_dict['data_related']['obstype_mapping'] = only_mapped
        
        
            
    def _display_avail_obstypes(self):
        self.obs_type.clear()
        self.obs_type.addItems(self.avail_obstypes.keys())
        
        #always update the unit and desc
        self._react_to_obstype_change()
        


    