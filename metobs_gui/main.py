#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 20 09:47:48 2023

@author: thoverga
"""

# command: designer in terminal to open the desinger tool



import os, sys
import matplotlib


import metobs_toolkit
from metobs_toolkit import rootlog as toolkit_logger

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.uic import loadUi


import metobs_gui.path_handler as path_handler
from metobs_gui.pandasmodel import DataFrameModel

import metobs_gui.log_displayer as log_displayer


import metobs_gui.template_page.template_page as template_page
import metobs_gui.import_data_page.import_data_page as import_page
import metobs_gui.gee_page.gee_page as gee_page
import metobs_gui.qc_page.qc_page as qc_page
import metobs_gui.gf_page.gf_page as gf_page
# import metobs_gui.analysis_page as analysis_page
import metobs_gui.gui_settings_page as gui_settings_page



class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        # Load gui widgets
        loadUi(os.path.join(path_handler.GUI_dir,'qt_windows','mainwindow.ui'),
               self) #open the ui file

        # -------- Information to pass beween different triggers ----------
        self.Dataset = metobs_toolkit.Dataset() #the toolkit dataset instance
        self._Dataset_imported=False #bool if dataset is imported
        # self.modeldata = None
        # self.analysis = None
        # self.cycle_stats = None #test
        
        # -----Setup GUI storage (long term: cache, and session term: temp) ----
        self.modeldata_temporar = None #for termporal storage on direct input from gee
        self.long_storage = {} #will read the json file to store info over mulitple settings
        self.session = {} #store info during one session
        
        path_handler._setup_cache_dir()
        path_handler._setup_temp_dir()

        # P1 INIT
        template_page.init_page(self)

        # # P2 INIT
        import_page.init_page(self)

        # # P3 INIT
        gee_page.init_page(self)

        # # P4 INIT
        qc_page.init_qc_page(self)

        # # P5 INIT
        # modeldata_page.init_modeldata_page(self)

        # # P6 INIT
        gf_page.init_fill_page(self)

        # # P7 INIT
        # analysis_page.init_analysis_page(self)
 
        #P8 INIT
        gui_settings_page._init_page(self)
    

        # ------- Setup (widgets and default values) ---------------

        # Setup error message dialog
        self.error_dialog = QtWidgets.QErrorMessage(self)


        # setup metobs toolkit log handles to stream to prompts

        input_page_log_handler = log_displayer.QPlainTextEditLogger(self.prompt)

        toolkit_logger.addHandler(input_page_log_handler)



        # link dfmodels to tables
        self.templmodel = DataFrameModel()
        self.table.setModel(self.templmodel)


    


        # =============================================================================
        # Windget cross links
        # =============================================================================
        
        self.data_file_T.textChanged.connect(self.data_file_T_2.setText) #link them
        self.metadata_file_T.textChanged.connect(self.metadata_file_T_2.setText) #link them
        
        self.use_data_box.clicked.connect(self.use_data_T_2.setCheckState) #link them
        self.use_metadata_box.clicked.connect(self.use_metadata_2.setCheckState) #link them
        


        # =============================================================================
        # Setup triggers         
        # =============================================================================
        
        
        template_page.setup_triggers(self)
        import_page.setup_triggers(self)
        gee_page.setup_triggers(self)
        qc_page.setup_triggers(self)
        gf_page.setup_triggers(self)
        gui_settings_page._setup_triggers(self)

       


       
    # ------- cross-tabs-reactions (triggers) ------------
    
    def react_dataset_loaded(self):
        """ Reaction when a dataset is loaded"""

        #Setup of present obstype spinners
        present_obs = list(self.Dataset.df.index.get_level_values('obstype').unique())
        obstype_spin_list = [self.obstype_spinner,
                            self.fill_obstype,
                            self.convert_outliers_trgs,
                            ]
        
        for spin in obstype_spin_list:
            spin.clear()
            spin.addItems(present_obs)

        #Enable widgets
        enable_list = [self.update_method_settings,
                       self.convert_outliers]
        for widg in enable_list:
            widg.setEnabled(True)

        #Special reactions
        gf_page._react_dataset_loaded(self)




def main():

    app=QApplication(sys.argv)

    mainwindow = MainWindow()
    mainwindow.show()
    succesfull=True
  
    sys.exit(app.exec_())

    return succesfull
  

if __name__ == '__main__':
    matplotlib.use('Qt5Agg') #in protector because server runners do not support this, when this module is imported from the __init__
    app=QApplication(sys.argv)
    main()

   


