#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main window of the MetObs GUI application.

@author: thoverga
"""

import os
import sys
import logging
import matplotlib

import metobs_toolkit

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
import metobs_gui.gui_settings_page as gui_settings_page

from metobs_gui.errors import Error


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        # Load gui widgets
        loadUi(
            os.path.join(path_handler.GUI_dir, 'qt_windows', 'mainwindow.ui'),
            self,
        )

        # -------- Information to pass between different triggers ----------
        self.Dataset = metobs_toolkit.Dataset()
        self._Dataset_imported = False

        # -----Setup GUI storage (long term: cache, and session term: temp) ----
        self.modeldata_temporar = None
        self.long_storage = {}
        self.session = {}

        path_handler._setup_cache_dir()
        path_handler._setup_temp_dir()

        # Page initializations
        try:
            template_page.init_page(self)
        except Exception as e:
            Error(f'Error initializing template page: {e}')

        try:
            import_page.init_page(self)
        except Exception as e:
            Error(f'Error initializing import page: {e}')

        try:
            gee_page.init_page(self)
        except Exception as e:
            Error(f'Error initializing GEE page: {e}')

        try:
            qc_page.init_qc_page(self)
        except Exception as e:
            Error(f'Error initializing QC page: {e}')

        try:
            gf_page.init_fill_page(self)
        except Exception as e:
            Error(f'Error initializing gap fill page: {e}')

        try:
            gui_settings_page._init_page(self)
        except Exception as e:
            Error(f'Error initializing settings page: {e}')

        # ------- Setup (widgets and default values) ---------------

        # Setup error message dialog
        self.error_dialog = QtWidgets.QErrorMessage(self)

        # Setup metobs toolkit log handler to stream to prompt widget
        input_page_log_handler = log_displayer.QPlainTextEditLogger(self.prompt)
        toolkit_logger = logging.getLogger('metobs_toolkit')
        toolkit_logger.addHandler(input_page_log_handler)

        # Link DataFrameModel to tables
        self.templmodel = DataFrameModel()
        self.table.setModel(self.templmodel)

        # =============================================================================
        # Widget cross links
        # =============================================================================
        self.data_file_T.textChanged.connect(self.data_file_T_2.setText)
        self.metadata_file_T.textChanged.connect(self.metadata_file_T_2.setText)

        self.use_data_box.clicked.connect(self.use_data_T_2.setCheckState)
        self.use_metadata_box.clicked.connect(self.use_metadata_2.setCheckState)

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
        """Reaction when a dataset is loaded."""
        try:
            present_obs = list(
                self.Dataset.df.index.get_level_values('obstype').unique()
            )
            obstype_spin_list = [
                self.obstype_spinner,
                self.fill_obstype,
                self.convert_outliers_trgs,
            ]

            for spin in obstype_spin_list:
                spin.clear()
                spin.addItems(present_obs)

            enable_list = [self.update_method_settings, self.convert_outliers]
            for widg in enable_list:
                widg.setEnabled(True)

            gf_page._react_dataset_loaded(self)

        except Exception as e:
            Error(f'Error reacting to dataset load: {e}')


def main():
    app = QApplication(sys.argv)
    mainwindow = MainWindow()
    mainwindow.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    matplotlib.use('Qt5Agg')
    main()
