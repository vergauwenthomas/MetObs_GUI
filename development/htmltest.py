#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug  4 16:20:40 2023

@author: thoverga
"""

from PyQt5 import QtCore, QtGui, QtWidgets,QtWebEngineWidgets
import os
from PyQt5.uic import loadUi

# html_path ='/home/thoverga/Documents/VLINDER_github/MetObs_GUI/development/dummy.html'
# htlm_path = '/home/thoverga/mymap.html'


# class HtmlWindow(object):


#     def setupUi(self, Dialog, dialogname, html_path):
#         Dialog.setObjectName(dialogname)
#         Dialog.resize(400, 300)
#         self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
#         self.verticalLayout.setObjectName("verticalLayout")
#         self.centralwidget = QtWidgets.QWidget(Dialog)
#         self.centralwidget.setObjectName("centralwidget")
#         self.webEngineView = QtWebEngineWidgets.QWebEngineView(self.centralwidget)
#         self.webEngineView.load(QtCore.QUrl().fromLocalFile(html_path))
#         self.verticalLayout.addWidget(self.webEngineView)
#         self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
#         self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
#         self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
#         self.buttonBox.setObjectName("buttonBox")
#         self.verticalLayout.addWidget(self.buttonBox)
#         self.retranslateUi(Dialog)
#         self.buttonBox.accepted.connect(Dialog.accept)
#         self.buttonBox.rejected.connect(Dialog.reject)
#         QtCore.QMetaObject.connectSlotsByName(Dialog)

#     def retranslateUi(self, Dialog):
#         _translate = QtCore.QCoreApplication.translate
#         Dialog.setWindowTitle(_translate("Dialog", "Dialog"))




def _show_spatial_html(html_path):
    print('maken')
    html = HtmlWindow(html_path)
    html.show()
    print('show')


class HtmlWindow(QtWidgets.QMainWindow):
    """ Creates new window """

    def __init__(self):
        super().__init__()
        loadUi('/home/thoverga/Documents/VLINDER_github/MetObs_GUI/metobs_gui/html.ui', self)

    def feed_html(self, html_path):
        self.display.load(QtCore.QUrl().fromLocalFile(html_path))

        # self.verticalLayout.addWidget(self.webEngineView)
from time import sleep


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.test = HtmlWindow()
        self.test.feed_html('/home/thoverga/mymap.html')
        self.test.show()



if __name__ == "__main__":
    import sys
    # app = QtWidgets.QApplication(sys.argv)
    # Dialog = QtWidgets.QDialog()
    # ui = HtmlWindow()
    # ui.setupUi(Dialog, 'dummy test name', '/home/thoverga/mymap.html' )
    # Dialog.show()
    # sys.exit(app.exec_())


    app=QtWidgets.QApplication(sys.argv)
    # main()

    mainwindow = MainWindow()
    mainwindow.show()
    # widget = main()
    # widget.show()
    sys.exit(app.exec_())




