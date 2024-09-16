#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 16 13:34:41 2024

@author: thoverga
"""


import os
import copy
import pandas as pd
import pytz
from PyQt5.QtWidgets import  QDialog
from PyQt5.uic import loadUi

import metobs_toolkit
import metobs_gui.path_handler as path_handler
from metobs_gui.errors import Error





# =============================================================================
# Datafile mapping
# =============================================================================

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
       
        self.avail_default_obstypes = Dataset.obstypes.keys()
        
        #initialize values
        self._init_data_mapping_dialog()
        
        #setup values
        self._setup_data_mapping_dialog()
        
        #set triggers
        self._set_triggers_data_mapping_dialog()




        
    
    
    def _init_data_mapping_dialog(self):
        
        #read columnnames
        self.colnames = list(_read_datafile(self.datafile).columns)
        self.avail_to_map = copy.copy(self.colnames)
        
        #initiate spinners
        self.timezone_spinner.addItems(pytz.all_timezones)
        self.timezone_spinner.setCurrentText('UTC')
        
        self.column_spinner.addItems(self.avail_to_map)
        
        
        
        
        return

        
        
    
    def _setup_data_mapping_dialog(self):
        """ enable/disable widgets by values """
        mapped_columns = {} 
        
        #Long-wide setup
        
        datafmt = self.browse_format.currentText()
        name_repr_options = ['A single column',
                             'All columns represent stations',
                             'Not a column (= single station)']
        
        if datafmt == 'Wide data':
            self.column_spinner.setEnabled(False)
            self.name_repr.clear()
            print(name_repr_options[1:])
            self.name_repr.addItems(name_repr_options[1:])
            
        elif datafmt == 'Long data':
            self.column_spinner.setEnabled(True)
            
            self.name_repr.clear()
            self.name_repr.addItems(name_repr_options)
        else:
            Error(f'{datafmt} is not a valid format.')
            
        #datetime fmt setup
        timestamp_rep = self.timestamp_repr_spinner.currentText()
        if timestamp_rep == 'A single column with datetimes':
            self.dt_label1.setText('Timestamp column')
            
            self.dt_col1_spinner.clear()
            self.dt_col1_spinner.addItems(self.avail_to_map)
            
            self.dt_col2_spinner.setEnabled(False)
        
            mapped_columns[self.dt_col1_spinner.currentText()] = 'The timestamp column' 
            
        elif timestamp_rep == 'A data column and a time column':
            self.dt_label1.setText('Date column: ')
            self.dt_col1_spinner.clear()
            self.dt_col1_spinner.addItems(self.avail_to_map)
            
            self.dt_label2.setText('Time column: ')
            self.dt_col2_spinner.setEnabled(True)
            self.dt_col2_spinner.clear()
            self.dt_col2_spinner.addItems(self.avail_to_map)
            
            mapped_columns[self.dt_col1_spinner.currentText()] = 'The Date column' 
            mapped_columns[self.dt_col2_spinner.currentText()] = 'The time column' 
            
        else:
            Error(f'{timestamp_rep} is not a valid format.')
            
            
        # name col setup
        name_rep = self.name_repr.currentText()
        if name_rep == 'A single column':
            self.name_col_spinner.setEnabled(True)
            self.name_col_spinner.clear()
            self.name_col_spinner.addItems(self.avail_to_map)
            
            self.single_station_name.setEnabled(False)
            
            mapped_columns[self.name_col_spinner.currentText()] = 'The station names (=ID)' 
            
        elif name_rep == 'All columns represent stations':
            self.name_col_spinner.setEnabled(False)
            self.single_station_name.setEnabled(False)
            
        elif name_rep == 'Not a column (= single station)':
            self.name_col_spinner.setEnabled(False)
            self.single_station_name.setEnabled(True)
            
        else:
            Error(f'{name_rep} is not a valid format.')
            
        
        # update printoutput
        self._print_info(mapped_columns)
     
        

        
    def _set_triggers_data_mapping_dialog(self):
        print("define triggers")
        
        self.browse_format.currentTextChanged.connect(lambda: self._setup_data_mapping_dialog())
        self.timestamp_repr_spinner.currentTextChanged.connect(lambda: self._setup_data_mapping_dialog())
        self.name_repr.currentTextChanged.connect(lambda: self._setup_data_mapping_dialog())


    def _print_info(self, infodict):
        
        
        printstr = ' ----- Mapped columns ----- '
        for col in self.colnames:
            if col in infodict:
                mapinfo = infodict[col]
            else:
                mapinfo = 'Not mapped'
                printstr+=f'\n *{col} --> {mapinfo}'
        
        self.mapping_info.clear()
        self.mapping_info.setPlainText(printstr)
        



# =============================================================================
# Special functions
# =============================================================================


def _read_datafile(datafile, kwargsdict={}):
    from metobs_toolkit.data_import import _read_csv_to_df
    
    
    kwargsdict['nrows'] = 20
    df = _read_csv_to_df(filepath=datafile,
                         kwargsdict=kwargsdict)
    return df
    
    
    