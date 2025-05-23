#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 30 14:26:57 2023

@author: thoverga
"""
import traceback
from PyQt5.QtWidgets import QMessageBox

class Error():
    def __init__(self, message, informative_text=None):
        # msg = super().__init__()

        self.msg = QMessageBox()
        self.msg.setIcon(QMessageBox.Critical)
        self.msg.setText(message)
        if informative_text is None:
            self.msg.setInformativeText(traceback.format_exc())
        else:
            self.msg.setInformativeText(informative_text)
        self.msg.setWindowTitle("Error")
        self.msg.exec_()




class Notification():
    def __init__(self, message):
        self.msgBox = QMessageBox()
        self.msgBox.setIcon(QMessageBox.Information)
        self.msgBox.setText(message)
        self.msgBox.setWindowTitle("Information")
        self.msgBox.setStandardButtons(QMessageBox.Ok)
        self.msgBox.exec_()
