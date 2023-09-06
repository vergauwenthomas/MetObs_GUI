#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 31 09:40:08 2023

@author: thoverga
"""

#%% Load vlinder toolkit (not shure what is best)
import sys
from io import StringIO

from PyQt5.QtWidgets import QSpinBox, QDoubleSpinBox


import metobs_gui.path_handler as path_handler
from metobs_gui.errors import Error, Notification
# method1: add the toolkit to path,
# sys.path.append(path_handler.TLK_dir)
# from vlinder_toolkit import Dataset

# method2: loead as package
# print('CHANGE THE TOOLKIT PACKAGE LOCATION !!')
# debug_path = '/home/thoverga/Documents/VLINDER_github/MetObs_toolkit'
# sys.path.insert(0, debug_path)
import metobs_toolkit



#%% Mapping
# when specific manipulation has to be done on values

tlk_to_gui = {
    'window_variation__max_increase_per_second': {'multiply': 3600.0},
    'window_variation__max_decrease_per_second' : {'multiply': 3600.0},
    'step__max_increase_per_second' : {'multiply': 3600.0},
    'step__max_decrease_per_second' : {'multiply': 3600.0},

    'persistance__time_window_to_check': {'remove': 'h'},
    'window_variation__time_window_to_check': {'remove': 'h'},
}


gui_to_tlk = {
    'window_variation__max_increase_per_second': {'devide': 3600.0},
    'window_variation__max_decrease_per_second' : {'devide': 3600.0},
    'step__max_increase_per_second' : {'devide': 3600.0},
    'step__max_decrease_per_second' : {'devide': 3600.0},

    'persistance__time_window_to_check': {'append': 'h'},
    'window_variation__time_window_to_check': {'append': 'h'},
}

def _append(x, val):
    return str(x)+str(val)
def _div(x, val):
    return float(x)/float(val)
def _multiply(x, val):
    return float(x) * float(val)
def _remove(x, val):
    return str(x).replace(str(val), '')


qc_not_in_gui = ['duplicated_timestamp', 'internal_consistency'] #not present in gui

#%% Helpers

class CapturingPrint(list):
    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self
    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        del self._stringio    # free up some memory
        sys.stdout = self._stdout

# class Capturing_logs(list):
#     def __enter__(self):
#         self._stderr = sys.stderr
#         sys.stderr = self._stringio_err = StringIO()
#         return self
#     def __exit__(self, *args):
#         self.extend(self._stringio_err.getvalue().splitlines())
#         del self._stringio_err    # free up some memory
#         sys.stderr = self._stderr



#%%

# =============================================================================
# Dataset methods
# =============================================================================


def import_dataset_from_file(data_path, metadata_path, template_path,
                             freq_est_method,
                             freq_est_simplyfy,
                             freq_est_simplyfy_toll,
                             kwargs_data,
                             kwargs_metadata,
                             gap_def,
                             sync, sync_tol,
                             sync_force,
                             sync_force_freq):

    try:
        # init dataset
        dataset = metobs_toolkit.Dataset()
        dataset.update_settings(input_data_file=data_path,
                                input_metadata_file=metadata_path,
                                template_file=template_path,
                                )
        # update gap defenition
        dataset.update_qc_settings(gapsize_in_records=int(gap_def))

    except Exception as e:

        error_msg = str(e)
        return None, False, ['Dataset initialisation and settings update',
                             error_msg]


    # import data
    try:


        dataset.import_data_from_file(freq_estimation_method = freq_est_method,
                                      freq_estimation_simplify = freq_est_simplyfy,
                                      freq_estimation_simplify_error=freq_est_simplyfy_toll,
                                      kwargs_data_read=kwargs_data,
                                      kwargs_metadata_read=kwargs_metadata)

    except Exception as e:
        error_msg = str(e)
        return None, False, ['Dataset importing data', error_msg]

    # syncronize
    if sync:
        try:
            if sync_force:
                dataset.sync_observations(tollerance = sync_tol,
                                      verbose=True,
                                      _force_resolution_minutes=sync_force_freq,
                                      _drop_target_nan_dt=False)
            else:

                dataset.sync_observations(tollerance = sync_tol,
                                      verbose=True,
                                      _force_resolution_minutes=None,
                                      _drop_target_nan_dt=False)
        except Exception as e:
            error_msg = str(e)
            return None, False, ['Dataset syncronization', error_msg]


    return dataset, True, ['error_theme', 'error_msg']


def coarsen_timeres(dataset, target_freq, origin, method):
    try:

        dataset.coarsen_time_resolution(origin=origin,
                                        freq=target_freq,
                                        method=method)
    except Exception as e:
        error_msg = str(e)
        return None, False, ['Dataset coarsen timeresolution', error_msg]


    return dataset, True, ['error_theme', 'error_msg']


def import_dataset_from_pkl(pkl_name, pkl_folder):
    print('A')
    print(f'folder_path={pkl_folder},filename={pkl_name}')
    try:
        dataset = metobs_toolkit.Dataset()
        dataset = dataset.import_dataset(folder_path=pkl_folder,
                                         filename=pkl_name)
        print('B')
    except Exception as e:
        error_msg = str(e)
        return None, False, ['Dataset import from pkl',
                            error_msg]

    return dataset, True, ['error_theme', 'error_msg']


def save_dataset_to_pkl(dataset, pkl_name, pkl_folder):
    try:
        dataset.save_dataset(outputfolder=pkl_folder,
                             filename=pkl_name)
    except Exception as e:
        error_msg = str(e)
        return None, False, ['Dataset save to pkl',
                             error_msg]
    return None, True, ['error_theme', 'error_msg']



def get_dataset_info(dataset):
    with CapturingPrint() as infolist:
        dataset.get_info()
    return infolist





def combine_to_obsspace(dataset):
    try:
        comb_df = dataset.combine_all_to_obsspace()
    except Exception as e:
        error_msg = str(e)
        return None, False, ['Combine dataset to observation-space',
                             error_msg]
    return comb_df, True, ['error_theme', 'error_msg']



def get_altitude(dataset):
    try:
        with CapturingPrint() as infolist:
            dataset.get_altitude()
    except Exception as e:
        error_msg = str(e)
        return False, 'ERROR', ['Get altidude error',
                       error_msg]
    return True, infolist, ['error_theme', 'error_msg']


def get_lcz(dataset):
    try:
        with CapturingPrint() as infolist:
            dataset.get_lcz()
    except Exception as e:
        error_msg = str(e)
        return False, 'ERROR', ['Get lcz error',
                       error_msg]
    return True, infolist, ['error_theme', 'error_msg']


def get_landcover(dataset, buffers, aggbool, gee_map, overwrite=True):
    try:
        with CapturingPrint() as infolist:
            _ = dataset.get_landcover(buffers=buffers,
                                      aggregate=aggbool,
                                      gee_map=gee_map,
                                      overwrite=overwrite)
    except Exception as e:
        error_msg = str(e)
        return False, 'ERROR', ['Get landcover error',
                       error_msg]
    return True, infolist, ['error_theme', 'error_msg']


def update_qc_stats (dataset, obstype='temp', gapsize_in_records=None,
                     dupl_timestamp_keep=None, persis_time_win_to_check=None,
                     persis_min_num_obs=None, rep_max_valid_repetitions=None,
                     gross_value_min_value=None, gross_value_max_value=None,
                     win_var_max_increase_per_sec=None,
                     win_var_max_decrease_per_sec=None,
                     win_var_time_win_to_check=None,
                     win_var_min_num_obs=None,
                     step_max_increase_per_sec=None,
                     step_max_decrease_per_sec=None,
                     buddy_radius=None,
                     buddy_num_min=None,
                     buddy_threshold=None,
                     buddy_max_elev_diff=None,
                     buddy_elev_gradient=None,
                     buddy_min_std=None,
                     buddy_debug=None):

    try:
        with CapturingPrint() as infolist:
            dataset.update_qc_settings(obstype=obstype,
                                       gapsize_in_records=gapsize_in_records,
                                       dupl_timestamp_keep=dupl_timestamp_keep,
                                       persis_time_win_to_check=persis_time_win_to_check,
                                       persis_min_num_obs=persis_min_num_obs,
                                       rep_max_valid_repetitions=rep_max_valid_repetitions,
                                       gross_value_min_value=gross_value_min_value,
                                       gross_value_max_value=gross_value_max_value,
                                       win_var_max_increase_per_sec=win_var_max_increase_per_sec,
                                       win_var_max_decrease_per_sec=win_var_max_decrease_per_sec,
                                       win_var_time_win_to_check=win_var_time_win_to_check,
                                       win_var_min_num_obs=win_var_min_num_obs,
                                       step_max_increase_per_sec= step_max_increase_per_sec,
                                       step_max_decrease_per_sec=step_max_decrease_per_sec,
                                       buddy_radius=buddy_radius,
                                       buddy_min_sample_size=buddy_num_min,
                                       buddy_max_elev_diff=buddy_max_elev_diff,
                                       buddy_min_std=buddy_min_std,
                                       buddy_threshold=buddy_threshold,
                                       buddy_elev_gradient=buddy_elev_gradient)

            # dataset.update_titan_qc_settings(
            #                     obstype=obstype,
            #                     buddy_radius=buddy_radius,
            #                     buddy_num_min=buddy_num_min,
            #                     buddy_threshold=buddy_threshold,
            #                     buddy_max_elev_diff=buddy_max_elev_diff,
            #                     buddy_elev_gradient=buddy_elev_gradient,
            #                     buddy_min_std=buddy_min_std,
            #                     buddy_num_iterations=buddy_num_iterations,
            #                     buddy_debug=buddy_debug,
            #                     )

    except Exception as e:
        error_msg = str(e)
        return False, 'ERROR', ['update QC settings error',
                       error_msg]


    return True, infolist, ['error_theme', 'error_msg']

def apply_qc(dataset, obstype,
             gross_value, persistance,
             repetitions, step, window_variation):

    try:
        with CapturingPrint() as infolist:
            dataset.apply_quality_control(obstype=obstype,
                                          gross_value=gross_value,
                                          persistance=persistance,
                                          repetitions=repetitions,
                                          step=step,
                                          window_variation=window_variation)



    except Exception as e:
        error_msg = str(e)
        return False, 'ERROR', ['Apply quality control error',
                       error_msg]


    return True, infolist, ['error_theme', 'error_msg']

def apply_buddy(dataset, obstype, use_constant_altitude, haversine_approx,
                metric_epsg):

    try:
        with CapturingPrint() as infolist:
            dataset.apply_buddy_check(obstype=obstype,
                                      use_constant_altitude=False,
                                      haversine_approx=haversine_approx,
                                      metric_epsg=metric_epsg)


    except Exception as e:
        error_msg = str(e)
        return False, 'ERROR', ['Apply buddy check error',
                       error_msg]


    return True, infolist, ['error_theme', 'error_msg']
# def apply_titan_buddy(dataset, obstype, use_constant_altitude):

#     try:
#         with CapturingPrint() as infolist:
#             dataset.apply_titan_buddy_check(obstype=obstype,
#                                             use_constant_altitude=False)


#     except Exception as e:
#         error_msg = str(e)
#         return False, 'ERROR', ['Apply titan buddy check error',
#                        error_msg]


#     return True, infolist, ['error_theme', 'error_msg']




def make_html_gee_map(dataset, html_path):
    try:
        with CapturingPrint() as infolist:
            _ = dataset.make_gee_plot(gee_map='worldcover',
                                      show_stations=True,
                                      save=True,
                                      outputfile = html_path)


    except Exception as e:
        error_msg = str(e)
        return False, 'ERROR', ['Creating html map error',
                       error_msg]


    return True, infolist, ['error_theme', 'error_msg']




def update_gap_and_missing_fill(dataset, gap_interpolation_method=None,
                                gap_interpolation_max_consec_fill=None,
                                gap_debias_prefered_leading_period_hours=None,
                                gap_debias_prefered_trailing_period_hours=None,
                                gap_debias_minimum_leading_period_hours=None,
                                gap_debias_minimum_trailing_period_hours=None,
                                automatic_max_interpolation_duration_str=None,
                                missing_obs_interpolation_method=None):
    try:
        with CapturingPrint() as infolist:
            dataset.update_gap_and_missing_fill_settings(
                    gap_interpolation_method=gap_interpolation_method,
                    gap_interpolation_max_consec_fill=gap_interpolation_max_consec_fill,
                    gap_debias_prefered_leading_period_hours=gap_debias_prefered_leading_period_hours,
                    gap_debias_prefered_trailing_period_hours=gap_debias_prefered_trailing_period_hours,
                    gap_debias_minimum_leading_period_hours=gap_debias_minimum_leading_period_hours,
                    gap_debias_minimum_trailing_period_hours=gap_debias_minimum_trailing_period_hours,
                    automatic_max_interpolation_duration_str=automatic_max_interpolation_duration_str,
                    missing_obs_interpolation_method=missing_obs_interpolation_method)


    except Exception as e:
        error_msg = str(e)
        return dataset, False, 'ERROR', ['Updating gaps and missing fill settings',
                       error_msg]


    return dataset, True, infolist, ['error_theme', 'error_msg']

def convert_outliers_to_missing_and_gaps(dataset, obstype, ngapsize):
    try:
        with CapturingPrint() as infolist:
            dataset.update_gaps_and_missing_from_outliers(
                            obstype=obstype,
                            n_gapsize=ngapsize)

    except Exception as e:
        error_msg = str(e)
        return dataset, False, 'ERROR', ['Updating outliers to missing and gaps',
                       error_msg]


    return dataset, True, infolist, ['error_theme', 'error_msg']

def interpolate_gaps(dataset, obstype, overwrite):
    try:
        with CapturingPrint() as infolist:
            dataset.fill_gaps_linear(obstype=obstype,
                                     overwrite_fill=overwrite)

    except Exception as e:
        error_msg = str(e)
        return dataset, False, 'ERROR', ['Fill gaps linear',
                       error_msg]


    return dataset, True, infolist, ['error_theme', 'error_msg']

def debias_fill_gaps(dataset, modeldata, method,  obstype, overwrite):
    try:
        with CapturingPrint() as infolist:
            _ = dataset.fill_gaps_era5(modeldata=modeldata,
                                       obstype=obstype,
                                       overwrite_fill=overwrite)

    except Exception as e:
        error_msg = str(e)
        return dataset, False, 'ERROR', ['Fill gaps debias Modeldata',
                       error_msg]


    return dataset, True, infolist, ['error_theme', 'error_msg']

def automatic_fill_gaps(dataset, modeldata, max_interp_dur_str, obstype, overwrite):
    try:
        with CapturingPrint() as infolist:
            _ = dataset.fill_gaps_automatic(
                        modeldata=modeldata,
                        obstype=obstype,
                        max_interpolate_duration_str=max_interp_dur_str,
                        overwrite_fill=overwrite)

    except Exception as e:
        error_msg = str(e)
        return dataset, False, 'ERROR', ['Fill gaps automatic',
                       error_msg]


    return dataset, True, infolist, ['error_theme', 'error_msg']



def fill_missing_observations(dataset, obstype):
    try:
        with CapturingPrint() as infolist:
            dataset.fill_missing_obs_linear(obstype=obstype)

    except Exception as e:
        error_msg = str(e)
        return dataset, False, 'ERROR', ['Fill missing observations linear',
                       error_msg]


    return dataset, True, infolist, ['error_theme', 'error_msg']


def get_missing_obs_info(dataset):
    try:
        with CapturingPrint() as infolist:
            dataset.get_missing_obs_info()

    except Exception as e:
        error_msg = str(e)
        return False, 'ERROR', ['Missing obs info',
                       error_msg]


    return True, infolist, ['error_theme', 'error_msg']

def get_gaps_info(dataset):
    try:
        with CapturingPrint() as infolist:
            dataset.get_gaps_info()

    except Exception as e:
        error_msg = str(e)
        return False, 'ERROR', ['Gaps info',
                       error_msg]


    return True, infolist, ['error_theme', 'error_msg']



# =============================================================================
# Modeldata methods
# =============================================================================


def get_modeldata(dataset, modelname, modeldata, obstype, stations, startdt, enddt):
    try:
        with CapturingPrint() as infolist:
            model = dataset.get_modeldata(modelname=modelname,
                                              modeldata=modeldata,
                                              obstype=obstype,
                                              stations=stations,
                                              startdt=startdt,
                                              enddt=enddt)


    except Exception as e:
        error_msg = str(e)
        return None, False, 'ERROR', [f'Extracting {modelname} from GEE',
                       error_msg]


    return model, True, infolist, ['error_theme', 'error_msg']

def import_modeldata(folder, pkl_file):
    try:
        with CapturingPrint() as infolist:
            empty_modeldata = metobs_toolkit.Modeldata('ERA5_hourly')
            modeldata = empty_modeldata.import_modeldata(folder_path=folder,
                                                         filename=pkl_file)



    except Exception as e:
        error_msg = str(e)
        return None, False, 'ERROR', [f'Importing modeldata to pkl',
                       error_msg]


    return modeldata, True, infolist, ['error_theme', 'error_msg']



def save_modeldata(modeldata, outputfolder, outputfile):
    try:
        with CapturingPrint() as infolist:
            modeldata.save_modeldata(outputfolder=outputfolder,
                                     filename=outputfile)


    except Exception as e:
        error_msg = str(e)
        return False, 'ERROR', [f'Saving modeldata to pkl',
                       error_msg]


    return True, infolist, ['error_theme', 'error_msg']

def import_modeldata_from_csv(modelname, csvpath):
    try:
        with CapturingPrint() as infolist:
            modeldata = metobs_toolkit.Modeldata(modelname)
            modeldata.set_model_from_csv(csvpath=csvpath)

    except Exception as e:
        error_msg = str(e)
        return None, False, 'ERROR', [f'Importing model from csv',
                       error_msg]


    return modeldata, True, infolist, ['error_theme', 'error_msg']


def get_modeldata_info(modeldata):
    return str(modeldata)

def conv_modeldata_units(modeldata, obstype, target_unit, expression):
    try:
        with CapturingPrint() as infolist:

            modeldata.convert_units_to_tlk(obstype=obstype,
                                           target_unit_name=target_unit,
                                           conv_expr=expression)

    except Exception as e:
        error_msg = str(e)
        return modeldata, False, 'ERROR', [f'Converting unit error.',
                       error_msg]


    return modeldata, True, infolist, ['error_theme', 'error_msg']



# =============================================================================
# Analysis stuff
# =============================================================================

def create_analysis_instance(dataset, add_gapfilled_values):
    try:
        with CapturingPrint() as infolist:
            ana = dataset.get_analysis(add_gapfilled_values=add_gapfilled_values)
    except Exception as e:
        error_msg = str(e)
        return None, False, 'ERROR', [f'Creating Analysis', error_msg]

    return ana, True, infolist, ['error_theme', 'error_msg']




def apply_filter_on_analysis(analysis, filterstring):
    try:
        with CapturingPrint() as infolist:
            ana = analysis.apply_filter(expression=filterstring)
    except Exception as e:
        error_msg = str(e)
        return analysis, False, 'ERROR', [f'Filtering Analysis', error_msg]

    return ana, True, infolist, ['error_theme', 'error_msg']




def apply_diurnal_cycle_without_ref(analysis, colorby, obstype, startdt,
                                    enddt, plot=True,
                                    stations=None,
                                    title=None, y_label=None, legend=True,
                                    errorbands=False,
                                    ):

    try:
        with CapturingPrint() as infolist:
            stats, all_stats, ax= analysis.get_diurnal_statistics(colorby=colorby, obstype=obstype,
                                                                  stations=stations, startdt=startdt,
                                                                  enddt=enddt, plot=plot,
                                                                  title=title, y_label=y_label, legend=legend,
                                                                  errorbands=errorbands,
                                                                  _return_all_stats=True) #True so the axes is returned
            all_stats.columns = all_stats.columns.to_flat_index()
    except Exception as e:
        error_msg = str(e)
        return None, None, None, False, 'ERROR', [f'Analysis diurnal cycle', error_msg]

    return stats, all_stats, ax, True, infolist, ['error_theme', 'error_msg']



def apply_diurnal_cycle_with_ref(analysis, colorby, obstype, startdt,
                                 tollerance, refstation,
                                 enddt, plot=True,
                                 stations=None,
                                 title=None, y_label=None, legend=True,
                                 errorbands=False,
                                 ):

    try:
        with CapturingPrint() as infolist:
            stats, all_stats, ax= analysis.get_diurnal_statistics_with_reference(colorby=colorby, obstype=obstype,
                                                                                 tollerance=tollerance,
                                                                                 refstation=refstation,
                                                                                 stations=stations, startdt=startdt,
                                                                                 enddt=enddt, plot=plot,
                                                                                 title=title, y_label=y_label, legend=legend,
                                                                                 errorbands=errorbands,
                                                                                 _return_all_stats=True) #True so the axes is returned
            all_stats.columns = all_stats.columns.to_flat_index()
    except Exception as e:
        error_msg = str(e)
        return None, None, None, False, 'ERROR', [f'Analysis diurnal cycle with ref', error_msg]

    return stats, all_stats, ax, True, infolist, ['error_theme', 'error_msg']

def apply_anual_cycle(analysis, groupby, obstype,
                             agg_method,
                             startdt, enddt, plot=True,
                             stations=None,
                             errorbands=False, title=None, y_label=None,
                             legend=True):

    try:
        with CapturingPrint() as infolist:
            stats, all_stats, ax= analysis.get_anual_statistics(groupby=groupby,
                                                                obstype=obstype,
                                                                agg_method=agg_method,
                                                                stations=stations,
                                                                startdt=startdt,
                                                                enddt=enddt,
                                                                plot=plot,
                                                                title=title,
                                                                y_label=y_label,
                                                                legend=legend,
                                                                errorbands=errorbands,
                                                                _return_all_stats=True) #True so the axes is returned
            all_stats.columns = all_stats.columns.to_flat_index()
    except Exception as e:
        error_msg = str(e)
        return None, None, None, False, 'ERROR', [f'Analysis anual cycle', error_msg]

    return stats, all_stats, ax, True, infolist, ['error_theme', 'error_msg']


def apply_custom_cycle(analysis, obstype, aggregation,
                       aggregation_method, horizontal_axis,
                       startdt, enddt,
                       stations=None, plot=True,
                       title=None, y_label=None, legend=True,
                       errorbands=False, verbose=True,
                       _obsdf=None, _show_zero_line=False):

    try:
        with CapturingPrint() as infolist:
            stats, all_stats, ax= analysis.get_aggregated_cycle_statistics(
                                                    obstype=obstype,
                                                    aggregation=aggregation,
                                                    aggregation_method=aggregation_method,
                                                    horizontal_axis=horizontal_axis,
                                                    startdt=startdt,
                                                    enddt=enddt,
                                                    stations=stations,
                                                    plot=plot,
                                                    title=title, y_label=y_label, legend=legend,
                                                    errorbands=errorbands, verbose=True, #True so the axes is returned
                                                    _obsdf=_obsdf, _show_zero_line=_show_zero_line)




            all_stats.columns = all_stats.columns.to_flat_index()
    except Exception as e:
        error_msg = str(e)
        return None, None, None, False, 'ERROR', [f'Analysis custom cycle', error_msg]

    return stats, all_stats, ax, True, infolist, ['error_theme', 'error_msg']



def get_lc_cor_info(analysis, obstype, groupby_labels):
    try:
        with CapturingPrint() as infolist:
            cor_dict = analysis.get_lc_correlation_matrices(
                                    obstype=obstype,
                                    groupby_labels=groupby_labels)

    except Exception as e:
        error_msg = str(e)
        return None, False, 'ERROR', [f'Analysis get landcover correlations', error_msg]
    return cor_dict, True, infolist, ['error_theme', 'error_msg']



def create_cor_figure(analysis, groupby_value, title=None):
    try:
        with CapturingPrint() as infolist:
            ax = analysis.plot_correlation_heatmap(groupby_value=groupby_value,
                                                         title=title,
                                                         _return_ax=True
                                                         )

    except Exception as e:
        error_msg = str(e)
        return None, False, 'ERROR', [f'Analysis heatmap plot of landcover correlations', error_msg]
    return ax, True, infolist, ['error_theme', 'error_msg']

def make_scatter_cor_plot(analysis):
    try:
        with CapturingPrint() as infolist:
            ax = analysis.plot_correlation_variation()

    except Exception as e:
        error_msg = str(e)
        return None, False, 'ERROR', [f'Analysis scatter plot of landcover correlations variation', error_msg]
    return ax, True, infolist, ['error_theme', 'error_msg']



#%% Toolkit functions





