#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 28 13:30:48 2023

@author: thoverga
"""
from pathlib import Path
import pytz
from PyQt5.QtWidgets import QFileDialog, QComboBox


# from main import MainWindow as MW

from metobs_gui.json_save_func import get_saved_vals, update_json_file
from metobs_gui.data_func import readfile, isvalidfile, get_columns

# from metobs_gui.template_func import (not_mapable, Obs_map_values,
#                                       Dt_map_values, Meta_map_values,
#                                       set_datetime_defaults,
#                                       set_obstype_spinner_values,
#                                       set_obstype_units_defaults,
#                                       set_obstype_desc_defaults,
#                                       enable_all_boxes)

import metobs_gui.template_func as template_func

from metobs_gui.errors import Error, Notification
# =============================================================================
# default settings
# =============================================================================

# not_mapable=template_func.not

# Obs_map_values = {

#      'temp':{'units': ['K', 'Celcius'], 'description':'2mT'},
#      'radiation_temp':{'units': ['K', 'Celcius'], 'description':'Blackglobe temperature'},
#      'humidity':{'units': ['%'], 'description':'Relative humidity'},
#      'precip':{'units': ['l/hour x m²'], 'description':'Precipitation intensity'},
#      'precip_sum':{'units': ['l/m²', 'Celcius'], 'description':'Precipitation cumulated'},
#      'wind_speed':{'units': ['m/s'], 'description':'Average wind speed'},
#      'wind_gust':{'units': ['m/s'], 'description':'Wind gust'},
#      'wind_direction':{'units': ['°'], 'description':'Wind direction (from north CW)'},
#      'pressure':{'units': ['Pa'], 'description':'Air pressure'},
#      'pressure_at_sea_level':{'units': ['Pa'], 'description':'Pressure at sealevel'}

#     }

# Dt_map_values = {
#     'datetime': {'format':'%Y-%m-%d %H:%M:%S'},
#     '_date':{'format':'%Y-%m-%d'},
#     '_time':{'format':'%H:%M:%S'},
#     }

# Meta_map_values = {
#     'name': {'description': 'Station name/ID'},
#     'lat':{'description': 'Latitude'},
#     'lon':{'description': 'Longitude' },
#     'location':{'description': 'Location identifier'},
#     'call_name':{'description': 'Pseudo name of station'},
#     'network':{'description': 'Name of the network'}
#     }




# =============================================================================
# Initialise values
# =============================================================================
def init_template_page(MW):

    MW.session['mapping'] = {}

    # set data paths to saved files
    set_datapaths_init(MW)

    # set static spinners
    MW.browse_format.addItems(['long', 'wide', 'single-station'])
    MW.wide_obs_type.addItems(list(template_func.Obs_map_values.keys()))

    MW.timezone_spinner.addItems(pytz.common_timezones)
    MW.timezone_spinner.setCurrentText('UTC')

    # disable format options
    MW.wide_obs_type.setEnabled(False) # disable comboBox
    MW.wide_obs_units.setEnabled(False)
    MW.wide_obs_desc.setEnabled(False)
    MW.stationname.setEnabled(False)

    # disable all widgest for the mapping
    for box in _get_obstype_boxes(MW): box.setEnabled(False)
    for box in _get_metadata_boxes(MW): box.setEnabled(False)



def set_datapaths_init(MW):
    """
    Read saved values to look for a path for the data and metadata file.

    """
    saved_vals = get_saved_vals()

    # set datafile path
    if 'data_file_path' in saved_vals:
        MW.data_file_T.setText(str(saved_vals['data_file_path']))
        MW.data_file_T_2.setText(str(saved_vals['data_file_path']))

    # set metadata file path
    if 'metadata_file_path' in saved_vals:
        MW.metadata_file_T.setText(str(saved_vals['metadata_file_path']))
        MW.metadata_file_T_2.setText(str(saved_vals['metadata_file_path']))





# =============================================================================
# Triggers
# =============================================================================


# ----- browse files -------#

def browsefiles_data(MW):
    fname=QFileDialog.getOpenFileName(MW, 'Select data file', str(Path.home()))
    MW.data_file_T.setText(fname[0]) #update text

def browsefiles_metadata(MW):
    fname=QFileDialog.getOpenFileName(MW, 'Select metadata file', str(Path.home()))
    MW.metadata_file_T.setText(fname[0]) #update text

# ----- save paths --------
def save_path(MW, savebool, savekey, saveval):
    if savebool:
        savedict = {str(savekey): str(saveval)}
        update_json_file(savedict)

# ----- enable specific format settings --------
def enable_format_widgets(MW):
    dat_format = str(MW.browse_format.currentText())
    if dat_format == 'long':
        MW.wide_obs_type.setEnabled(False) # disable comboBox
        MW.wide_obs_units.setEnabled(False)
        MW.wide_obs_desc.setEnabled(False)
        MW.stationname.setEnabled(False)
    elif dat_format == 'wide':
        MW.wide_obs_type.setEnabled(True) # disable comboBox
        MW.wide_obs_units.setEnabled(True)
        MW.wide_obs_desc.setEnabled(True)
        MW.stationname.setEnabled(False)

    else:
        MW.wide_obs_type.setEnabled(False) # disable comboBox
        MW.wide_obs_units.setEnabled(False)
        MW.wide_obs_desc.setEnabled(False)
        MW.stationname.setEnabled(True)

    if MW.session['mapping']['started']:
        if (dat_format == 'long') | (dat_format == 'single-station'):
            # enable all
            for box in _get_obstype_boxes(MW): box.setEnabled(True)
            for box in _get_datetime_boxes(MW): box.setEnabled(True)
            if MW.use_metadata.isChecked():
                for box in _get_metadata_boxes(MW): box.setEnabled(True)
        else:
            for box in _get_obstype_boxes(MW): box.setEnabled(False)
            for box in _get_datetime_boxes(MW): box.setEnabled(True)
            if MW.use_metadata.isChecked():
                for box in _get_metadata_boxes(MW): box.setEnabled(True)



def prepare_for_mapping(MW):
    MW.session['mapping']['started'] = True

    dat_format = str(MW.browse_format.currentText())
    if (dat_format == 'long') | (dat_format == 'single-station'):
        # First try reading the datafile
        # 1. THe data file
        datafile = MW.data_file_T.text()
        valid, _msg = isvalidfile(datafile, filetype='.csv')
        if not valid:
            Error(_msg)
            return
        # Read columns
        df_cols = list(readfile(datafile, nrows=20)[0].columns)

        # Get the obstype spinners
        csv_columns = df_cols
        csv_columns.insert(0, template_func.not_mapable)

        # enable all obs boxes for colum mapping
        for box in _get_obstype_boxes(MW): box.setEnabled(True)
        for box in _get_datetime_boxes(MW): box.setEnabled(True)

        # set column and default values
        template_func.set_obstype_spinner_values(MW, csv_columns)
        template_func.set_time_spinner_values(MW, csv_columns)
        template_func.set_obstype_desc_defaults(MW)
        template_func.set_obstype_units_defaults(MW)
        template_func.set_datetime_defaults(MW)




    #2. The metadata
    if MW.use_metadata.isChecked():
        metadatafile = MW.metadata_file_T.text()
        valid, _msg = isvalidfile(metadatafile, filetype='.csv')
        if not valid:
            Error(_msg)
            return
        metadf_cols = list(readfile(metadatafile, nrows=20)[0].columns)
        metadf_cols.insert(0, template_func.not_mapable)

        # enable all obs boxes for colum mapping
        for box in _get_metadata_boxes(MW): box.setEnabled(True)

        # set column and default values
        template_func.set_metadata_spinner_values(MW, metadf_cols)




# =============================================================================
# helpers
# =============================================================================
def _get_obstype_boxes(MW):
    return [MW.temp_col_CB, MW.temp_units_CB, MW.temp_desc_T,
             MW.radtemp_col_CB, MW.radtemp_units_CB, MW.radtemp_desc_T,
             MW.hum_col_CB, MW.hum_units_CB, MW.hum_desc_T,
             MW.pre_col_CB, MW.pre_units_CB, MW.pre_desc_T,
             MW.pre_s_col_CB, MW.pre_s_units_CB, MW.pre_s_desc_T,
             MW.wind_col_CB, MW.wind_units_CB, MW.wind_desc_T,
             MW.gust_col_CB, MW.gust_units_CB, MW.gust_desc_T,
             MW.dir_col_CB, MW.dir_units_CB, MW.dir_desc_T,
             MW.p_col_CB, MW.p_units_CB, MW.p_desc_T,
             MW.psea_col_CB, MW.psea_units_CB, MW.psea_desc_T]

def _get_datetime_boxes(MW):
     return [MW.datetime_col_CB, MW.datetime_fmt_T,
             MW.date_col_CB, MW.date_fmt_T,
             MW.time_col_CB, MW.time_fmt_T]


def _get_metadata_boxes(MW):
    return [MW.name_col_CB, MW.lat_col_CB, MW.lon_col_CB,
            MW.loc_col_CB, MW.call_col_CB, MW.network_col_CB]


