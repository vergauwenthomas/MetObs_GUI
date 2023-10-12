#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 12 09:18:11 2023

@author: thoverga
"""

import os
from pathlib import Path

import matplotlib

from datetime import timedelta, datetime
from metobs_gui.path_handler import GUI_dir
import metobs_gui.path_handler as path_handler
from metobs_gui.tlk_scripts import make_interactive_spatial_map
from metobs_gui.errors import Error, Notification
from PyQt5.QtWidgets import QDialog, QMainWindow, QPushButton, QFileDialog
from PyQt5.uic import loadUi
from PyQt5 import QtCore




class InteractiveSpatialDialogWindow(QDialog):
    def __init__(self, dataset, default_filepath):
        super().__init__()
        loadUi(os.path.join(GUI_dir, 'interactive_spatial_map.ui'), self)
        self.dataset = dataset
        self.default_filepath = default_filepath
        self._cur_html = None

        # initialize widgets
        self._set_obstype_spinner()
        self._set_datetime_spinners()
        self._set_colormap_spinner()

        # setup triggers
        self.generate_map.clicked.connect(lambda: self.make_html())
        self.save_browse.clicked.connect(lambda: self.browse_to_save())
        self.save_but.clicked.connect(lambda: self.save_html())
        self.open_browse.clicked.connect(lambda: self.browse_to_open())
        self.open_but.clicked.connect(lambda: self.open_html())


    def get_arguments(self):
        argdict = {}
        argdict['obstype'] = str(self.obstypespinner.currentText())

        startstr = str(self.start_widg.textFromDateTime(self.start_widg.dateTime()))
        startdt = datetime.strptime(startstr, "%d/%m/%Y %H:%M")
        argdict['startdt'] = startdt

        endstr = str(self.end_widg.textFromDateTime(self.end_widg.dateTime()))
        enddt = datetime.strptime(endstr, "%d/%m/%Y %H:%M")
        argdict['enddt'] = enddt

        argdict['vmin'] = float(self.vmin_widg.value())
        argdict['vmax'] = float(self.vmax_widg.value())

        argdict['colormap'] = str(self.colmap_widg.currentText())
        argdict['radius'] = int(self.radius_widg.value())
        argdict['fill_alpha'] = float(self.alpha_widg.value())
        argdict['max_fps'] = int(self.fps_widg.value())

        argdict['outl_col'] = str(self.outl_col_widg.text())
        argdict['ok_col'] = str(self.ok_col_widg.text())
        argdict['gap_col'] = str(self.gap_col_widg.text())
        argdict['fill_col'] = str(self.fill_col_widg.text())

        return argdict


    def make_html(self):

        # scrape arguments from GUI
        argdict = self.get_arguments()

        #Create html file
        cont, msg = make_interactive_spatial_map(dataset=self.dataset,
                                                 obstype = argdict['obstype'],
                                                 save=True,
                                                 outputfile=self.default_filepath,
                                                 starttime=argdict['startdt'],
                                                 endtime=argdict['enddt'],
                                                 vmin=argdict['vmin'],
                                                 vmax=argdict['vmax'],
                                                 mpl_cmap_name=argdict['colormap'],
                                                 radius=argdict['radius'],
                                                 fill_alpha=argdict['fill_alpha'],
                                                 max_fps=argdict['max_fps'],
                                                 outlier_col=argdict['outl_col'],
                                                 ok_col=argdict['ok_col'],
                                                 gap_col=argdict['gap_col'],
                                                 fill_col=argdict['fill_col'])
        if not cont:
            Error(msg[0], msg[1])
            return


        # Feed file to webengine
        self.display_html(html_path=self.default_filepath)


    def display_html(self, html_path):
        self.webview.load(QtCore.QUrl().fromLocalFile(html_path))
        self._cur_html = html_path



    def _set_obstype_spinner(self):
        self.obstypespinner.clear()
        available_obstypes = list(self.dataset.df.columns)
        self.obstypespinner.addItems(available_obstypes)

    def _set_datetime_spinners(self):
        #startdt
        self.start_widg.clear()
        startdt = self.dataset.df.index.get_level_values('datetime').min()
        startdtstr = startdt.strftime("%d/%m/%Y %H:%M")
        self.start_widg.setDateTime(self.start_widg.dateTimeFromText(startdtstr))

        #enddt
        self.end_widg.clear()
        enddt = startdt + timedelta(days=1)
        enddtstr = enddt.strftime("%d/%m/%Y %H:%M")
        self.end_widg.setDateTime(self.end_widg.dateTimeFromText(enddtstr))

    def _set_colormap_spinner(self):
        possible_maps = ['magma', 'inferno', 'plasma', 'viridis',
                         'cividis', 'twilight', 'twilight_shifted','turbo']

        self.colmap_widg.clear()
        self.colmap_widg.addItems(possible_maps)
        self.colmap_widg.setCurrentText('viridis')

    def browse_to_save(self):
        fname=QFileDialog.getSaveFileName(self, 'Html file to save', str(Path.home()),
                                          "HTML (*.html)")
        filepath = fname[0]
        if not filepath.endswith('.html'):
            filepath += '.html'
        self.save_path.setText(filepath) #update text

    def save_html(self):
        cur_html_path = self._cur_html
        target_path = str(self.save_path.text())
        if not path_handler.parent_dir_exist(target_path):
            Error('Path error', f'The parent-folder of {target_path} is not found.')
            return
        path_handler.copy_file(filepath = cur_html_path,
                               targetpath=target_path)

        Notification(f'Html file saved at {target_path}!')
        return



    def browse_to_open(self):
        fname=QFileDialog.getOpenFileName(self, 'Select html file', str(Path.home()),
                                          "HTML (*.html)")
        self.open_path.setText(str(fname[0])) #update text

    def open_html(self):
        filepath = str(self.open_path.text())
        if not path_handler.file_exist(filepath):
            Error('file not found', f'The file: {filepath} is not found.')
            return
        try:
            self.display_html(filepath)
        except Exception as e:
            Error('HTML error', str(e))

        return



