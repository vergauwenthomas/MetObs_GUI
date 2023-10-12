#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 20 09:47:48 2023

@author: thoverga
"""

# command: designer in terminal to open the desinger tool



import os, sys
import matplotlib

from metobs_toolkit import loggers as toolkit_logger


from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.uic import loadUi


import metobs_gui.path_handler as path_handler
from metobs_gui.pandasmodel import DataFrameModel

import metobs_gui.log_displayer as log_displayer


import metobs_gui.template_page as template_page
import metobs_gui.import_data_page as import_page
import metobs_gui.metadata_page as metadata_page
import metobs_gui.qc_page as qc_page
import metobs_gui.modeldata_page as modeldata_page
import metobs_gui.fill_page as fill_page
import metobs_gui.analysis_page as analysis_page
import metobs_gui.gui_settings_page as gui_settings_page



class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        # Load gui widgets
        loadUi(os.path.join(path_handler.GUI_dir,'mainwindow.ui'),
               self) #open the ui file

        # -------- Information to pass beween different triggers ----------
        self.dataset = None #the vlindertoolkit dataset instance
        self.modeldata = None
        self.analysis = None
        self.cycle_stats = None #test
        self.extra_obstypes = {}

        self.modeldata_temporar = None #for termporal storage on direct input from gee

        self.long_storage = {} #will read the json file to store info over mulitple settings
        self.session = {} #store info during one session

        # P1 INIT
        template_page.init_template_page(self)

        # P2 INIT
        import_page.init_import_page(self)

        # P3 INIT
        metadata_page.init_metadata_page(self)

        # P4 INIT
        qc_page.init_qc_page(self)

        # P5 INIT
        modeldata_page.init_modeldata_page(self)

        # P6 INIT
        fill_page.init_fill_page(self)

        # P7 INIT
        analysis_page.init_analysis_page(self)





        # ------- Setup (widgets and default values) ---------------

        # Setup error message dialog
        self.error_dialog = QtWidgets.QErrorMessage(self)


        # setup metobs toolkit log handles to stream to prompts

        input_page_log_handler = log_displayer.QPlainTextEditLogger(self.prompt)
        metadata_page_log_handler = log_displayer.QPlainTextEditLogger(self.prompt_metadata)
        qc_page_log_handler = log_displayer.QPlainTextEditLogger(self.prompt_qc)
        fill_page_log_handler = log_displayer.QPlainTextEditLogger(self.prompt_fill)
        modeldata_page_log_handler = log_displayer.QPlainTextEditLogger(self.prompt_modeldata)
        toolkit_logger.addHandler(input_page_log_handler)
        toolkit_logger.addHandler(metadata_page_log_handler)
        toolkit_logger.addHandler(qc_page_log_handler)
        toolkit_logger.addHandler(fill_page_log_handler)
        toolkit_logger.addHandler(modeldata_page_log_handler)




        # link dfmodels to tables
        self.templmodel = DataFrameModel()
        self.table.setModel(self.templmodel)


        # ------- Callbacks (triggers) ------------


        # =============================================================================
        # Windget links
        # =============================================================================
        self.data_file_T.textChanged.connect(self.data_file_T_2.setText) #link them
        self.metadata_file_T.textChanged.connect(self.metadata_file_T_2.setText) #link them
        self.use_startdt.clicked.connect(self.use_enddt.setCheckState) #link them
        self.use_enddt.clicked.connect(self.use_startdt.setCheckState) #link them







        # =============================================================================
        # Mapping tab
        # =============================================================================
        template_page.setup_template_triggers(self)

        # =============================================================================
        # Import data tab
        # =============================================================================
        import_page.setup_import_triggers(self)


        # =============================================================================
        # Metadata tab
        # =============================================================================
        metadata_page.setup_metadatapage(self)

        # =============================================================================
        # QC tab
        # =============================================================================
        qc_page.setup_qc_triggers(self)

        # =============================================================================
        # Modeldata tab
        # =============================================================================
        modeldata_page.setup_modeldata_triggers(self)
        self.external_save_path.clicked.connect(lambda: template_page.save_path(
                                                                MW=self,
                                                                savebool=True,
                                                                savekey='external_modeldata_path',
                                                                saveval=self.external_path.text()))



        # =============================================================================
        # Fill tab
        # =============================================================================
        fill_page.setup_fill_page(self)


        # =============================================================================
        # Analysis tab
        # =============================================================================

        analysis_page.setup_analysis_page(self)


        # =============================================================================
        # GUI settings
        # =============================================================================
        self.clear_saved.clicked.connect(lambda: gui_settings_page.clear_cache(self))

# =============================================================================
# Helpers
# =============================================================================
    def get_val(self, data_func_return):

        if not data_func_return[1]:
            self.error_dialog.showMessage(data_func_return[2])
        return data_func_return[0]







def main():
    # setup_logging()
    app=QApplication(sys.argv)

    mainwindow = MainWindow()
    mainwindow.show()


    # html = _show_spatial_html('/home/thoverga/mymap.html')
    # html.show()
    # widget = QtWidgets.QStackedWidget()
    # widget.addWidget(mainwindow)
    # widget.show()

    # following lines are log window --> uncomment for debugging
    # dlg = MyDialog()
    # dlg.show()
    # dlg.raise_()

    succesfull=True
    # except:
    #     print('Failing !')
    #     # sys.exit('Something went wrong in the GUI')
    #     succesfull=False
    #     pass
    sys.exit(app.exec_())

    return succesfull
    # try:
    #     app=QApplication(sys.argv)

    #     mainwindow = MainWindow()
    #     widget = QtWidgets.QStackedWidget()
    #     widget.addWidget(mainwindow)
    #     widget.show()
    #     succesfull=True
    # except:
    #     print('Failing !')
    #     # sys.exit('Something went wrong in the GUI')
    #     succesfull=False
    #     pass
    # sys.exit(app.exec_())

    # return succesfull


if __name__ == '__main__':
    matplotlib.use('Qt5Agg') #in protector because server runners do not support this, when this module is imported from the __init__
    app=QApplication(sys.argv)
    main()

    # mainwindow = MainWindow()
    # mainwindow.show()
    # widget = main()
    # widget.show()
    # sys.exit(app.exec_())



