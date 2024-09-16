#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug  3 10:31:13 2023

@author: thoverga
"""


import os
import sys
from pathlib import Path
import logging
from metobs_toolkit import rootlog as toolkit_logger

from PyQt5.QtWidgets import QMainWindow, QApplication, QPlainTextEdit
from PyQt5.uic import loadUi




lib_folder = Path(__file__).resolve().parents[1]

toolkit_folder =os.path.join(str(lib_folder.parents[0]), 'MetObs_toolkit')

sys.path.insert(0,str(toolkit_folder))
sys.path.insert(0,str(lib_folder))


ui_file = '/home/thoverga/Documents/VLINDER_github/MetObs_GUI/development/test.ui'


import metobs_toolkit
#%%

class QPlainTextEditLogger(logging.Handler):
    def __init__(self, connect_widget):
        super(QPlainTextEditLogger, self).__init__()

        self.widget = connect_widget
        self.widget.setReadOnly(True)

        #setup format of handler
        self.setLevel(logging.DEBUG)
        # # Create a Formatter for formatting the log messages
        logger_formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
        self.setFormatter(logger_formatter)



    def emit(self, record):
        msg = self.format(record)
        self.widget.appendPlainText(msg)

    def write(self, m):
        pass

#%%


from metobs_toolkit import rootlog as toolkit_logger

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        # Load gui widgets
        loadUi(ui_file,
               self) #open the ui file

        # Set up logging to use your widget as a handler
        log_handler = QPlainTextEditLogger(self.textlog)
        # logging.getLogger().addHandler(log_handler)
        toolkit_logger.addHandler(log_handler)

        self.button.clicked.connect(lambda: self.make_logs()) #browse datafile

    def make_logs(self):
        test = metobs_toolkit.Dataset()





if __name__ == '__main__':
    # matplotlib.use('Qt5Agg') #in protector because server runners do not support this, when this module is imported from the __init__
    app=QApplication(sys.argv)
    # main()

    mainwindow = MainWindow()
    mainwindow.show()
    # widget = main()
    # widget.show()
    sys.exit(app.exec_())