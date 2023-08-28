#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 27 16:17:53 2023

@author: thoverga
"""

# # DEBUG
# import sys
# sys.path.insert(0, '/home/thoverga/Documents/VLINDER_github/MetObs_toolkit/metobs_toolkit')
# import metobs_toolkit
# # END DEBUG

import sys, os
import pandas as pd
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QDialog, QDialogButtonBox
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5 import QtCore
from metobs_gui.errors import Error, Notification
from PyQt5.uic import loadUi
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar


from metobs_gui.tlk_scripts import combine_to_obsspace

import metobs_gui.path_handler as path_handler
from metobs_gui.pandasmodel import DataFrameModel
import metobs_gui.template_func as template_func

# =============================================================================
# Notes to myself!
# =============================================================================

# Keep in mind to store the new widgets (the extra windows) as an attribute of self (the parent)!!
# if you do not do this, but store it in a variable than the windown will only exist as long as the variable exists.... so it will be destroyed if not saved as attribute of the parent!




# =============================================================================
# High order functions
# =============================================================================

def _show_metadf(MW):
    # check if dataset is available
    if MW.dataset is None:
        Error('Show dataset', 'There is no dataset.')
        return
    # create a seperate window containing the metadf
    window = MergeWindow(MW.dataset.metadf, mode='metadf')
    window.show()

def _show_obsspace(MW):
    # check if dataset is available
    if MW.dataset is None:
        Error('Show dataset', 'There is no dataset.')
        return

    combdf, _cont, _msg = combine_to_obsspace(MW.dataset)
    if not _cont:
        Error(_msg[0], _msg[1])
        return

    # create a seperate window containing the dataframe
    window = MergeWindow(combdf, mode='mergedf')
    window.show()

def _show_timeseries(MW):
    # check if dataset is available
    if MW.dataset is None:
        Error('Show dataset', 'There is no dataset.')
        return

    # create a seperate window containing the plot
    plot_window = DatasetTimeSeriesWindow(dataset = MW.dataset)
    plot_window.make_plot()
    plot_window.show()

def _show_modeldata_dataframe(MW):
    if MW.modeldata is None:
        Error('Show modeldata', 'There is no Modeldata.')
        return
    if MW.modeldata.df.empty:
        Error('Show modeldata', 'The Modeldata is empty.')
        return

    # create a seperate window containing the metadf
    window = MergeWindow(MW.modeldata.df, mode='metadf')
    window.show()

def _show_missing_obs_df(MW):
    # check if dataset is available
    if MW.dataset is None:
        Error('Show dataset', 'There is no dataset.')
        return
    # create a seperate window containing the metadf
    df = MW.dataset.missing_obs.series.to_frame()
    window = MergeWindow(df, mode='missing_obsdf')
    window.show()

def _show_missing_obs_fill_df(MW):
    # check if dataset is available
    if MW.dataset is None:
        Error('Show dataset', 'There is no dataset.')
        return
    # create a seperate window containing the metadf
    df = MW.dataset.missing_fill_df
    window = MergeWindow(df, mode='missing_obsdf')
    window.show()


def _show_gaps_df(MW):
    # check if dataset is available
    if MW.dataset is None:
        Error('Show dataset', 'There is no dataset.')
        return
    # create a seperate window containing the metadf
    df = MW.dataset.get_gaps_df()
    window = MergeWindow(df, mode='gapsdf')
    window.show()

def _show_gaps_fill_df(MW):
    # check if dataset is available
    if MW.dataset is None:
        Error('Show dataset', 'There is no dataset.')
        return
    # create a seperate window containing the metadf
    df = MW.dataset.gapfilldf
    window = MergeWindow(df, mode='gapsdf')
    window.show()



def _show_modeldata(MW):
    if MW.modeldata is None:
        Error('Show modeldata', 'There is no Modeldata.')
        return
    if MW.modeldata.df.empty:
        Error('Show modeldata', 'The Modeldata is empty.')
        return
    # create a seperate window containing the plot
    plot_window = ModeldataTimeSeriesWindow(dataset = MW.dataset, modeldata=MW.modeldata)
    plot_window.make_plot()
    plot_window.show()




# =============================================================================
# Matplotlib extension class
# =============================================================================
class timeseriesCanvas(FigureCanvasQTAgg):

    def __init__(self, dataset=None, modeldata=None, width=5, height=4, dpi=100):
        # Data objects
        self.dataset = dataset
        self.modeldata = modeldata
        # Figure object
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(timeseriesCanvas, self).__init__(fig)


    def set_dataset(self, dataset):
        self.dataset = dataset
    def set_modeldata(self, modeldata):
        self.modeldata = modeldata

    def create_toolbar(self):
        # create toolbar connectd to the canvas
        return NavigationToolbar(canvas=self)
    def _clear_axis(self):
        print('clear axes')
        self.axes.cla()
    # =============================================================================
    #     fill axes methods
    # =============================================================================
    def dataset_timeseriesplot(self, obstype='temp', colorby='name',
                       stationnames=None, show_outliers=True):


        self.axes = self.dataset.make_plot(stationnames=stationnames,
                                           obstype=obstype,
                                           colorby=colorby,
                                           starttime=None,
                                           endtime=None,
                                           _ax=self.axes,
                                           title=None,
                                           legend=False,
                                           show_outliers=show_outliers)
    def modeldata_timeseriesplot(self, add_obs=False, obstype_model='temp',
                                 obstype_dataset='temp', stationnames=None,
                                 show_outliers=True):

        if add_obs:
            dataset = self.dataset
        else:
            dataset=None

        # update this
        self.axes = self.modeldata.make_plot(obstype_model=obstype_model,
                                             dataset = dataset,
                                             obstype_dataset=obstype_dataset,
                                             stationnames=stationnames,
                                             starttime=None,
                                             endtime=None,
                                             title=None,
                                             show_outliers=show_outliers,
                                             show_filled=True,
                                             legend=True,
                                             _ax=self.axes)


# =============================================================================
# Figure windows
# =============================================================================



class DatasetTimeSeriesWindow(QMainWindow):
    """ Creates new window """

    def __init__(self, dataset):
        super().__init__()
        loadUi(os.path.join(path_handler.GUI_dir,'fig_window.ui'), self)

        # setup canvas
        self.canvas=timeseriesCanvas(dataset=dataset, modeldata=None)

        #init widgets
        self.init_widgets(dataset)

        # triggers
        self.update_plot_box.clicked.connect(lambda: self.update_plot())


    def init_widgets(self, dataset):
        self.select_colorby.clear()
        self.select_colorby.addItems(['name','label'])

        stationnames = dataset.df.index.get_level_values('name').unique().to_list()
        stationnames.insert(0, 'ALL')
        self.select_subset.clear()
        self.select_subset.addItems(stationnames)

        self.select_obstype.clear()
        self.select_obstype.addItems(dataset.df.columns.to_list())



    def update_plot(self):
        obstype =self.select_obstype.currentText()
        subset=self.select_subset.currentText()
        colorby = self.select_colorby.currentText()
        show_outliers = self.select_show_outliers.isChecked()

        if subset=='ALL':
            stationnames=None
        else:
            stationnames = [subset]

        self.canvas._clear_axis()
        self.canvas.dataset_timeseriesplot(obstype=obstype,
                                   colorby=colorby,
                                   stationnames=stationnames,
                                   show_outliers=show_outliers)
        self.canvas.draw()


    def make_plot(self):
        self.canvas.dataset_timeseriesplot()
        self.vert_layout.addWidget(self.canvas.create_toolbar())
        self.vert_layout.addWidget(self.canvas)


# =============================================================================
# TImeseries for modeldata
# =============================================================================




class ModeldataTimeSeriesWindow(QMainWindow):
    """ Creates new window """

    def __init__(self, dataset, modeldata):
        super().__init__()
        loadUi(os.path.join(path_handler.GUI_dir,'modeldata_fig_window.ui'), self)

        if dataset is None:
            self.obs_available=False
        else:
            self.obs_available=True

        # setup canvas
        self.canvas=timeseriesCanvas(dataset=dataset, modeldata=modeldata)

        #init widgets
        self.init_widgets(dataset, modeldata)

        # triggers
        self.update_plot_box.clicked.connect(lambda: self.update_plot())
        self.add_dataset.clicked.connect(lambda: self.setup_dataset())



    def init_widgets(self, dataset, modeldata):
        stationnames = modeldata.df.index.get_level_values('name').unique().to_list()
        stationnames.insert(0, 'ALL')
        self.select_subset.clear()
        self.select_subset.addItems(stationnames)

        self.select_obstype.clear()
        self.select_obstype.addItems(modeldata.df.columns.to_list())

        if not dataset is None:
            obstypes_dataset = dataset.df.columns.to_list()
        else:
            obstypes_dataset = []
        self.select_obstype_dataset.addItems(obstypes_dataset)

        if not self.obs_available:
            self.add_dataset.setEnabled(False)

        self.setup_dataset()

    def setup_dataset(self):
        if self.add_dataset.isChecked():
            self.select_obstype_dataset.setEnabled(True)
            self.select_show_outliers.setEnabled(True)
        else:
            self.select_obstype_dataset.setEnabled(False)
            self.select_show_outliers.setEnabled(False)




    def update_plot(self):
        obstype_model=self.select_obstype.currentText()
        subset=self.select_subset.currentText()
        show_outliers = self.select_show_outliers.isChecked()

        if self.add_dataset.isChecked():
            add_obs=True
            obstype_dataset = self.select_obstype_dataset.currentText()
        else:
            add_obs=False
            obstype_dataset=None

        if subset=='ALL':
            stationnames=None
        else:
            stationnames = [subset]

        self.canvas._clear_axis()
        self.canvas.modeldata_timeseriesplot(add_obs=add_obs,
                                             obstype_model=obstype_model,
                                             obstype_dataset=obstype_dataset,
                                             stationnames=stationnames,
                                             show_outliers=show_outliers)
        self.canvas.draw()





    def make_plot(self):
        self.canvas.modeldata_timeseriesplot() #create mpl axes plot
        self.vert_layout.addWidget(self.canvas.create_toolbar())
        self.vert_layout.addWidget(self.canvas)



# =============================================================================
# Analysis cycles
# =============================================================================




class BasicWindow(QMainWindow):
    """ Creates new window """

    def __init__(self, ax):
        super().__init__()
        loadUi(os.path.join(path_handler.GUI_dir,'basic_fig.ui'), self)

        self.fig = ax.get_figure()

        self.canvas=FigureCanvasQTAgg(self.fig)
        self.toolbar = NavigationToolbar(canvas=self.canvas)


    def make_plot(self):
        self.vert_layout.addWidget(self.toolbar)
        self.vert_layout.addWidget(self.canvas)



def make_a_cycle_plot(MW):
    # create a seperate window containing the plot
    MW.cyclewindow = BasicWindow(MW.cycle_ax)
    MW.cyclewindow.make_plot()
    MW.cyclewindow.show()



def show_cycle_stats_df(MW):
    # check if stats is available
    if MW.cycle_stats is None:
        Error('Show cycle statistics', 'There is no cycle.')
        return
    # create a seperate window containing the metadf
    MW.testwindow = MergeWindow(MW.cycle_stats, mode='cycle')
    MW.testwindow.show()

def make_a_heatmap_plot(MW):
    # check if ax is available
    if MW.heatmap_ax is None:
        Error('Show heatmap figure', 'There is no heatmap figure generated.')
        return
    MW.heatwindow = BasicWindow(MW.heatmap_ax)
    MW.heatwindow.make_plot()
    MW.heatwindow.show()

def show_cor_matix_df(MW, cordf):
    if cordf.empty:
        Error('Show correlation matrix', 'There is data to show.')
        return

    # create a seperate window containing the metadf
    MW.testwindow = MergeWindow(cordf, mode='cycle')
    MW.testwindow.show()






# =============================================================================
# Table windows
# =============================================================================

class MergeWindow(QMainWindow):
    """ Creates new window """

    def __init__(self, df, mode='mergedf'):
        super().__init__()
        loadUi(os.path.join(path_handler.GUI_dir,'tabular_data_window.ui'), self)

        # Define data attributes
        self.df = df.reset_index()
        self.combmodel = DataFrameModel()
        self.combmodel.setDataFrame(self.df)
        self.merge_table.setModel(self.combmodel)

        self.mode = mode

        # initialise values
        self.set_obstype_subsetting_spinner()


        # Triggers
        self.subset_merged_obstype.activated.connect(lambda: self.subset_comb_table())

    def trigger_update(self):
        self.subset_comb_table()

    def set_obstype_subsetting_spinner(self):
        # if mode is metadata --> disable spinner
        if ((self.mode == 'metadf') | (self.mode == 'missing_obsdf') | (self.mode == 'gapsdf') | (self.mode == 'cycle')):
            self.subset_merged_obstype.setEnabled(False)
            return

        # check if dataset is available, if not use all possible obstypes
        all_obstypes = list(template_func.Obs_map_values.keys())
        if self.df.empty:
            obstypes = all_obstypes
        else:
            if self.mode == 'mergedf':
                available_obstypes = self.df['obstype'].unique()
                obstypes = [obstype for obstype in all_obstypes if obstype in available_obstypes]
            else:
                obstypes = [obstype for obstype in all_obstypes if obstype in self.df.columns]

        # insert 'NO SELECTION'
        if not 'NO SELECTION' in obstypes:
            obstypes.insert(0,'NO SELECTION')

        # Update spinner
        self.subset_merged_obstype.clear()
        self.subset_merged_obstype.addItems(obstypes)
        self.subset_merged_obstype.setCurrentText('NO SELECTION')

    def subset_comb_table(self):
        # only if the combdf dataframe is not empty, and
        #  an obstype is selected, and the obstype is in the dataframe
        obstype = self.subset_merged_obstype.currentText()

        # comb_df = self.df.reset_index()
        if self.mode == 'mergedf':
            if ((not self.df.empty) &
                (obstype != 'NO SELECTION')):
                # subset model
                self.combmodel.setDataFrame(self.df[self.df['obstype'] == obstype])

        else:
            if ((not self.df.empty) &
                (obstype != 'NO SELECTION')
                (obstype in self.df.columns)):

                subsetcols = ['name', 'datetime', obstype, obstype+'_final_label']
                # update model
                self.combmodel.setDataFrame(self.df[subsetcols])


# =============================================================================
# HTML window (from file)
# =============================================================================


def _show_spatial_html(MW, html_path):
    print('hier')
    MW.html = HtmlWindow()
    print('nu')
    MW.html.feed_html(html_path)
    print('done')


class HtmlWindow(QDialog):
    """ Creates new window """

    def __init__(self):
        super().__init__()
        loadUi('/home/thoverga/Documents/VLINDER_github/MetObs_GUI/metobs_gui/html_map.ui', self)

    def feed_html(self, html_path):
        self.display_2.load(QtCore.QUrl().fromLocalFile(html_path))







