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
        loadUi(os.path.join(path_handler.GUI_dir,'qt_windows','mainwindow.ui'),
               self) #open the ui file

        # -------- Information to pass beween different triggers ----------
        self.Dataset = metobs_toolkit.Dataset() #the toolkit dataset instance
        self._Dataset_imported=False #bool if dataset is imported
        self.modeldata = None
        self.analysis = None
        self.cycle_stats = None #test
        
        # -----Setup GUI storage (long term: cache, and session term: temp) ----
        self.modeldata_temporar = None #for termporal storage on direct input from gee
        self.long_storage = {} #will read the json file to store info over mulitple settings
        self.session = {} #store info during one session
        
        path_handler._setup_cache_dir()
        path_handler._setup_temp_dir()

        # P1 INIT
        template_page.init_template_page(self)

        # # P2 INIT
        import_page.init_import_page(self)

        # # P3 INIT
        metadata_page.init_metadata_page(self)

        # # P4 INIT
        qc_page.init_qc_page(self)

        # # P5 INIT
        # modeldata_page.init_modeldata_page(self)

        # # P6 INIT
        # fill_page.init_fill_page(self)

        # # P7 INIT
        # analysis_page.init_analysis_page(self)

        gui_settings_page._init_page(self)
    

        # ------- Setup (widgets and default values) ---------------

        # Setup error message dialog
        self.error_dialog = QtWidgets.QErrorMessage(self)


        # setup metobs toolkit log handles to stream to prompts

        input_page_log_handler = log_displayer.QPlainTextEditLogger(self.prompt)
        # metadata_page_log_handler = log_displayer.QPlainTextEditLogger(self.prompt_metadata)
        # qc_page_log_handler = log_displayer.QPlainTextEditLogger(self.prompt_qc)
        # fill_page_log_handler = log_displayer.QPlainTextEditLogger(self.prompt_fill)
        # modeldata_page_log_handler = log_displayer.QPlainTextEditLogger(self.prompt_modeldata)
        toolkit_logger.addHandler(input_page_log_handler)
        # toolkit_logger.addHandler(metadata_page_log_handler)
        # toolkit_logger.addHandler(qc_page_log_handler)
        # toolkit_logger.addHandler(fill_page_log_handler)
        # toolkit_logger.addHandler(modeldata_page_log_handler)


        # link dfmodels to tables
        self.templmodel = DataFrameModel()
        self.table.setModel(self.templmodel)


        # ------- Callbacks (triggers) ------------


        # =============================================================================
        # Windget cross links
        # =============================================================================
        
        self.data_file_T.textChanged.connect(self.data_file_T_2.setText) #link them
        self.metadata_file_T.textChanged.connect(self.metadata_file_T_2.setText) #link them
        
        self.use_data_box.clicked.connect(self.use_data_T_2.setCheckState) #link them
        self.use_metadata_box.clicked.connect(self.use_metadata_2.setCheckState) #link them
        
        # self.use_startdt.clicked.connect(self.use_enddt.setCheckState) #link them
        # self.use_enddt.clicked.connect(self.use_startdt.setCheckState) #link them


        # =============================================================================
        # Setup triggers         
        # =============================================================================
        
        
        template_page._setup_triggers(self)
        import_page._setup_triggers(self)
        metadata_page.setup_triggers(self)
        qc_page.setup_triggers(self)
       

       


        # # =============================================================================
        # # Modeldata tab
        # # =============================================================================

        # self.model_method.currentTextChanged.connect(lambda: modeldata_page.setup_model_settings(self))

        # self.use_startdt.clicked.connect(lambda: modeldata_page.setup_model_dt(self))
        # self.use_enddt.clicked.connect(lambda: modeldata_page.setup_model_dt(self))

        # self.get_gee_modeldata.clicked.connect(lambda: modeldata_page.get_gee_modeldata(self))
        # self.import_modeldata.clicked.connect(lambda : modeldata_page.import_modeldata(self))

        # self.external_browse.clicked.connect(lambda: modeldata_page.browse_external_modeldata_file(self))
        # self.browse_drive.clicked.connect(lambda: modeldata_page.browse_google_file(self))

        # self.external_save_path.clicked.connect(lambda: template_page.save_path(
        #                                                         MW=self,
        #                                                         savebool=True,
        #                                                         savekey='external_modeldata_path',
        #                                                         saveval=self.external_path.text()))

        # self.obstype_convertor.currentTextChanged.connect(lambda : modeldata_page.get_tlk_unit(self))
        # self.use_expression.clicked.connect(lambda: modeldata_page.setup_conv_expression(self))
        # self.conv_units.clicked.connect(lambda: modeldata_page.convert_units(self))

        # self.get_modeldata_info.clicked.connect(lambda: modeldata_page.show_modeldata_info(self))
        # self.plot_modeldata.clicked.connect(lambda: modeldata_page.make_plot(self))
        # self.show_modeldata.clicked.connect(lambda: modeldata_page.show_modeldata_df(self))
        # self.model_save.clicked.connect(lambda: modeldata_page.save_modeldata(self))

        # # =============================================================================
        # # Fill tab
        # # =============================================================================
        # self.fill_gaps_technique.currentTextChanged.connect(lambda: fill_page.setup_gap_settings(self))
        # self.fill_missing.clicked.connect(lambda: fill_page.apply_fill_missing(self))
        # self.apply_convert_outl.clicked.connect(lambda: fill_page.setup_convert_outliers(self))
        # self.gapsize_conv.valueChanged.connect(lambda: fill_page.assume_gapsize(self))

        # self.conv_outliers.clicked.connect(lambda: fill_page.convert_outl_to_mis(self))
        # self.fill_gaps.clicked.connect(lambda: fill_page.apply_fill_gaps(self))

        # # bottom buttens
        # self.print_missing_info.clicked.connect(lambda: fill_page.make_print_missing_obs(self))
        # self.print_gap_info.clicked.connect(lambda: fill_page.make_print_gaps(self))
        # self.print_dataset_info.clicked.connect(lambda: fill_page.make_print_dataset(self))

        # self.show_missing.clicked.connect(lambda: fill_page.show_df_missing_obs(self))
        # self.show_gaps.clicked.connect(lambda: fill_page.show_df_gaps(self))
        # self.show_dataset_4.clicked.connect(lambda: fill_page.show_df_dataset(self))

        # self.show_filled_missing.clicked.connect(lambda: fill_page.show_filled_df_missing_obs(self))
        # self.show_filled_gaps.clicked.connect(lambda: fill_page.show_filled_df_gaps(self))

        # self.plot_dataset_6.clicked.connect(lambda: fill_page.plot_dataset(self))



        # # =============================================================================
        # # Analysis tab
        # # =============================================================================

        # self.create_analysis.clicked.connect(lambda: analysis_page.create_analysis(self))
        # self.groupdef_custom.textChanged.connect(lambda: analysis_page.update_horizontal_axis_possibilities(self))

        # self.apply_filter.clicked.connect(lambda: analysis_page.filter_analysis(self))
        # self.plot_diurnal.clicked.connect(lambda: analysis_page.diurnal_plot_trigger(self))
        # self.plot_anual.clicked.connect(lambda: analysis_page.anual_plot_trigger(self))
        # self.plot_custom.clicked.connect(lambda: analysis_page.custom_cycle_plot_trigger(self))
        # self.get_cor.clicked.connect(lambda: analysis_page.get_lc_correlations(self))
        # self.make_heat_plot.clicked.connect(lambda: analysis_page.make_heatmap_plot(self))
        # self.show_cor_matrix.clicked.connect(lambda: analysis_page.display_cor_mat(self))

        # self.make_scatter_plot.clicked.connect(lambda: analysis_page.create_scatter_cor_plot(self))



        # self.startdt_check_diurnal.stateChanged.connect(lambda: analysis_page.dirunal_start_end(self))
        # self.startdt_check_anual.stateChanged.connect(lambda: analysis_page.anual_start_end(self))
        # self.startdt_check_custom.stateChanged.connect(lambda: analysis_page.custom_start_end(self))

        # # =============================================================================
        # # GUI settings
        # # =============================================================================
        gui_settings_page._setup_triggers(self)


    # =============================================================================
    # Cross-page helpers     
    # =============================================================================
    
    def update_all_obstype_spinners(self):
        """ Update all spinners in the gui that reflect present obstypes."""
        
        if self.Dataset.df.empty:
            return
        present_obstypes = self.Dataset._get_present_obstypes()
        
        #update spinners
        #TODO extend list !!!!
        to_reset_spinners = [self.obstype_spinner]         
        for spinner in to_reset_spinners:
            spinner.clear()
            spinner.addItems(present_obstypes)



    # =============================================================================
    # Helpers
    # =============================================================================
    # def get_val(self, data_func_return):

    #     if not data_func_return[1]:
    #         self.error_dialog.showMessage(data_func_return[2])
    #     return data_func_return[0]





def main():

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



