#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 28 13:30:48 2023

@author: thoverga
"""
from pathlib import Path
import os
import copy
import pytz
from PyQt5.QtWidgets import QFileDialog, QComboBox


# from main import MainWindow as MW

from metobs_gui.json_save_func import get_saved_vals, update_json_file
from metobs_gui.data_func import readfile, isvalidfile, get_columns

from metobs_gui.import_data_page import set_possible_templates


import metobs_gui.template_func as template_func
import metobs_gui.path_handler as path_handler

from metobs_gui.errors import Error, Notification
from metobs_gui.dialog_launcher import NewObstypeDialogWindow, MapColumnDialogWindow, NewUnitDialogWindow

from metobs_gui.tlk_scripts import test_new_obstype, get_default_obstypes
from metobs_gui.errors import Error



# =============================================================================
# Initialise values
# =============================================================================
def init_template_page(MW):

    MW.session['mapping'] = {}
    MW.session['mapping']['started'] = False
    #Store mapping info
    reset_saved_mapping(MW)

    # add default obstypess
    MW.session['mapping']['obstypes'] = {'defaults': get_default_obstypes()}
    MW.session['mapping']['obstypes']['new_obstypes'] = {}

    # list all templates in the cache
    MW.session['templates'] = {}
    MW.session['templates']['cache'] = template_func.get_all_templates() # name.csv : path
    MW.session['templates']['in_use']: {} # name.csv : path

    # set data paths to saved files
    set_datapaths_init(MW)

    # set static spinners
    MW.browse_format.addItems(['long', 'wide', 'single-station'])
    MW.wide_obs_type.addItems(list(template_func.Obs_map_values.keys()))

    MW.timezone_spinner.addItems(pytz.common_timezones)
    MW.timezone_spinner.setCurrentText('UTC')

    # disable format options
    MW.wide_obs_type.setEnabled(False) # disable comboBox
    MW.wide_unit.setEnabled(False)
    MW.wide_obs_desc.setEnabled(False)
    MW.stationname.setEnabled(False)







def setup_template_triggers(MW):
    MW.Browse_data_B.clicked.connect(lambda: browsefiles_data(MW)) #browse datafile
    MW.Browse_metadata_B.clicked.connect(lambda: browsefiles_metadata(MW)) #browse metadatafile
    # save paths when selected
    MW.save_data_path.clicked.connect(lambda: save_path(
                                                            MW=MW,
                                                            savebool=MW.save_data_path.isChecked(),
                                                            savekey='data_file_path',
                                                            saveval=MW.data_file_T.text()))
    MW.save_metadata_path.clicked.connect(lambda: save_path(
                                                            MW=MW,
                                                            savebool=MW.save_metadata_path.isChecked(),
                                                            savekey='metadata_file_path',
                                                            saveval=MW.metadata_file_T.text()))

    MW.browse_format.currentTextChanged.connect(lambda: enable_format_widgets(MW))

    # initiate the start mapping module
    MW.start_mapping_B.clicked.connect(lambda: prepare_for_mapping(MW))

    # construnct the mappindict
    MW.build_B.clicked.connect(lambda: make_template_build(MW))

    # save template
    MW.save_template.clicked.connect(lambda: save_template_call(MW))

    # display df's
    MW.preview_data.clicked.connect(lambda: show_data_head(MW))
    MW.preview_metadata.clicked.connect(lambda: show_metadata_head(MW))
    MW.view_template.clicked.connect(lambda: show_template(MW))

    MW.wide_obs_type.currentTextChanged.connect(lambda: wide_obstype_change(MW))

    # Mapping and obstypes
    MW.add_obstype.clicked.connect(lambda: make_new_obstype(MW))
    MW.map_columns.clicked.connect(lambda: map_column(MW))
    MW.reset_mapping.clicked.connect(lambda: reset_saved_mapping(MW))
    MW.add_unit.clicked.connect(lambda: create_new_unit(MW))


def set_datapaths_init(MW):
    """
    Read saved values to look for a path for the data and metadata file.

    """
    saved_vals = get_saved_vals()

    # set datafile path
    if 'data_file_path' in saved_vals:
        MW.data_file_T.setText(str(saved_vals['data_file_path']))


    # set metadata file path
    if 'metadata_file_path' in saved_vals:
        MW.metadata_file_T.setText(str(saved_vals['metadata_file_path']))





# =============================================================================
# Triggers
# =============================================================================
def reset_saved_mapping(MW):
    MW.session['mapping']['mapped_obstypes'] = {} #column name (obstype) --> 'obstype': ...., 'unit': ...
    MW.session['mapping']['mapped_metadata'] = {} #column name (metadata) --> metatype
    MW.session['mapping']['mapped_name'] = None #Name column
    MW.session['mapping']['mapped_datetime'] = {"datetime": {'columnname': None, 'fmt': None},
                                                'date' : {'columnname': None, 'fmt': None},
                                                'time': {'columnname': None, 'fmt': None}}

    MW.mapping_info.clear()
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
    reset_saved_mapping(MW) #clear current saved mapping info
    MW.save_template.setEnabled(False)

    if dat_format == 'long':
        MW.wide_obs_type.setEnabled(False) # disable comboBox
        MW.wide_unit.setEnabled(False)
        MW.wide_obs_desc.setEnabled(False)
        MW.stationname.setEnabled(False)
        MW.map_columns.setEnabled(True)
        MW.reset_mapping.setEnabled(True)

    elif dat_format == 'wide':
        update_wide_obstypes(MW) #find all possible obstypes and units
        MW.wide_obs_type.setEnabled(True) # disable comboBox
        MW.wide_unit.setEnabled(True)
        MW.wide_obs_desc.setEnabled(True)
        MW.stationname.setEnabled(False)
        MW.map_columns.setEnabled(False)
        MW.reset_mapping.setEnabled(False)

    else:
        MW.wide_obs_type.setEnabled(False) # disable comboBox
        MW.wide_unit.setEnabled(False)
        MW.wide_obs_desc.setEnabled(False)
        MW.stationname.setEnabled(True)
        MW.map_columns.setEnabled(True)
        MW.reset_mapping.setEnabled(True)

def wide_obstype_change(MW):
    # wide obstype has changed --> update available units
    obstypename = str(MW.wide_obs_type.currentText())
    if obstypename != '': #not initialized yet

        # get obstypes
        all_obstypes = _get_all_obstypes_dict(MW)
        obstype = all_obstypes[obstypename]
        possible_units = obstype.get_all_units()
        default_unit = obstype.get_standard_unit()

        MW.wide_unit.clear()
        MW.wide_unit.addItems(possible_units)
        MW.wide_unit.setCurrentText(default_unit)

def update_wide_obstypes(MW):
    #when a new obstype is added
    # get obstypes
    all_obstypes = _get_all_obstypes_dict(MW)

    # update spinner
    MW.wide_obs_type.clear()
    MW.wide_obs_type.addItems(list(all_obstypes.keys()))

    # update corresponding unit
    wide_obstype_change(MW)








def prepare_for_mapping(MW):
    MW.session['mapping']['started'] = True

    dat_format = str(MW.browse_format.currentText())
    # _get_name_box(MW).setEnabled(True)
    MW.session['mapping']['info'] = {'data_format': dat_format}
    if (dat_format == 'long') | (dat_format == 'single-station'):
        # First try reading the datafile
        # 1. THe data file
        datafile = MW.data_file_T.text()
        valid, _msg = isvalidfile(datafile, filetype='.csv')
        if not valid:
            Error(_msg)
            return
        # Read columns
        df_head = readfile(datafile, nrows=20)[0]
        df_cols = list(df_head.columns)
        MW.session['mapping']['data_head'] = df_head.copy() #save for tests on template
        MW.session['mapping']['data_cols'] = df_cols.copy() #save for tests on template
        # Get the obstype spinners
        csv_columns = df_cols

        # csv_columns.insert(0, template_func.not_mapable)



        # set column and default values
        # template_func.set_obstype_spinner_values(MW, csv_columns)
        # template_func.set_time_spinner_values(MW, csv_columns)
        # template_func.set_obstype_desc_defaults(MW)
        # template_func.set_obstype_units_defaults(MW)
        # template_func.set_datetime_defaults(MW)
    else:
        csv_columns = []
        # if not MW.use_metadata.isChecked():
        #     # no metadata and wide format
        #     _get_name_box(MW).setEnabled(False)



    #2. The metadata
    if MW.use_metadata.isChecked():
        metadatafile = MW.metadata_file_T.text()
        valid, _msg = isvalidfile(metadatafile, filetype='.csv')
        if not valid:
            Error(_msg)
            return
        metadf_head = readfile(metadatafile, nrows=20)[0]
        metadf_cols = list(metadf_head.columns)
        MW.session['mapping']['metadata_head'] = metadf_head.copy() #save for tests on template
        MW.session['mapping']['metadata_cols'] = metadf_cols.copy() #save for tests on template
        # metadf_cols.insert(0, template_func.not_mapable)

        # enable all obs boxes for colum mapping
        # for box in _get_metadata_boxes(MW): box.setEnabled(True)

        # set column and default values
        # template_func.set_metadata_spinner_values(MW, metadf_cols)
    else:
        metadf_cols = []

    # template_func.set_name_spinner_values(MW, csv_columns, metadf_cols)
    # enable the build button
    MW.build_B.setEnabled(True)



# -------  Build template ---------

def build_template(MW):
    MW.session['mapping']['template_df'] = None
    df, succes = template_func.make_template_build(MW)
    if succes:
        MW.session['mapping']['template_df'] = df.copy()
        MW.templmodel.setDataFrame(df)
        MW.save_template.setEnabled(True) #enable the save button

def save_template_call(MW):
    # test if template is not empty
    if MW.session['mapping']['template_df'] is None:
        Error('Template error', 'The template has not been succesfully build. It is not possible to save.')
        return
    if MW.session['mapping']['template_df'].empty:
        Error('Template error', 'The template is empty. It is not possible to save.')
        return
    # form path to save the template
    template_name = str(MW.templatename.text())
    if not template_name.endswith('.csv'):
        filename = template_name + '.csv'
    else:
        filename = template_name
    target_path = os.path.join(path_handler.template_dir, filename)

    if path_handler.file_exist(target_path):
        Error(f'{target_path} already exists! Change name of the template file and save again.')
        return

    # save template
    temp_df =MW.session['mapping']['template_df']
    temp_df.to_csv(path_or_buf=target_path, sep=',', index=False)

    Notification(f'Template ({filename}) is saved!')

    # update dict
    MW.session['templates']['in_use'] = {filename : target_path}
    # update cache templates
    MW.session['templates']['cache'] = template_func.get_all_templates() # name.csv : path

    # Trigger update spinner on import page so the saved templ appears in the spinner there
    set_possible_templates(MW)


def show_data_head(MW):
    # 1. THe data file
    datafile = MW.data_file_T.text()
    valid, _msg = isvalidfile(datafile, filetype='.csv')
    if not valid:
        Error(_msg)
        return
    # Read columns
    df_head = readfile(datafile, nrows=20)[0]
    MW.templmodel.setDataFrame(df_head)

def show_metadata_head(MW):
   metadatafile = MW.metadata_file_T.text()
   valid, _msg = isvalidfile(metadatafile, filetype='.csv')
   if not valid:
       Error(_msg)
       return
   # Read columns
   metadf_head = readfile(metadatafile, nrows=20)[0]
   MW.templmodel.setDataFrame(metadf_head)



def show_template(MW):
    if not 'template_df' in MW.session['mapping']:
        Error('View error', 'The template is not been succesfully build yet.')
        return
    MW.templmodel.setDataFrame(MW.session['mapping']['template_df'])




def map_column(MW):
    if not MW.session['mapping']['started']:
        Error('Mapping not started', 'First start the mapping procecess.')
        return
    # =============================================================================
    # Get unmapped observation types and columns
    # =============================================================================

    # get all columnnames
    all_data_columnnames = MW.session['mapping']['data_cols']

    # get obstypes
    all_obstypes = _get_all_obstypes_dict(MW)

    # get the already mapped obstypes
    mapped = MW.session['mapping']['mapped_obstypes']
    mapped_columns = list(mapped.keys())
    mapped_obstypes = [val['obstype'] for val in mapped.values()]

    # unmapped data columns
    unmapped_data_columns = list(set(all_data_columnnames) - set(mapped_columns))

    # unmapped obstypes
    unmapped_obs_names = list(set([obs for obs in all_obstypes.keys()]) - set([obs2.name for obs2 in mapped_obstypes]))
    unmapped_obs = [obs for obs in all_obstypes.values() if obs.name in unmapped_obs_names]

    # =============================================================================
    # Get unmapped meta data columns
    # =============================================================================
    use_metadata = MW.use_metadata.isChecked()
    if use_metadata:
        all_metadata_columnames = MW.session['mapping']['metadata_cols']
    else:
        all_metadata_columnames = []
    required_meta = ['lat', 'lon']
    already_mapped = MW.session['mapping']['mapped_metadata'].values()

    # get unmapped metacolumns
    unmapped_metadata = [typ for typ in required_meta if typ not in already_mapped]

    # =============================================================================
    # Get special mappings (name and timestamp)
    # =============================================================================
    required_special = ['name', 'datetime', 'date', 'time']
    unmapped_specials = []

    # add name to unmapped if needed
    if MW.session['mapping']['mapped_name'] is None:
        unmapped_specials.append('name')

    # add datetime
    _dtmap = MW.session['mapping']['mapped_datetime']
    if ((_dtmap['datetime']['columnname'] is None) &
        (_dtmap['date']['columnname'] is None) &
        (_dtmap['time']['columnname'] is None)):

        unmapped_specials.append('datetime')
        unmapped_specials.append('date')
        unmapped_specials.append('time')

    elif ((_dtmap['datetime']['columnname'] is not None)):
        # do not add any datetime arg to spinner
        pass
    elif ((_dtmap['datetime']['columnname'] is None) &
          (_dtmap['date']['columnname'] is not None) &
          (_dtmap['time']['columnname'] is None)):
        unmapped_specials.append('time')
    elif ((_dtmap['datetime']['columnname'] is None) &
          (_dtmap['date']['columnname'] is None) &
          (_dtmap['time']['columnname'] is not None)):
        unmapped_specials.append('date')
    else:
        import sys
        sys.exit('unforseen situation in possible datetime arguments for spinner.')




    MW.dial =  MapColumnDialogWindow(data_column_names=unmapped_data_columns,
                                     metadata_column_names= all_metadata_columnames,
                                     use_metadata=use_metadata,
                                     unused_obstypes=unmapped_obs,
                                     unmapped_metatypes=unmapped_metadata,
                                     unmapped_specialtypes=unmapped_specials)
    MW.dial.show()

    def transfer_data(dialog):
        (obstypemapping, metamapping, namemapping, dtmapping, text)= dialog.get_mapping_data() #get data

        #update attributes
        MW.session['mapping']['mapped_obstypes'].update(obstypemapping)
        MW.session['mapping']['mapped_metadata'].update(metamapping)
        MW.session['mapping']['mapped_name'] = namemapping
        MW.session['mapping']['mapped_datetime'].update(dtmapping)

        MW.mapping_info.clear()
        MW.mapping_info.appendPlainText(text)

        MW.dialog_user_input = None
        dialog.closeself() #close dialog

    # trigger
    MW.dial.close_button.clicked.connect(lambda: transfer_data(MW.dial))


def create_new_unit(MW):
    MW.dialog_user_input = None
    def transfer_data(dialog):
        io = dialog.get_IO() #get data
        if io is None:
            return

        obstype_name, new_unit_name, conv_list = io

        # update obstpe
        if obstype_name in MW.session['mapping']['obstypes']['defaults'].keys():
            MW.session['mapping']['obstypes']['defaults'][obstype_name].add_unit(unit_name=new_unit_name,
                                                                                 conversion=conv_list)
        elif obstype_name in MW.session['mapping']['obstypes']['new_obstypes'].keys():
            MW.session['mapping']['obstypes']['new_obstypes'][obstype_name].add_unit(unit_name=new_unit_name,
                                                                                 conversion=conv_list)

        Notification(f'{new_unit_name} is added as a unit for {obstype_name}!')

        dialog.closeself()

    # launch dialog
    all_obstypes =  _get_all_obstypes_dict(MW)
    MW.dial = NewUnitDialogWindow(obstype_dict=all_obstypes)
    MW.dial.show()

    # trigger
    MW.dial.save_unit.clicked.connect(lambda: transfer_data(MW.dial))

    # Update spinners depenng on all obstypes
    update_wide_obstypes(MW)



def make_new_obstype(MW):
    MW.dialog_user_input = None
    def transfer_data(dialog):
        io = dialog.get_IO() #get data
        MW.dialog_user_input = io #overload to self
        cont = check_if_obstype_is_valid(MW)
        if cont:
            MW.dialog_user_input = None
            dialog.closeself() #close dialog


    # launch dialog
    MW.dial = NewObstypeDialogWindow()
    MW.dial.show()

    # trigger
    MW.dial.create_new_obstype.clicked.connect(lambda: transfer_data(MW.dial))

    # Update spinners depending on all obstypes
    update_wide_obstypes(MW)

# =============================================================================
# Template funct
# =============================================================================

def make_template_build(MW):
    templdf, cont = template_func.make_template_build(MW)
    if not cont:
        MW.save_template.setEnabled(False)
        return
    # store template
    MW.session['mapping']['template_df'] = templdf

    # enable save button
    MW.save_template.setEnabled(True)
    # display template
    show_template(MW)

    # make notification
    Notification('Template has been build sucsessfully!')





# =============================================================================
# helpers
# =============================================================================


def check_if_obstype_is_valid(MW):
    # try converting to obstype
    obsname = MW.dialog_user_input[0]
    std_units = MW.dialog_user_input[1]
    description = MW.dialog_user_input[2]
    conv_dict = MW.dialog_user_input[3]


    # test validity
    cont, new_obstype, err_msg = test_new_obstype(obsname=obsname,
                                     std_unit=std_units,
                                     description=description,
                                     unit_aliases={},
                                     unit_conv=conv_dict)
    if not cont:
        Error(err_msg[0], err_msg[1])

    # test if obstype is new
    default_obsnames = get_default_obstypes()
    if obsname in default_obsnames:
        Error('Known obstype', f'{obsname} is already a default observation type.')
        return False
    extra_obstype_names = list(MW.extra_obstypes.keys())
    if obsname in extra_obstype_names:
        Error('Known obstype', f'{obsname} is already added to the known observation types.')
        return False

    # add obstype as attribute
    print(f" obsname: {obsname}, new_obstype: {new_obstype}, current saved: {MW.session['mapping']['obstypes']['new_obstypes']}")
    MW.session['mapping']['obstypes']['new_obstypes'][obsname] = new_obstype
    Notification(f'{obsname} added to the known observation types!')
    return True

def _get_all_obstypes_dict(MW):
    # all obstypes are a combination of
    # * the default obstypes
    # * the new created obstypes
    # * (added units of corresponding obstypes)

    all_obstypes = list(MW.session['mapping']['obstypes']['defaults'].values())
    all_obstypes.extend(list(MW.session['mapping']['obstypes']['new_obstypes'].values()))
    test = {obs.name: obs for obs in all_obstypes}
    return test



