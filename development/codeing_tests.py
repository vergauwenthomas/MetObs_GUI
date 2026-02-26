#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 18 14:55:36 2024

@author: thoverga
"""

import sys, os
sys.path.insert(0, '/home/thoverga/Documents/VLINDER_github/MetObs_toolkit')
import metobs_toolkit


print(metobs_toolkit.__version__)


#%%

inputdata = '/home/thoverga/Desktop/siebe_toolkit_scripts/Siebe_2024.csv'
inputmetadata = '/home/thoverga/Desktop/siebe_toolkit_scripts/GPS meetpunten GENK.csv'
inputtemplate='/home/thoverga/Documents/VLINDER_github/MetObs_GUI/metobs_gui/cache/templates/siebe_template.json'




dataset = metobs_toolkit.Dataset()


dataset.import_data_from_file(input_data_file=metobs_toolkit.demo_datafile,
                              input_metadata_file=metobs_toolkit.demo_metadatafile,
                              template_file=metobs_toolkit.demo_template)

era5 = metobs_toolkit.default_GEE_datasets['ERA5-land']

era5file = "/home/thoverga/Documents/VLINDER_github/MetObs_toolkit/tests/data/ERA5-land_timeseries_data_of_full_dataset_28_stations.csv"

dataset.import_gee_data_from_file(filepath=era5file,
                                  gee_dynamic_manager=era5,
                                  )

dataset


def find_present_modeldetails(dataset) -> dict: 

    #create dict of modelnames and variables
    modeltargets = {}

    for sta in dataset.stations:
        for modelseries in sta.modeldata:
            if modelseries.modelname not in modeltargets:
                modeltargets[modelseries.modelname] = []
            modeltargets[modelseries.modelname].append(modelseries.modelvariable)


    for modelname in modeltargets.keys():
        modeltargets[modelname] = list(set(modeltargets[modelname]))


    return modeltargets

# dataset.gee_datasets['ERA5-land'].make_plot(obstype_model=obstype_model,
#                                      Dataset = dataset,
#                                      obstype_dataset=obstype_dataset,
#                                      stationnames=stationnames,
#                                      starttime=None,
#                                      endtime=None,
#                                      title=None,
#                                      show_outliers=show_outliers,
#                                      show_filled=True,
#                                      legend=True,
                                     # _ax=self.axes)
#%%

