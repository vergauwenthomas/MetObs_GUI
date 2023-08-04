#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 20 09:47:48 2023

@author: thoverga
"""

# command: designer in terminal to open the desinger tool



import os, sys
from pathlib import Path
import matplotlib

from metobs_toolkit import loggers as toolkit_logger

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication, QFileDialog, QMainWindow
from PyQt5.QtWidgets import QScrollArea, QTabWidget
from PyQt5.uic import loadUi

import pandas as pd
import pytz

import metobs_gui.data_func as data_func
import metobs_gui.template_func as template_func
import metobs_gui.path_handler as path_handler
import metobs_gui.tlk_scripts as tlk_scripts

from metobs_gui.json_save_func import get_saved_vals, update_json_file
from metobs_gui.pandasmodel import DataFrameModel

from metobs_gui.errors import Error, Notification
from metobs_gui.extra_windows import MergeWindow, TimeSeriesWindow
import metobs_gui.log_displayer as log_displayer


import metobs_gui.template_page as template_page
import metobs_gui.import_data_page as import_page
import metobs_gui.metadata_page as metadata_page


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        # Load gui widgets
        loadUi(os.path.join(path_handler.GUI_dir,'last_attempt.ui'),
               self) #open the ui file

        # -------- Information to pass beween different triggers ----------
        self.dataset = None #the vlindertoolkit dataset instance

        self.long_storage = {} #will read the json file to store info over mulitple settings
        self.session = {} #store info during one session

        # P1 INIT
        template_page.init_template_page(self)

        # P2 INIT
        import_page.init_import_page(self)

        # P3 INIT
        metadata_page.init_metadata_page(self)

        # P2 ------------------------
        # self.template_dict = None #dict; all available templname : templpath
        # self.default_settings = tlk_scripts.get_default_settings()


        # ------- Setup (widgets and default values) ---------------

        # Setup error message dialog
        self.error_dialog = QtWidgets.QErrorMessage(self)


        # setup metobs toolkit log handles to stream to prompts
        # Setup the logger handle to stream to the prompt
        input_page_log_handler = log_displayer.QPlainTextEditLogger(self.prompt) #to prompt on input page
        metadata_page_log_handler = log_displayer.QPlainTextEditLogger(self.prompt_metadata) #to prompt on input page
        toolkit_logger.addHandler(input_page_log_handler)
        toolkit_logger.addHandler(metadata_page_log_handler)



        # link dfmodels to tables
        self.templmodel = DataFrameModel()
        self.table.setModel(self.templmodel)


        # ------- Callbacks (triggers) ------------


        # =============================================================================
        # Windget links
        # =============================================================================
        self.data_file_T.textChanged.connect(self.data_file_T_2.setText) #link them
        self.metadata_file_T.textChanged.connect(self.metadata_file_T_2.setText) #link them







        # =============================================================================
        # Mapping tab
        # =============================================================================
        self.Browse_data_B.clicked.connect(lambda: template_page.browsefiles_data(self)) #browse datafile
        self.Browse_metadata_B.clicked.connect(lambda: template_page.browsefiles_metadata(self)) #browse metadatafile
        # save paths when selected
        self.save_data_path.clicked.connect(lambda: template_page.save_path(
                                                                MW=self,
                                                                savebool=self.save_data_path.isChecked(),
                                                                savekey='data_file_path',
                                                                saveval=self.data_file_T.text()))
        self.save_metadata_path.clicked.connect(lambda: template_page.save_path(
                                                                MW=self,
                                                                savebool=self.save_metadata_path.isChecked(),
                                                                savekey='metadata_file_path',
                                                                saveval=self.metadata_file_T.text()))

        self.browse_format.currentTextChanged.connect(lambda: template_page.enable_format_widgets(self))

        # initiate the start mapping module
        self.start_mapping_B.clicked.connect(lambda: template_page.prepare_for_mapping(self))

        # construnct the mappindict
        self.build_B.clicked.connect(lambda: template_page.build_template(self))

        # save template
        self.save_template.clicked.connect(lambda: template_page.save_template_call(self))

        # display df's
        self.preview_data.clicked.connect(lambda: template_page.show_data_head(self))
        self.preview_metadata.clicked.connect(lambda: template_page.show_metadata_head(self))
        self.view_template.clicked.connect(lambda: template_page.show_template(self))


        # =============================================================================
        # Import data tab
        # =============================================================================
        self.Browse_data_B_2.clicked.connect(lambda: import_page.browsefiles_data(self)) #browse datafile
        self.Browse_metadata_B_2.clicked.connect(lambda: import_page.browsefiles_metadata(self)) #browse metadatafile
        self.Browse_specific_temp.clicked.connect(lambda: import_page.browsefiles_templatefile(self)) #browse template
        self.pkl_browser.clicked.connect(lambda: import_page.browsefiles_pklfile(self)) #browse pkl file


        self.use_specific_temp.clicked.connect(lambda: import_page.setup_use_specific_temp(self))
        self.use_pkl.clicked.connect(lambda: import_page.setup_use_input_pkl(self))
        self.freq_simpl.clicked.connect(lambda: import_page.setup_freq_simplification(self))
        self.sync_obs.clicked.connect(lambda: import_page.setup_syncronize(self))
        self.use_origin.clicked.connect(lambda: import_page.setup_origin(self))
        self.resample.clicked.connect(lambda: import_page.setup_resample_timeres(self))

        self.pkl_path_save.clicked.connect(lambda: import_page.save_input_pkl_path(self))


        self.make_dataset.clicked.connect(lambda: import_page.make_dataset(self))

        self.get_info.clicked.connect(lambda: import_page.show_info(self))
        self.show_dataset.clicked.connect(lambda: import_page.make_obsspace(self))
        self.show_metadata.clicked.connect(lambda: import_page.show_metadf(self))
        self.plot_dataset.clicked.connect(lambda: import_page.make_dataset_plot(self))

        self.save_pkl_B.clicked.connect(lambda: import_page.save_dataset(self))


        # =============================================================================
        # Metadata tab
        # =============================================================================
        self.get_altitude.clicked.connect(lambda: metadata_page.get_altitude(self))
        self.get_lcz.clicked.connect(lambda: metadata_page.get_lcz(self))
        self.get_landcover.clicked.connect(lambda: metadata_page.get_landcover(self))

        self.gee_submit.clicked.connect(lambda: metadata_page.get_altitude(self))

        self.preview_metadata_2.clicked.connect(lambda: metadata_page.preview_metadata(self))
        self.spatial_plot.clicked.connect(lambda: metadata_page.spatial_plot(self))



#         # =============================================================================
#         # Quality control tab
#         # =============================================================================
#         self.plot_dataset.clicked.connect(lambda: self.make_figure())
#         self.apply_qc.clicked.connect(lambda: self.apply_qc_on_dataset())

#         # =============================================================================
#         # Gap filling tab
#         # =============================================================================


#         # =============================================================================
#         # Visualisation tab
#         # =============================================================================


#         # =============================================================================
#         # Meta data tab
#         # =============================================================================


#         # =============================================================================
#         # Model data tab
#         # =============================================================================


#         # =============================================================================
#         # Analysis tab
#         # =============================================================================




# # ------- Initialize --------------



#         # ----------P2 -----------------
#         # self.set_possible_templates() #load available dataset
#         # self.set_timezone_spinners()




#         tlk_scripts.set_qc_default_settings(self)


#         #----- Cleanup files ----------------
#         path_handler.clear_dir(path_handler.TMP_dir) #cleanup tmp folder

#%%
# =============================================================================
# Helpers
# =============================================================================
    def get_val(self, data_func_return):

        if not data_func_return[1]:
            self.error_dialog.showMessage(data_func_return[2])
        return data_func_return[0]


# =============================================================================
# Init values
# =============================================================================
    # def set_templ_map_val(self):
    #     # First try reading the datafile
    #     data_columns = self.read_datafiles(self.data_file_T.text())

    #     # Check if meta data is given, if so read the metadata columns
    #     if len(self.metadata_file_T.text()) > 2:
    #         metadata_columns = self.read_datafiles(self.metadata_file_T.text())
    #     else:
    #         metadata_columns = []

    #     # Set defaults appropriate
    #     template_func.set_templ_vals(self, data_columns, metadata_columns)



    # def set_datapaths_init(self):
    #     saved_vals = get_saved_vals()

    #     # set datafile path
    #     if 'data_file_path' in saved_vals:
    #         self.data_file_T.setText(str(saved_vals['data_file_path']))
    #         self.data_file_T_2.setText(str(saved_vals['data_file_path']))

    #     # set metadata file path
    #     if 'metadata_file_path' in saved_vals:
    #         self.metadata_file_T.setText(str(saved_vals['metadata_file_path']))
    #         self.metadata_file_T_2.setText(str(saved_vals['metadata_file_path']))


    # def set_possible_templates(self):
    #     templ_dict = template_func.get_all_templates()

    #     # remove .csv for presenting
    #     templ_names = [name.replace('.csv', '') for name in templ_dict.keys()]

    #     #update spinner
    #     self.select_temp.clear()
    #     self.select_temp.addItems(templ_names)

    #     # Store information to pass between triggers
    #     self.template_dict = templ_dict #dict templname : templpath




# =============================================================================
# Save values
# =============================================================================
    # def save_path(self, savebool, savekey, saveval):
    #     if savebool:
    #         savedict = {str(savekey): str(saveval)}
    #         update_json_file(savedict)

# =============================================================================
# Triggers
# =============================================================================

    def browsefiles_data_p2(self):
        fname=QFileDialog.getOpenFileName(self, 'Select data file', str(Path.home()))
        self.data_file_T_2.setText(fname[0])



    def browsefiles_metadata_p2(self):
        fname=QFileDialog.getOpenFileName(self, 'Select metadata file', str(Path.home()))
        self.metadata_file_T_2.setText(fname[0]) #update text



    def read_datafiles(self, filepath):
        if not path_handler.file_exist(filepath):
            Error(f'{filepath} is not a file.')
        _return = data_func.get_columns(filepath=filepath)
        columns = self.get_val(_return)

        return columns

    # def build_template(self):
    #     df = template_func.make_template_build(self)
    #     if df.empty:
    #         Error('There are no mapped values.')
    #     self.templmodel.setDataFrame(df)

    #     self.save_template.setEnabled(True) #enable the save button


    def save_template_call(self):
        # copy the template to the templates dir of the toolkit
        templ_loc = os.path.join(path_handler.TMP_dir, 'template.csv')

        filename = str(self.templatename.text())
        if not filename.endswith('.csv'):
            filename = filename + '.csv'

        target_loc = os.path.join(path_handler.CACHE_dir, filename)

        # check if templatefile already exists.
        if path_handler.file_exist(target_loc):
            Error(f'{target_loc} already exists! Change name of the template file.')
            return
        path_handler.copy_file(templ_loc, target_loc)

        self.set_possible_templates() #update widget

        Notification(f'Template ({filename}) is saved!')



    def make_tlk_dataset(self):
        self.dataset, self.merge_window.comb_df = tlk_scripts.load_dataset(self)

        # trigger update in seperate window
        self.merge_window.trigger_update()


    def apply_qc_on_dataset(self):
        self.merge_window.comb_df = tlk_scripts.apply_qualitycontrol(self)

        # trigger update in seperate window
        self.merge_window.trigger_update()

    def show_dataset_info(self):
        tlk_scripts.dataset_show_info(self)


    def create_dataset_window(self):

        self.merge_window.show()

# =============================================================================
# Testing
# =============================================================================


    def make_figure(self):
        self.tswindow.set_dataset(self.dataset)
        print(self.dataset)
        self.tswindow.make_plot()
        self.tswindow.show()


#%%

# =============================================================================
# Main and protector
# =============================================================================

def main():

    app=QApplication(sys.argv)

    mainwindow = MainWindow()
    mainwindow.show()
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
    # main()

    mainwindow = MainWindow()
    mainwindow.show()
    # widget = main()
    # widget.show()
    sys.exit(app.exec_())



