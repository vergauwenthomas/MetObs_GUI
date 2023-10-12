#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct  6 09:56:23 2023

@author: thoverga
"""
import os
import matplotlib

from datetime import timedelta, datetime
from metobs_gui.path_handler import GUI_dir
from metobs_gui.errors import Error, Notification
from PyQt5.QtWidgets import QDialog, QMainWindow, QPushButton
from PyQt5.uic import loadUi



# =============================================================================
# Dialog for new observation type
# =============================================================================

class NewObstypeDialogWindow(QDialog):
    def __init__(self):
        super().__init__()
        loadUi(os.path.join(GUI_dir, 'create_new_obstype.ui'), self)

    def get_IO(self):
        obstype_name = str(self.obsname.text())
        std_unit = str(self.std_unit.text())
        desc = str(self.description.text())
        unit_conv_str = str(self.unit_conv.text())

        # convert conversionstring to dict
        conv_dict, cont = conversion_string_to_dict(convstr=unit_conv_str)
        if cont:
            return obstype_name, std_unit, desc, conv_dict

    def closeself(self):
        self.close()

# =============================================================================
# Dialog for adding a new unit
# =============================================================================
class NewUnitDialogWindow(QDialog):
    def __init__(self, obstype_dict):
        super().__init__()
        self.obstypes = obstype_dict
        loadUi(os.path.join(GUI_dir, 'create_new_unit.ui'), self)

        # initialise widgets
        self.obstype_selector.clear()
        self.obstype_selector.addItems(list(self.obstypes.keys()))

        self.update_info()

        # Triggers
        self.obstype_selector.currentTextChanged.connect(lambda: self.update_info())


    def update_info(self):
        obsname = str(self.obstype_selector.currentText())
        obstype = self.obstypes[obsname]

        # write to display
        self.obstype_display.clear()

        str1 = f'The standard unit of <b>{obsname}</b> is <b>{obstype.get_standard_unit()}</b>.'
        str2 = 'All knonw units are: '
        known_units_str = ''
        for unit in obstype.get_all_units():
            known_units_str += f'   * {unit}\n'

        str3 = f'The current conversion table:\n {obstype.conv_table}'


        self.obstype_display.appendHtml(str1)
        self.obstype_display.appendPlainText(str2)
        self.obstype_display.appendPlainText(known_units_str)
        self.obstype_display.appendPlainText(str3)



    def get_IO(self):
        obstype_name = str(self.obstype_selector.currentText())
        unit_name = str(self.unit_name.text())
        unit_conv_str = str(self.unit_conversion.text())
        # convert conversionstring to dict
        conv_list, cont = conversion_string_to_list(convstr=unit_conv_str)
        if cont:
            return obstype_name, unit_name, conv_list

    def closeself(self):
        self.close()



# =============================================================================
#  Map column dialog
# =============================================================================


class MapColumnDialogWindow(QDialog):
    def __init__(self, data_column_names, metadata_column_names, use_metadata,
                 unused_obstypes, unmapped_metatypes, unmapped_specialtypes):
        super().__init__()
        loadUi(os.path.join(GUI_dir, 'map_column_dialog.ui'), self)

        self.IO = {} #store mapping info
        self.IO['datacolumns'] = {} #column name (obstype) --> obstype and unit
        self.IO['metadatacolumns']= {} #column name (metadata) --> description
        self.IO['namecolumn'] = None
        self.IO['dt'] = {"datetime": {'columnname': None, 'fmt': None},
                                        'date' : {'columnname': None, 'fmt': None},
                                        'time': {'columnname': None, 'fmt': None}}

        # store all arguments as attributes

        self.obstypes = unused_obstypes
        self.data_column_names = data_column_names
        self.metadata_column_names = metadata_column_names
        self.use_metadata = use_metadata

        # setup spinners (data)
        self.columnname_spinner.addItems(data_column_names)
        self.obstype_spinner.addItems([obs.name for obs in unused_obstypes])
        self.update_unit_spinner()
        # setup spinners (specials)
        self.non_obstype_spinner.addItems(unmapped_specialtypes)
        self.update_fmt_qline()
        # setup spinners (metadata)
        if self.use_metadata:
            self.meta_columnname.addItems(metadata_column_names)
            self.metadata_spinner.addItems(unmapped_metatypes)
        else:
            self.disable_metadata()

        self.update_overview()

        #triggers
        # Link units with obstypes
        self.obstype_spinner.currentTextChanged.connect(lambda: self.update_unit_spinner())
        self.non_obstype_spinner.currentTextChanged.connect(lambda: self.update_fmt_qline())

        self.map_column_data.clicked.connect(lambda: self.map_data_column())
        self.map_column_data_special.clicked.connect(lambda: self.map_data_column_as_special())
        self.map_column_metadata.clicked.connect(lambda: self.map_metadata_column())
        self.close_button.clicked.connect(lambda: self.closeself())

    def map_data_column(self):

        # when click on Map column for data
        columnname = str(self.columnname_spinner.currentText())
        obstype = self.get_current_obstype()
        unit = str(self.unit_spinner.currentText())
        description = str(self.obs_description.text())


        # update the description of the obstype
        obstype.set_description(description)

        # add to IO dict
        self.IO['datacolumns'][columnname] = {'obstype': obstype,
                                             'unit': unit,
                                             }

        #remove the column and obstype from the spinners
        cur_spinner_idx = self.columnname_spinner.currentIndex()
        self.columnname_spinner.removeItem(cur_spinner_idx)

        cur_spinner_idx = self.obstype_spinner.currentIndex()
        self.obstype_spinner.removeItem(cur_spinner_idx)

        # trigger unit
        self.update_unit_spinner()

        # make notification
        Notification(f'{columnname} is mapped as {obstype.name} (in {unit}).')
        self.update_overview()

    def map_metadata_column(self):
        # when click on Map column for data
        columnname = str(self.meta_columnname.currentText())
        metatype = str(self.metadata_spinner.currentText())

        # add to IO dict
        self.IO['metadatacolumns'][columnname]= metatype

        #remove the column and obstype from the spinners
        self.remove_from_spinner(columnname, 'meta_columnname')
        self.remove_from_spinner(metatype, 'metadata_spinner')

        # make notification
        Notification(f'{columnname} is mapped as {metatype}.')
        self.update_overview()
    def map_data_column_as_special(self):

        # when click on Map column for data (specials)
        columnname = str(self.columnname_spinner.currentText())
        specialtype = str(self.non_obstype_spinner.currentText())
        fmt = str(self.datetimeformat.text())

        if specialtype == 'name':
            cont = self.test_name_column(columnname=columnname)
            if not cont:
                return
            self.IO['namecolumn'] = columnname

            # remove the column from the data and metadata spinners
            self.remove_from_spinner(columnname, 'columnname_spinner')
            self.remove_from_spinner(columnname, 'meta_columnname')
            self.remove_from_spinner('name', 'non_obstype_spinner')

            # make notification
            Notification(f'{columnname} is mapped as Name column.')


        if specialtype == 'datetime':
            # TODO: write fmt test
            self.IO['dt']['datetime']['columnname'] = columnname
            self.IO['dt']['datetime']['fmt'] = fmt
            # remove the column from the data and metadata spinners
            self.remove_from_spinner(columnname, 'columnname_spinner')
            for col in ['datetime', 'date', 'time']:
                self.remove_from_spinner(col, 'non_obstype_spinner')

            # make notification
            Notification(f'{columnname} is mapped as Datetime column. (in {fmt})')

        if specialtype == 'date':
            # TODO: write fmt test
            self.IO['dt']['date']['columnname'] = columnname
            self.IO['dt']['date']['fmt'] = fmt
            # remove the column from the data and metadata spinners
            self.remove_from_spinner(columnname, 'columnname_spinner')
            for col in ['datetime', 'date']:
                self.remove_from_spinner(col, 'non_obstype_spinner')

            # make notification
            Notification(f'{columnname} is mapped as Date column.  (in {fmt})')

        if specialtype == 'time':
            # TODO: write fmt test
            self.IO['dt']['time']['columnname'] = columnname
            self.IO['dt']['time']['fmt'] = fmt
            # remove the column from the data and metadata spinners
            self.remove_from_spinner(columnname, 'columnname_spinner')
            for col in ['datetime', 'time']:
                self.remove_from_spinner(col, 'non_obstype_spinner')

            # make notification
            Notification(f'{columnname} is mapped as Time column.')

        self.update_overview()



    def test_name_column(self, columnname):
        # test if the name column is the found in both data and metadata
        if columnname not in self.data_column_names:
            Error(f'"name" column not found', f'The {columnname} is not found as a data column!')
            return False
        if self.use_metadata:
            if columnname not in self.metadata_column_names:
                Error(f'"name" column not found', f'The {columnname} is not found as a metadata column!')
                return False
        return True

    def disable_metadata(self):
        for widg in [self.meta_columnname, self.metadata_spinner, self.map_column_metadata]:
            widg.setEnabled(False)

    def remove_from_spinner(self, itemname, spinnername):
        index = getattr(self, spinnername).findText(itemname)
        if index != -1:
            getattr(self,spinnername).removeItem(index)  # remove item from index


    def update_fmt_qline(self):
        cur_special = self.non_obstype_spinner.currentText()
        if cur_special == 'datetime':
            self.datetimeformat.setText('%Y/%m/%d %H:%M:%S')
            self.datetimeformat.setEnabled(True)
        elif cur_special == 'time':
            self.datetimeformat.setText('%H:%M:%S')
            self.datetimeformat.setEnabled(True)
        elif cur_special == 'date':
            self.datetimeformat.setText('%Y/%m/%d')
            self.datetimeformat.setEnabled(True)
        else:
            self.datetimeformat.setEnabled(False)


    def update_unit_spinner(self):
        # empty spinner
        self.unit_spinner.clear()
        # Get selected obstype
        selected_obstype = self.get_current_obstype()
        # add all known units in the spinner
        self.unit_spinner.addItems(selected_obstype.get_all_units())
        # select the std unit by default
        self.unit_spinner.setCurrentText(selected_obstype.get_standard_unit())

        # update the description widget
        self.obs_description.setText(selected_obstype.get_description())



    def get_current_obstype(self):
        selected_obstypename = self.obstype_spinner.currentText()
        return [obs for obs in self.obstypes if obs.name == selected_obstypename][0]

    def update_overview(self):
        self.overview.clear()

        self.overview.appendPlainText(' --- Mapped Data Columns ---')
        for key, item in self.IO['datacolumns'].items():
            self.overview.appendPlainText(f'   {key} --> {item["obstype"].name}  (in {item["unit"]})')
        self.overview.appendPlainText('\n')

        # special data columns
        if self.IO['namecolumn'] is not None:
            self.overview.appendPlainText(f'   {self.IO["namecolumn"]} --> Name column')

        if self.IO['dt']['datetime']['columnname'] is not None:
            self.overview.appendPlainText(f"   {self.IO['dt']['datetime']['columnname']} --> datetime column in {self.IO['dt']['datetime']['fmt']} column")
        if self.IO['dt']['date']['columnname'] is not None:
            self.overview.appendPlainText(f"   {self.IO['dt']['date']['columnname']} --> date column in {self.IO['dt']['date']['fmt']} column")
        if self.IO['dt']['time']['columnname'] is not None:
            self.overview.appendPlainText(f"   {self.IO['dt']['time']['columnname']} --> time column in {self.IO['dt']['time']['fmt']} column")
        # Metadata columns
        self.overview.appendPlainText('\n')
        self.overview.appendPlainText(' --- Mapped Metadata Columns ---')
        for key, item in self.IO['metadatacolumns'].items():
            self.overview.appendPlainText(f'   {key} --> {item}')

        if self.IO['namecolumn'] is not None:
            self.overview.appendPlainText(f'   {self.IO["namecolumn"]} --> Name column')

    def get_mapping_data(self):

        #select all text to transfer to main
        text = self.overview.toPlainText()

        return (self.IO['datacolumns'], self.IO['metadatacolumns'],
                self.IO['namecolumn'], self.IO['dt'], text)

    def closeself(self):
        self.close()







# =============================================================================
# Helpers
# =============================================================================
def conversion_string_to_list(convstr):
    try:
        conv = convstr.replace('"', '').replace("'", "").replace(' ', '').replace('[', '').replace(']', '')
        conv_list = []
        for strel in conv.split(','):
            conv_list.append(str(strel))
    except:
        Error('Syntax error new unit', f'There is a syntax error converting {convstr} to a list. Look carefully at the default string for the syntax.')
        return None, False

    #1. Check if list is not empty
    if not bool(conv_list):
        Error('Syntax error new obstype', f'There is a syntax error converting {convstr} to a list (-> conversion is empty). Look carefully at the default string for the syntax.')
        return None, False

    # 2. check if all elements of conversion
    for expr in conv_list:
        cont = _test_conv_expr(expr)
        if not cont:
            return None, False
    return conv_list, True


def conversion_string_to_dict(convstr):
    """ convert string expression of unit conversion to a dict of strings."""
    try:
        conv = convstr.split('{')[1].split('}')[0].replace('"', '').replace("'", "").replace(' ', '')
        conv_dict = {}

        # make pairs --> do not split on , because this will not work for complex conversions that have a , in the value of the conversiondict!!
        # # Idea is to split on the :, and than split on ,
        keystr = []
        valstr = []

        unstrlist = conv.split('],')
        for strel in unstrlist:
            strel = strel.replace('[', '').replace(']', '')
            keystr.append(strel.split(':')[0])
            valstr.append(strel.split(':')[1])

        for pairstr in list(zip(keystr, valstr)):
            key = str(pairstr[0])
            val = [str(part) for part in pairstr[1].split(',')]
            conv_dict[key] = val

    except:
        Error('Syntax error new obstype', f'There is a syntax error converting {convstr} to a dict. Look carefully at the default string for the syntax.')
        return None, False

    #1. Check if dict is not empty
    if not bool(conv_dict):
        Error('Syntax error new obstype', f'There is a syntax error converting {convstr} to a dict (-> conversion is empty). Look carefully at the default string for the syntax.')
        return None, False

    # 2. check if all elements of conversion
    for expr in conv_dict.values():
        for subexpr in expr:
            cont = _test_conv_expr(subexpr)
            if not cont:
                return None, False
    return conv_dict, True


def _test_conv_expr(expression):

    # test if conversion is valid
    # ... start with x
    if not expression.startswith('x'):
        Error('Syntax error new obstype', f'Expression {expression} does not start with x.')
        return False
    # ... conatain only one occurance of +,-,* or /
    manipulations = ['+', '-', '*', '/']
    man_counter = 0
    for man in manipulations:
        man_counter += expression.count(man)
        if expression.count(man) > 1:
            Error('Syntax error new obstype', f'There is more than one occurance of {man} in the {expression} string.')
            return False
    if man_counter != 1:
        Error('Syntax error new obstype', f'There must be one reference of +, -, * or / for each conversion which is not fulfilled in in the {expression} string.')
        return False

    return True

