#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 13 09:36:43 2023

@author: thoverga
"""
import sys, os
from PyQt5 import QtWidgets
from PyQt5.uic import loadUi
import logging
import metobs_gui.path_handler as path_handler



# Uncomment below for terminal log messages
# logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(name)s - %(levelname)s - %(message)s')
#%%

# add a handler to the metobs_TOOLKIT logger to stream directly to a widget


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



#How to use:

# Set up logging to use your widget as a handler
# log_handler = QPlainTextEditLogger(self.textlog)
# toolkit_logger.addHandler(log_handler)

# where self.textlog is a plaintextedit widget, and toolkit_logger is a logging instance.


#%%





class QTextEditLogger(logging.Handler):
    def __init__(self, parent):
        super().__init__()
        self.widget = QtWidgets.QPlainTextEdit(parent)
        self.widget.setReadOnly(True)

    def emit(self, record):
        msg = self.format(record)
        self.widget.appendPlainText(msg)


class MyDialog(QtWidgets.QDialog, QtWidgets.QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)

        logTextBox = QTextEditLogger(self)
        # You can format what is printed to text box
        logTextBox.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logging.getLogger().addHandler(logTextBox)
        # You can control the logging level
        logging.getLogger().setLevel(logging.DEBUG)

        # self._button = QtWidgets.QPushButton(self)
        # self._button.setText('Test Me')

        layout = QtWidgets.QVBoxLayout()
        # Add the new logging box widget to the layout
        layout.addWidget(logTextBox.widget)
        # layout.addWidget(self._button)
        self.setLayout(layout)

        # Connect signal to slot
        # self._button.clicked.connect(self.test)

    # def test(self):
    #     logging.debug('damn, a bug')
    #     logging.info('something to remember')
    #     logging.warning('that\'s not right')
    #     logging.error('foobar')


