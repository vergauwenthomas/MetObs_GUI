#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug  4 09:43:52 2023

@author: thoverga
"""

import os

# from metobs_gui.extra_windows import _show_metadf, _show_spatial_html


import metobs_gui.tlk_scripts as tlk_scripts
import metobs_gui.path_handler as path_handler
from metobs_gui.extra_windows import MetadataDialog, HtmlDialog
from metobs_gui.errors import Error, Notification



# =============================================================================
# init page
# =============================================================================


def init_metadata_page(MW):
    # add all landcover maps
    # MW.lc_map.addItems(['worldcover'])

    #initialize spinners
    setup_spinners(MW)
    



# =============================================================================
# Setup
# =============================================================================

def setup_spinners(MW):
    geedataset_names = list(MW.Dataset.gee_datasets.keys())
    
    MW.geedataset_spinner.clear()
    MW.geedataset_spinner.addItems(geedataset_names)
    
    MW.lc_map.clear()
    MW.lc_map.addItems(geedataset_names)
    #set worldcover as default
    MW.lc_map.setCurrentIndex(geedataset_names.index('worldcover'))

    
# =============================================================================
# Triggers
# =============================================================================

def setup_triggers(MW):
    
    #Get buttons
    MW.get_lcz.clicked.connect(lambda: _react_get_lcz(MW))    
    MW.get_altitude.clicked.connect(lambda: _react_get_altitude(MW))
    MW.get_landcover.clicked.connect(lambda: _react_get_landcover(MW))
    
    #bottom buttons
    MW.preview_metadata_2.clicked.connect(lambda: _react_show_metadata(MW))
    MW.spatial_plot.clicked.connect(lambda: _react_spatial_plot(MW))
    MW.show_gee_info.clicked.connect(lambda: _react_show_gee_info(MW))


# =============================================================================
# reactions
# =============================================================================
def _react_get_landcover(MW):
    # is metadata sufficient
    _cont = _coordinates_available(MW)
    if not _cont:
        return

    # start prompting
    MW.prompt_metadata.appendPlainText('\n---- Get landcover fractions from GEE ---- \n')
    
    bufferrad = int(MW.lc_radius.value())
    aggbool = MW.lc_agg.isChecked()
    lcmap = MW.lc_map.currentText()
    
    _lcfrac, succes, stout = tlk_scripts.gui_wrap(MW.Dataset.get_landcover,
                                                      {'buffers': [bufferrad],
                                                       'aggregate': aggbool,
                                                       'overwrite': True,
                                                       'gee_map':lcmap})
    if not succes:
        Error('Error when extracting landcover fractions', stout)
        return
    
    # write output to prompt
    MW.prompt_metadata.appendPlainText(str(stout))

    MW.prompt_metadata.appendPlainText('\n---- Get landcover fractions from GEE ---> Done! ---- \n')
    Notification(f'landcover fractions for {bufferrad}m are added to the metadf.')
    return
    

def _react_get_lcz(MW):
    # is metadata sufficient
    _cont = _coordinates_available(MW)
    if not _cont:
        return

    # start prompting
    MW.prompt_metadata.appendPlainText('\n---- Get LCZ from GEE ---- \n')

    _lcz, succes, stout = tlk_scripts.gui_wrap(MW.Dataset.get_lcz,
                                                      {})
    if not succes:
        Error('Error when extracting LCZ.', stout)
        return
    # write output to prompt
    MW.prompt_metadata.appendPlainText(str(stout))

    MW.prompt_metadata.appendPlainText('\n---- Get LCZ from GEE ---> Done! ---- \n')
    Notification('LCZ is added to the metadf.')
    return
 

def _react_get_altitude(MW):
    # is metadata sufficient
    _cont = _coordinates_available(MW)
    if not _cont:
        return

    # start prompting
    MW.prompt_metadata.appendPlainText('\n---- Get Altitude from GEE ---- \n')

    _lcz, succes, stout = tlk_scripts.gui_wrap(MW.Dataset.get_altitude,
                                                      {})
    if not succes:
        Error('Error when extracting altitude.', stout)
        return
    # write output to prompt
    MW.prompt_metadata.appendPlainText(str(stout))

    MW.prompt_metadata.appendPlainText('\n---- Get Alitutde from GEE ---> Done! ---- \n')
    Notification('Altitude is added to the metadf.')
    return
 

def _react_show_gee_info(MW):
    geename=MW.geedataset_spinner.currentText()
    MW.prompt_metadata.appendPlainText(f'\n ---------- Get info of {geename} -------- \n')
    
    _, succes, stout = tlk_scripts.gui_wrap(MW.Dataset.gee_datasets[geename].get_info,
                                                  {})
    if succes:
        MW.prompt_metadata.appendPlainText(str(stout))
        MW.prompt_metadata.centerCursor()
    else:
        Error(f'Error in getting info of {geename}.')

def _react_show_metadata(MW):
    MW._dlg = MetadataDialog(df=MW.Dataset.metadf) #launched when created    

def _react_spatial_plot(MW):
    # Check if dataset and coordinates exist
    if not _coordinates_available(MW):
        return
    MW.prompt_metadata.appendPlainText(f'\n---- Create interactive map ---- \n')
    
    #target an html file in tmp folder, remove if already exist
    filename="geestatic_plot.html"
    trg_html = os.path.join(path_handler.TMP_dir, filename)
    if path_handler.file_exist(trg_html):
        os.remove(trg_html)
    
    #create the map
    _map, succes, stout = tlk_scripts.gui_wrap(MW.Dataset.make_gee_static_spatialplot,
                                            {'Model':'lcz', #TODO
                                             'outputfolder': path_handler.TMP_dir,
                                             'filename':filename,
                                             'vmin':None, #TODO
                                             'vmax':None, #TODO
                                             'overwrite':False})
    
    if not succes:
        Error('Error when creating a geestatic spatialplot.', stout)
        return
    
    MW.prompt_metadata.appendPlainText(f'\n---- Create interactive map ---> Done! ---- \n')
    
    MW._dlg = HtmlDialog(trg_html)
    


# =============================================================================
# helpers
# =============================================================================





# def preview_metadata(MW):
#     _show_metadf(MW)






# def spatial_plot(MW):

#     # Check if dataset and coordinates exist
#     if not _coordinates_available(MW):
#         return

#     MW.prompt_metadata.appendPlainText(f'\n---- Create interactive map ---- \n')

#     # Create path to save the html file
#     # save in the TMP dir
#     filename = 'metadata_html.html'
#     filepath = os.path.join(path_handler.TMP_dir, filename)

#     # remove the file if it already exists
#     if path_handler.file_exist(filepath):
#         os.remove(filepath)

#     # create the html map
#     print('A')
#     _cont, terminal, _msg = tlk_scripts.make_html_gee_map(dataset=MW.dataset,
#                                                           html_path=filepath)

#     print('B')
#     if not _cont:
#         Error(_msg[0], _msg[1])
#         return

#     # write output to prompt
#     for line in terminal:
#         MW.prompt_metadata.appendPlainText(line)

#     MW.prompt_metadata.appendPlainText(f'\n---- Create interactive map ---> Done! ---- \n')
#     print('C')
#     _show_spatial_html(MW, filepath)
#     print('D')
#     MW.html.show()
#     print('E')





# # =============================================================================
# # helpers
# # =============================================================================

def _coordinates_available(MW):
    # check if dataset is available
    if MW.Dataset is None:
        Error('Empty dataset', 'This action could not be performed because there is no dataset.')
        return False

    # check if coordinate columns are available
    if not ('lat' in MW.Dataset.metadf.columns):
        Error('Missing coordinates', f'This action could not be performed because there is no latitude column in the metadf.\n {MW.Dataset.metadf}')
        return False

    if not ('lon' in MW.Dataset.metadf.columns):
        Error('Missing coordinates', f'This action could not be performed because there is no latitude column in the metadf.\n {MW.Dataset.metadf}')
        return False

    # check if the lat values are not all nan
    if MW.Dataset.metadf['lat'].isnull().all():
        Error('Missing coordinates', f'This action could not be performed because there is no latitude values found in the metadf. \n {MW.Dataset.metadf}')
        return False
    if MW.Dataset.metadf['lon'].isnull().all():
        Error('Missing coordinates', f'This action could not be performed because there is no longitude values found in the metadf. \n {MW.Dataset.metadf}')
        return False

    # check if the lat and lon values are within a spefic range
    if (MW.Dataset.metadf['lat'].min() <= -90.) | (MW.Dataset.metadf['lat'].max() > 90.):
        Error('Fault latitude', f'This action could not be performed because the latitudes are not within [-90, 90]. \n {MW.Dataset.metadf}')
        return False
    # check if the lat and lon values are within a spefic range
    if (MW.Dataset.metadf['lon'].min() <= -180.) | (MW.Dataset.metadf['lat'].max() > 180.):
        Error('Fault longitude', f'This action could not be performed because the longitude are not within [-180, 180]. \n {MW.Dataset.metadf}')
        return False

    return True





