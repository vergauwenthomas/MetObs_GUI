""" Module for displaying a dialog for inspecting the dataframe
    'attributes' of a Dataset or Station."""

import os
import pandas as pd
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QDialog

import metobs_gui.path_handler as path_handler
from metobs_gui.pandasmodel import DataFrameModel
from metobs_gui.tlk_scripts import gui_wrap, get_function_defaults
# =============================================================================
# Show full status df
# =============================================================================
class DataDialog(QDialog):
    """ Displays a dataframe"""

    def __init__(self, dataset):
        super().__init__()
        loadUi(os.path.join(path_handler.GUI_dir,'qt_windows','show_data_dialog.ui'), self)
        self.open()
        
        # Define data attributes
        #Flatten multindex
        self.Dataset = dataset
    
        # Feed it to the widget
        self.combmodel = DataFrameModel()
        self.combmodel.setDataFrame(self.Dataset.df.reset_index())
        self.merge_table.setModel(self.combmodel)
        
        self._setup_spinners()
        self._setup_triggers()
        
    def _setup_spinners(self):
        #get attr
        attrnames = ['df', 'metadf', 'outliersdf', 'gapsdf', 'modeldatadf']
        self.data_attr_spinner.clear()
        self.data_attr_spinner.addItems(attrnames)


        #get station names
        stanames = self.Dataset.df.index.get_level_values('name').unique().to_list()
        stanames.insert(0, 'ALL')
        self.name_spinbox.clear()
        self.name_spinbox.addItems(stanames)
        
        #get opbstypes 
        obstypes=self.Dataset.df.index.get_level_values('obstype').unique().to_list()
        obstypes.insert(0, 'ALL')
        self.obstype_spinbox.clear()
        self.obstype_spinbox.addItems(obstypes)
        
        
    def _setup_triggers(self):
        self.apply_filter.clicked.connect(lambda: self._react_apply_filter())
        
    
    def _react_apply_filter(self):
        #Get dattaframe
        subdf = getattr(self.Dataset, self.data_attr_spinner.currentText())


        #subset to name        
        subset_name = self.name_spinbox.currentText()
        if subset_name == 'ALL':
            pass
        else:
            if subset_name in subdf.index.get_level_values('name'):
                subdf =  subdf.xs(subset_name, level='name',drop_level=False)
            else:
                subdf = pd.DataFrame()

        #subset to obstype     
        subset_obstype= self.obstype_spinbox.currentText()
        if subset_obstype == 'ALL':
            pass
        else:
            if subset_obstype in subdf.index.get_level_values('obstype'):
                subdf =  subdf.xs(subset_obstype, level='obstype',drop_level=False)
            else:
                pd.DataFrame()
        #update the table widget
        self.combmodel.setDataFrame(subdf.reset_index())


