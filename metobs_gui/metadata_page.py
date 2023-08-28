#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug  4 09:43:52 2023

@author: thoverga
"""

import os

from metobs_gui.extra_windows import _show_metadf, _show_spatial_html


import metobs_gui.tlk_scripts as tlk_scripts
import metobs_gui.path_handler as path_handler

from metobs_gui.errors import Error, Notification



# =============================================================================
# init page
# =============================================================================


def init_metadata_page(MW):
    # add all landcover maps
    MW.lc_map.addItems(['worldcover'])




# =============================================================================
# triggers
# =============================================================================


def get_altitude(MW):
    # is metadata sufficient
    _cont = _coordinates_available(MW)
    if not _cont:
        return

    # start prompting
    MW.prompt_metadata.appendPlainText('\n---- Get Altitude from GEE ---- \n')

    # extract data
    _cont, terminal, _msg = tlk_scripts.get_altitude(MW.dataset)
    if not _cont:
        Error(_msg[0], _msg[1])
        return
    # write output to prompt
    for line in terminal:
        MW.prompt_metadata.appendPlainText(line)

    MW.prompt_metadata.appendPlainText('\n---- Get Altitude from GEE ---> Done! ---- \n')

    Notification('Altitude is added to the metadf.')
    return

def get_lcz(MW):
    # is metadata sufficient
    _cont = _coordinates_available(MW)
    if not _cont:
        return

    # start prompting
    MW.prompt_metadata.appendPlainText('\n---- Get LCZ from GEE ---- \n')

    _cont, terminal, _msg = tlk_scripts.get_lcz(MW.dataset)
    if not _cont:
        Error(_msg[0], _msg[1])
        return
    # write output to prompt
    for line in terminal:
        MW.prompt_metadata.appendPlainText(line)

    MW.prompt_metadata.appendPlainText('\n---- Get LCZ from GEE ---> Done! ---- \n')
    Notification('LCZ is added to the metadf.')
    return



def get_landcover(MW):
    # is metadata sufficient
    _cont = _coordinates_available(MW)
    if not _cont:
        return

    # extract arguments
    buf_radius = int(MW.lc_radius.value())
    agg = True if MW.lc_agg.isChecked() else False
    mapname = str(MW.lc_map.currentText())

    MW.prompt_metadata.appendPlainText(f'\n---- Get landcover ({buf_radius}m) from GEE ---- \n')

    _cont, terminal, _msg = tlk_scripts.get_landcover(dataset = MW.dataset,
                                                buffers = [buf_radius],
                                                aggbool=agg,
                                                gee_map=mapname)
    if not _cont:
        Error(_msg[0], _msg[1])
        return

    # write output to prompt
    for line in terminal:
        MW.prompt_metadata.appendPlainText(line)

    MW.prompt_metadata.appendPlainText(f'\n---- Get landcover ({buf_radius}m) from GEE ---> Done! ---- \n')
    Notification(f'landcover for buffer of {buf_radius}m is added to the metadf.')


def submit_gee_code(MW):
    Error('NOG te implementern', 'Laat thomas weten als je deze error krijgt! Normaal gezien moet er een browserwindow openen voor te verificeren.')





def preview_metadata(MW):
    _show_metadf(MW)






def spatial_plot(MW):

    # Check if dataset and coordinates exist
    if not _coordinates_available(MW):
        return

    MW.prompt_metadata.appendPlainText(f'\n---- Create interactive map ---- \n')

    # Create path to save the html file
    # save in the TMP dir
    filename = 'metadata_html.html'
    filepath = os.path.join(path_handler.TMP_dir, filename)

    # remove the file if it already exists
    if path_handler.file_exist(filepath):
        os.remove(filepath)

    # create the html map
    print('A')
    _cont, terminal, _msg = tlk_scripts.make_html_gee_map(dataset=MW.dataset,
                                                          html_path=filepath)

    print('B')
    if not _cont:
        Error(_msg[0], _msg[1])
        return

    # write output to prompt
    for line in terminal:
        MW.prompt_metadata.appendPlainText(line)

    MW.prompt_metadata.appendPlainText(f'\n---- Create interactive map ---> Done! ---- \n')
    print('C')
    _show_spatial_html(MW, filepath)
    print('D')
    MW.html.show()
    print('E')





# =============================================================================
# helpers
# =============================================================================

def _coordinates_available(MW):
    # check if dataset is available
    if MW.dataset is None:
        Error('Empty dataset', 'This action could not be performed because there is no dataset.')
        return False

    # check if coordinate columns are available
    if not ('lat' in MW.dataset.metadf.columns):
        Error('Missing coordinates', f'This action could not be performed because there is no latitude column in the metadf.\n {MW.dataset.metadf}')
        return False

    if not ('lon' in MW.dataset.metadf.columns):
        Error('Missing coordinates', f'This action could not be performed because there is no latitude column in the metadf.\n {MW.dataset.metadf}')
        return False

    # check if the lat values are not all nan
    if MW.dataset.metadf['lat'].isnull().all():
        Error('Missing coordinates', f'This action could not be performed because there is no latitude values found in the metadf. \n {MW.dataset.metadf}')
        return False
    if MW.dataset.metadf['lon'].isnull().all():
        Error('Missing coordinates', f'This action could not be performed because there is no longitude values found in the metadf. \n {MW.dataset.metadf}')
        return False

    # check if the lat and lon values are within a spefic range
    if (MW.dataset.metadf['lat'].min() <= -90.) | (MW.dataset.metadf['lat'].max() > 90.):
        Error('Fault latitude', f'This action could not be performed because the latitudes are not within [-90, 90]. \n {MW.dataset.metadf}')
        return False
    # check if the lat and lon values are within a spefic range
    if (MW.dataset.metadf['lon'].min() <= -180.) | (MW.dataset.metadf['lat'].max() > 180.):
        Error('Fault longitude', f'This action could not be performed because the longitude are not within [-180, 180]. \n {MW.dataset.metadf}')
        return False

    return True





