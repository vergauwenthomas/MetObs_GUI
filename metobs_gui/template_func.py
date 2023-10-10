#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 20 13:00:45 2023

@author: thoverga
"""

import metobs_gui.path_handler as path_handler
import os
import math
from pathlib import Path
import numpy as np
import pandas as pd

from metobs_gui.errors import Error, Notification

# =============================================================================
# default settings
# =============================================================================

not_mapable='NO MAPPING'

Obs_map_values = {

     'temp':{'units': ['K', 'Celcius'], 'description':'2mT'},
     'radiation_temp':{'units': ['K', 'Celcius'], 'description':'Blackglobe temperature'},
     'humidity':{'units': ['%'], 'description':'Relative humidity'},
     'precip':{'units': ['l/hour x m²'], 'description':'Precipitation intensity'},
     'precip_sum':{'units': ['l/m²', 'Celcius'], 'description':'Precipitation cumulated'},
     'wind_speed':{'units': ['m/s'], 'description':'Average wind speed'},
     'wind_gust':{'units': ['m/s'], 'description':'Wind gust'},
     'wind_direction':{'units': ['°'], 'description':'Wind direction (from north CW)'},
     'pressure':{'units': ['Pa'], 'description':'Air pressure'},
     'pressure_at_sea_level':{'units': ['Pa'], 'description':'Pressure at sealevel'}

    }

Dt_map_values = {
    'datetime': {'format':'%Y-%m-%d %H:%M:%S'},
    '_date':{'format':'%Y-%m-%d'},
    '_time':{'format':'%H:%M:%S'},
    }

Meta_map_values = {
    'name': {'description': 'Station name/ID'},
    'lat':{'description': 'Latitude'},
    'lon':{'description': 'Longitude' },
    'location':{'description': 'Location identifier'},
    'call_name':{'description': 'Pseudo name of station'},
    'network':{'description': 'Name of the network'}
    }

# =============================================================================
# Functions
# =============================================================================


#     # =============================================================================
#     # Observation types
#     # =============================================================================
# def set_obstype_spinner_values(main, values):
#     # empty spinner values
#     main.temp_col_CB.clear()
#     main.radtemp_col_CB.clear()
#     main.hum_col_CB.clear()
#     main.pre_col_CB.clear()
#     main.pre_s_col_CB.clear()
#     main.wind_col_CB.clear()
#     main.gust_col_CB.clear()
#     main.dir_col_CB.clear()
#     main.p_col_CB.clear()
#     main.psea_col_CB.clear()
#     # Fill with defaults
#     main.temp_col_CB.addItems(values)
#     main.radtemp_col_CB.addItems(values)
#     main.hum_col_CB.addItems(values)
#     main.pre_col_CB.addItems(values)
#     main.pre_s_col_CB.addItems(values)
#     main.wind_col_CB.addItems(values)
#     main.gust_col_CB.addItems(values)
#     main.dir_col_CB.addItems(values)
#     main.p_col_CB.addItems(values)
#     main.psea_col_CB.addItems(values)

# def set_time_spinner_values(main, values):
#     # empty spinner values
#     main.datetime_col_CB.clear()
#     main.date_col_CB.clear()
#     main.time_col_CB.clear()
#     # Fill with defaults
#     main.datetime_col_CB.addItems(values)
#     main.date_col_CB.addItems(values)
#     main.time_col_CB.addItems(values)

# def set_name_spinner_values(main, values_a, values_b):
#     """ The valuese are the unique sum of values_a and values_b """
#     if values_a is None:
#         values_a = []
#     if values_b is None:
#         values_b = []
#     values_a.extend(values_b)
#     comb_val = list(set(values_a))

#     # empty spinner values
#     main.name_col_CB.clear()
#     main.name_col_CB.addItems(comb_val)



# def set_obstype_units_defaults(main):
#     # empty spinner values
#     main.temp_units_CB.clear()
#     main.radtemp_units_CB.clear()
#     main.hum_units_CB.clear()
#     main.pre_units_CB.clear()
#     main.pre_s_units_CB.clear()
#     main.wind_units_CB.clear()
#     main.gust_units_CB.clear()
#     main.dir_units_CB.clear()
#     main.p_units_CB.clear()
#     main.psea_units_CB.clear()
#     # Fill with defaults
#     main.temp_units_CB.addItems(Obs_map_values['temp']['units'])
#     main.radtemp_units_CB.addItems(Obs_map_values['radiation_temp']['units'])
#     main.hum_units_CB.addItems(Obs_map_values['humidity']['units'])
#     main.pre_units_CB.addItems(Obs_map_values['precip']['units'])
#     main.pre_s_units_CB.addItems(Obs_map_values['precip_sum']['units'])
#     main.wind_units_CB.addItems(Obs_map_values['wind_speed']['units'])
#     main.gust_units_CB.addItems(Obs_map_values['wind_gust']['units'])
#     main.dir_units_CB.addItems(Obs_map_values['wind_direction']['units'])
#     main.p_units_CB.addItems(Obs_map_values['pressure']['units'])
#     main.psea_units_CB.addItems(Obs_map_values['pressure_at_sea_level']['units'])

# def set_obstype_desc_defaults(main):

#     # Fill with defaults
#     main.temp_desc_T.setText(Obs_map_values['temp']['description'])
#     main.radtemp_desc_T.setText(Obs_map_values['radiation_temp']['description'])
#     main.hum_desc_T.setText(Obs_map_values['humidity']['description'])
#     main.pre_desc_T.setText(Obs_map_values['precip']['description'])
#     main.pre_s_desc_T.setText(Obs_map_values['precip_sum']['description'])
#     main.wind_desc_T.setText(Obs_map_values['wind_speed']['description'])
#     main.gust_desc_T.setText(Obs_map_values['wind_gust']['description'])
#     main.dir_desc_T.setText(Obs_map_values['wind_direction']['description'])
#     main.p_desc_T.setText(Obs_map_values['pressure']['description'])
#     main.psea_desc_T.setText(Obs_map_values['pressure_at_sea_level']['description'])

# def set_datetime_defaults(main):

#     # Fill with defaults
#     main.datetime_fmt_T.setText(Dt_map_values['datetime']['format'])
#     main.date_fmt_T.setText(Dt_map_values['_date']['format'])
#     main.time_fmt_T.setText(Dt_map_values['_time']['format'])





# def set_metadata_spinner_values(main, values):
#     print('Setting metadata spinners items with: ', values)
#     # empty spinner values
#     main.lat_col_CB.clear()
#     main.lon_col_CB.clear()
#     main.loc_col_CB.clear()
#     main.call_col_CB.clear()
#     main.network_col_CB.clear()
#     # fill values
#     main.lat_col_CB.addItems(values)
#     main.lon_col_CB.addItems(values)
#     main.loc_col_CB.addItems(values)
#     main.call_col_CB.addItems(values)
#     main.network_col_CB.addItems(values)




# def enable_all_boxes(main):
#     main.temp_col_CB.setEnabled(True)
#     main.temp_units_CB.setEnabled(True)

#     main.radtemp_units_CB.setEnabled(True)
#     main.radtemp_desc_T.setEnabled(True)
#     main.hum_units_CB.setEnabled(True)
#     main.hum_desc_T.setEnabled(True)

#     main.pre_units_CB.setEnabled(True)
#     main.pre_desc_T.setEnabled(True)

#     main.pre_s_units_CB.setEnabled(True)
#     main.pre_s_desc_T.setEnabled(True)

#     main.wind_units_CB.setEnabled(True)
#     main.wind_desc_T.setEnabled(True)

#     main.gust_units_CB.setEnabled(True)
#     main.gust_desc_T.setEnabled(True)

#     main.dir_units_CB.setEnabled(True)
#     main.dir_desc_T.setEnabled(True)

#     main.p_units_CB.setEnabled(True)
#     main.p_desc_T.setEnabled(True)

#     main.psea_units_CB.setEnabled(True)
#     main.psea_desc_T.setEnabled(True)

#     main.build_B.setEnabled(True)


def make_template_build(main):
      # 1 Make dict of obstypes to write in the template
      obsmapper = {}
      for mapped_column, mapped_info in main.session['mapping']['mapped_obstypes'].items():
          obstype = mapped_info['obstype']
          obsmapper[obstype.name] = {'map_column': mapped_column,
                                     'map_unit': mapped_info['unit'],
                                     'map_desc': obstype.get_description()
                                      }

      print(obsmapper)

      # 2 make dict for datetime mapping
      dtmapper = {} #for datetimes
      for dttype, dtinfo in main.session['mapping']['mapped_datetime'].items():
          if dtinfo['columnname'] is not None:
              # Renaming is requirded for data and time
              if dttype == 'date': keyname='_date'
              if dttype == 'time': keyname='_time'
              if dttype == 'datetime': keyname='datetime'

              dtmapper[keyname] = {
                                  'map_column': dtinfo['columnname'],
                                  'map_fmt': dtinfo['fmt']
                                  }


      print(dtmapper)

      # 3 make dict for metadata mapping
      metamapper = {}
      for colname, metatype in main.session['mapping']['mapped_metadata'].items():
          metamapper[metatype] = {'map_column': colname}

      # 4. add name mapping
      namemapper = {}
      namemapper['name'] = main.session['mapping']['mapped_name']

      # 5. optionsmapper
      # Options to dict
      possible_options = {'data_structure': None, #['long', 'wide', 'single_station'],
                          'stationname': None, #'_any_',
                          'obstype': None, #observation_types,
                          'obstype_unit': None, #'_any_',
                          'obstype_description' : None, # '_any_',
                          'timezone': None, #all_timezones
                          }
      # format
      fmtdict= {'long': 'long',
                'wide':'wide',
                'single-station': 'single_station'}

      possible_options['data_structure'] = fmtdict[str(main.browse_format.currentText())]
      possible_options['stationname'] = str(main.stationname.text())
      possible_options['timezone'] = str(main.timezone_spinner.currentText())

      if possible_options['data_structure'] == 'wide':
          possible_options['obstype'] = str(main.wide_obs_type.currentText())
          possible_options['obstype_unit'] = str(main.wide_unit.currentText())
          possible_options['obstype_description'] = str(main.wide_obs_desc.text())


      # empty textedit is represented by empty string, convert to none
      for key, val in possible_options.items():
          if val == '':
              possible_options[key] = None
      filtered_opt = {key: val for key, val in possible_options.items() if not val is None}

      options_dict = {'options' : list(filtered_opt.keys()),
                      'options_values': list(filtered_opt.values())}
      options_df = pd.DataFrame(options_dict)
      print(f'OPTIONS df: \n {options_df}')




      # 6. check if mapping is valid
      template_ok = test_template(main, obsmapper, metamapper, namemapper, dtmapper, filtered_opt)

      if not template_ok:
          return None, False #succes = False




      # 2. Convert to a dataframe
      def to_dataframe(mapper):
          df = pd.DataFrame(mapper).transpose()
          df.index.name = 'varname'
          df = df.dropna(axis = 0, how = 'all')
          df = df.reset_index()
          df = df.rename(columns={'map_column': 'template column name',
                                  'map_unit': 'units',
                                  'map_desc': 'description',
                                  'map_fmt': 'format'})
          return df

      mapdf = pd.concat([to_dataframe(dtmapper),
                         to_dataframe(metamapper),
                         to_dataframe(obsmapper)])
      # add name:

      mapdf = pd.concat([mapdf, pd.Series({'varname':'name', 'template column name': namemapper['name']}).to_frame().transpose()])
      print('mapdf1: ', mapdf)
      mapdf = mapdf.reset_index(drop=True)
      mapdf = pd.concat([mapdf,options_df], ignore_index=False, axis=1) #add optionscolumns
      print('mapdf return: ', mapdf)
      return mapdf, True



def test_template(main, obsmapper, metamapper, namemapper, dtmapper, optionsmapper):
    data_head = main.session['mapping']['data_head']
    data_cols = main.session['mapping']['data_cols']

    if main.use_metadata.isChecked():
        metadata_head = main.session['mapping']['metadata_head']
        metadata_cols = main.session['mapping']['metadata_cols']


    fmt = optionsmapper['data_structure'] # long, wide or single_station
    namecol = namemapper['name']


    if (fmt == 'long') :
        # name must be in the data file as column
        if not namecol in data_cols:
            Error('Invalid mapping', f'The name column "{namecol}" is not found as a column in the data file! ')
            return False
    if (fmt == 'long') | (fmt == 'single_station'):
        if main.use_metadata.isChecked():
            if not namecol in metadata_cols:
                # a) if metadata is given, and format is long, check if name column is present in both datafiles
                Error('Invalid mapping', f'The name column "{namecol}" is not found as a column in the metadata file! ')
                return False

        # b) check if at least one obstype is mapped
        mapped_obs = [key for key, item in obsmapper.items() if isinstance(item['map_column'], str)]
        if len(mapped_obs) < 1 :
            Error('Invalid mapping', f'None observation type is mapped! ')
            return False


    # check datetimemapping
    mapped_dt = [key for key, item in dtmapper.items() if isinstance(item['map_column'], str)]

    if len(mapped_dt) == 0:
        Error('Invalid mapping', f'None datetime mapping is provided.')
        return False
    if len(mapped_dt) == 1:
        if mapped_dt[0] =='datetime':
            # test datetime format
            dt_head = data_head[dtmapper['datetime']['map_column']]
            dtfmt = dtmapper['datetime']['map_fmt']
            try:
                pd.to_datetime(dt_head, format=dtfmt)
            except:
                Error('Invalid mapping', f' {dtfmt} is not valid for the timestamps in the data ({dt_head[0:3].to_list()}, ...)')
                return False
        else:
            Error('Invalid mapping', f'When one timestamp column is used, it must represent the datetime and not the {mapped_dt[0]}')
            return False
    if len(mapped_dt) == 2:
        if (not '_date' in mapped_dt) | (not '_time' in mapped_dt):
            Error('Invalid mapping', f'When two columns are use to indicate timestamps, one must be a "date" and the other a "time" representation.')
            return False
        # test datetime format
        date_head = data_head[dtmapper['_date']['map_column']]
        time_head = data_head[dtmapper['_time']['map_column']]

        datefmt = dtmapper['_date']['map_fmt']
        timefmt = dtmapper['_time']['map_fmt']

        try:
            pd.to_datetime(date_head, format=datefmt)
        except:
            Error('Invalid mapping', f' {datefmt} is not valid for the column representing the dates in the data ({date_head[0:3].to_list()}, ...)')
            return False
        try:
            pd.to_datetime(time_head, format=timefmt)
        except:
            Error('Invalid mapping', f' {timefmt} is not valid for the column representing the timestamps in the data ({time_head[0:3].to_list()}, ...)')
            return False
    if len(mapped_dt) > 2:
        Error('Invalid mapping', f'Invalid combination of datetime indicators: {mapped_dt}')
        return False

    # check wide data
    if (fmt == 'wide'):
        print(optionsmapper)
        if not 'obstype_unit' in optionsmapper.keys():
            Error('Invalid mapping', f'(wide - format) Specify the observation units for the {optionsmapper["obstype"]} records.')
            return False

        if not 'obstype_description' in optionsmapper.keys():
            Error('Invalid mapping', f'(wide - format) Specify the observation description for the {optionsmapper["obstype"]} records.')
            return False

    if (fmt == 'single_station'):
        print('single station !!!!!!!')
        if not 'stationname' in optionsmapper:
            Error('Invalid mapping', f'(single station - format) Specify the name of the station.')
            return False


    return True



def get_all_templates():
    """
    Returns a dict with keys the filenames of all available templates and keys the full paths.
    :return: DESCRIPTION
    :rtype: dict

    """
    template_dict = {}

    # default templates
    template_dict['default_template.csv'] = path_handler.tlk_default_template

    # all templates in cache
    filenames, filepaths = path_handler.list_filenames(path_handler.template_dir,
                                                       fileextension='.csv')

    template_dict.update(dict(zip(filenames, filepaths)))

    return template_dict









