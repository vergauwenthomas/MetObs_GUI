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

import metobs_toolkit
from metobs_toolkit.template import _get_empty_templ_dict
import metobs_gui.path_handler as path_handler
from metobs_gui.errors import Error



# =============================================================================
# Datafile mapping
# =============================================================================

class New_obstype_Window(QDialog):
    """ Create a new obstype window"""
    
    def __init__(self, Dataset):
        super().__init__()
        
        loadUi(os.path.join(path_handler.GUI_dir, 'qt_windows','new_obstype_dialog.ui'),
               self)
        
        self.Dataset = Dataset
        self.new_obs = None
        
        self._triggers()
        
        
    def _add_new_obstype(self):
        self.new_obs = metobs_toolkit.Obstype(
            obsname=self.obsname.text(),
            std_unit=self.unit.text(),
            description=self.desc.text(),
            unit_aliases={},
            unit_conversions=ast.literal_eval(self.unit_conv.text()))
        
    def _triggers(self):
        self.add_button.clicked.connect(lambda: self._add_new_obstype())
       
        
class New_unit_Window(QDialog):
    """ Create a new obstype window"""
    
    def __init__(self, trg_obstype):
        super().__init__()
        
        loadUi(os.path.join(path_handler.GUI_dir, 'qt_windows','new_unit_dialog.ui'),
               self)
        
        self.new_unit = None
        self.conv = None
        
        self.obsname.setText(trg_obstype.name)
        self.std_unit.setText(trg_obstype.get_standard_unit())
        
        self._triggers()
        
        
    def _add_new_unit(self):
        self.new_unit = self.new_unit_box.text()
        self.conv = ast.literal_eval(self.conv_box.text())
        
        
    def _triggers(self):
        self.add_button.clicked.connect(lambda: self._add_new_unit())



class Data_map_Window(QDialog):
    """ Creates new window """

    def __init__(self, datafile, Dataset):
        super().__init__()
        loadUi(os.path.join(path_handler.GUI_dir, 'qt_windows','templ_build_data.ui'),
               self)

        self.open()
        
        #Data attributes
        self.Dataset = Dataset #toolkit Dataset
        self.datafile = datafile
        self.colnames = []
        self.avail_to_map = [] #columns that are not mapped yet
        self.avail_obstypes = Dataset.obstypes
        
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
        self.colnames = list(_read_datafile(self.datafile).columns)
        self.avail_to_map = copy.copy(self.colnames)
        
        #initiate spinners
        self.timezone_spinner.addItems(pytz.all_timezones)
        self.timezone_spinner.setCurrentText('UTC')
        
        self.column_spinner.addItems(self.avail_to_map)
        
        self.browse_format.clear()
        self.browse_format.addItems(['Long data', 'Wide data'])
        
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
        self.unit.clear()
        self.unit.addItems(cur_obstype.get_all_units())
        self.unit.setCurrentText(cur_obstype.get_standard_unit())
        
        #description
        self.obs_desc.setText(cur_obstype.get_description())
        
        self._print_info()
        
    def _map_an_obstype(self):
        obsname = str(self.obs_type.currentText())
        columnname = str(self.column_spinner.currentText())
        obsmapdict = {
                    "tlk_obstype": obsname,
                    "columnname": columnname,
                    "unit": str(self.unit.currentText()),
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
        new_obs_dialog.exec_()
        
        new_obs = new_obs_dialog.new_obs
        
        #add it to the Dataset
        self.Dataset.add_new_observationtype(new_obs)
        #add it to avail obstypes
        self.avail_obstypes[new_obs.name] = new_obs
        
        #reload the spinners
        self.obs_type.clear()
        self.obs_type.addItems(self.avail_obstypes.keys())
        
        
        
    def _react_add_new_unit(self):
        """ the user want to create a new unit """
        
        active_obstypename = self.obs_type.currentText()
        new_unit_dialog = New_unit_Window(trg_obstype=self.Dataset.obstypes[active_obstypename])
        new_unit_dialog.setWindowTitle("NEW UNIT")
        new_unit_dialog.exec_()
        
        new_unit = new_unit_dialog.new_unit
        new_conv = new_unit_dialog.conv
        
        #add it to the Dataset
        self.Dataset.add_new_unit(obstype=active_obstypename,
                                  new_unit=new_unit,
                                  conversion_expression=new_conv)
        
        
        #reload the spinners
        self._react_to_obstype_change()
        
        
        
    # =============================================================================
    # Setup triggers 
    # =============================================================================
        
        
    def _set_triggers_data_mapping_dialog(self):
        print("define triggers")
        
        self.browse_format.activated.connect(lambda: self._react_data_structure())
        self.timestamp_repr_spinner.activated.connect(lambda: self._react_timestamp_repr())
        self.name_repr.activated.connect(lambda: self._react_name_repr())
        self.obs_type.activated.connect(lambda: self._react_to_obstype_change())
        self.map_obstype_but.clicked.connect(lambda: self._map_an_obstype())
        self.update_temp_button.clicked.connect(lambda: self._print_info())
        
        self.add_obstype.clicked.connect(lambda: self._react_add_new_obs())
        self.add_unit.clicked.connect(lambda: self._react_add_new_unit())
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
            
        
            
    def _display_avail_obstypes(self):
        self.obs_type.clear()
        self.obs_type.addItems(self.avail_obstypes.keys())
        
        #always update the unit and desc
        self._react_to_obstype_change()
        





# =============================================================================
# Special functions
# =============================================================================


def _read_datafile(datafile, kwargsdict={}):
    from metobs_toolkit.data_import import _read_csv_to_df
    
    
    kwargsdict['nrows'] = 20
    df = _read_csv_to_df(filepath=datafile,
                         kwargsdict=kwargsdict)
    return df
    
    
    