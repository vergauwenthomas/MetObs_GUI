#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 25 10:27:04 2023

@author: thoverga
"""


from datetime import datetime
from metobs_gui.errors import Error, Notification
import metobs_gui.tlk_scripts as tlk_scripts

from metobs_gui.extra_windows import make_a_cycle_plot, show_cycle_stats_df, make_a_heatmap_plot, show_cor_matix_df


# =============================================================================
# Init page
# =============================================================================

def init_analysis_page(MW):
    # no initialisation required


    MW.startdt_check_diurnal.clicked.connect(MW.enddt_check_diurnal.setCheckState) #link them
    MW.enddt_check_diurnal.clicked.connect(MW.startdt_check_diurnal.setCheckState) #link them

    MW.startdt_check_anual.clicked.connect(MW.enddt_check_anual.setCheckState) #link them
    MW.enddt_check_anual.clicked.connect(MW.startdt_check_anual.setCheckState) #link them

    MW.startdt_check_custom.clicked.connect(MW.enddt_check_custom.setCheckState) #link them
    MW.enddt_check_custom.clicked.connect(MW.startdt_check_custom.setCheckState) #link them

    return



# =============================================================================
# setup (triggers)
# =============================================================================

def activate_analysis_widgets(MW, setvalue=True):
    to_activate_list = [MW.filter_query, MW.apply_filter,
                        MW.obstype_diurnal, MW.groupby_diurnal, MW.refstation, MW.ref_tollerance, MW.plot_diurnal,
                        MW.obstype_anual, MW.groupby_anual, MW.agg_method_anual, MW.plot_anual,
                        MW.obstype_custom, MW.groupdef_custom, MW.agg_method_custom, MW.haxis_custom, MW.plot_custom,

                        MW.cor_obstype, MW.cor_group_def, MW.get_cor]


    for widg in to_activate_list:
        widg.setEnabled(setvalue)



def set_values_for_spinners(MW):
    possible_obstypes = list(MW.analysis.df.columns)

    timegroups = ['hour', 'minute', 'month', 'year', 'day_of_year', 'week_of_year', 'season']
    metadata_groups = list(MW.analysis.metadf.columns)
    extra_groups = ['name']

    possible_ref_stations = list(MW.analysis.df.index.get_level_values('name').unique())


    diurnal_groupby = ['name', 'lcz']

    agg_methods = ['mean', 'min', 'max', 'std', 'median']

    anual_groupby = []
    anual_groupby.extend(timegroups)
    anual_groupby.extend(metadata_groups)
    anual_groupby.extend(extra_groups)



    # Set obstype spinners:
    obstype_widgets = [MW.obstype_diurnal, MW.obstype_anual, MW.obstype_custom, MW.cor_obstype]
    for obs_spin in obstype_widgets:
        obs_spin.clear()
        obs_spin.addItems(possible_obstypes)

    # groupby spinners
    MW.groupby_diurnal.clear()
    MW.groupby_diurnal.addItems(diurnal_groupby)

    MW.groupby_anual.clear()
    MW.groupby_anual.addItems(anual_groupby)

    # agg method spinner
    MW.agg_method_anual.clear()
    MW.agg_method_anual.addItems(agg_methods)

    MW.agg_method_custom.clear()
    MW.agg_method_custom.addItems(agg_methods)

    # haxis elements
    update_horizontal_axis_possibilities(MW)

    # refstations
    MW.refstation.clear()
    MW.refstation.addItems(possible_ref_stations)






def update_horizontal_axis_possibilities(MW):
    groupdef_str = str(MW.groupdef_custom.text())
    groupdef_list = groupdef_str.replace(' ','').split(',')

    MW.haxis_custom.clear()
    MW.haxis_custom.addItems(groupdef_list)


def activate_cor_plots(MW, setvalue=True):
    for widg in [MW.make_heat_plot, MW.make_scatter_plot, MW.show_cor_matrix, MW.heat_cor_group]:
        widg.setEnabled(setvalue)






def dirunal_start_end(MW):
    if MW.startdt_check_diurnal.isChecked():
        setactive = True
    else:
        setactive=False

    for widg in [MW.startdt_diurnal, MW.enddt_diurnal]:
        widg.setEnabled(setactive)

def anual_start_end(MW):
    if MW.startdt_check_anual.isChecked():
        setactive = True
    else:
        setactive=False

    for widg in [MW.startdt_anual, MW.enddt_anual]:
        widg.setEnabled(setactive)

def custom_start_end(MW):
    if MW.startdt_check_custom.isChecked():
        setactive = True
    else:
        setactive=False

    for widg in [MW.startdt_custom, MW.enddt_custom]:
        widg.setEnabled(setactive)


# =============================================================================
# Triggers
# =============================================================================

def create_analysis(MW):

    if MW.dataset is None:
        Error('No Dataset', 'There is no dataset loaded to create analysis from.')
        return

    # start prompting
    MW.prompt_analysis.appendPlainText(f'\n---- Creating Analysis instance ---- \n')

    use_filled = True if MW.use_filled_for_ana.isChecked() else False

    ana, _cont, terminal, _msg = tlk_scripts.create_analysis_instance(dataset = MW.dataset,
                                                            add_gapfilled_values = use_filled)

    if not _cont:
        # deactivate the dashboard for analyis
        activate_analysis_widgets(MW, False)
        Error(_msg[0], _msg[1])
        return
    for line in terminal:
        MW.prompt_fill.appendPlainText(line)

    # update attribute
    MW.analysis = ana

    # Activate the dashboard for analyis
    activate_analysis_widgets(MW, True)
    # update spinners
    set_values_for_spinners(MW)

    MW.prompt_analysis.appendPlainText(f'\n---- Creating Analysis instance ---> Done! ---- \n')


def filter_analysis(MW):
    if not analysis_available(MW):
        return

    filterstring = str(MW.filter_query.text())

    if filterstring=='':
        Error('Filter querry', 'There is no filter expression given.')
        return

    # start prompting
    MW.prompt_analysis.appendPlainText(f'\n---- Filtering Analysis with: {filterstring} ---- \n')

    init_n_records = MW.analysis.df.shape[0]

    ana, _cont, terminal, _msg = tlk_scripts.apply_filter_on_analysis(analysis=MW.analysis,
                                                                      filterstring=filterstring)

    if not _cont:
        # deactivate the dashboard for analyis
        activate_analysis_widgets(MW, False)
        Error(_msg[0], _msg[1])
        return
    for line in terminal:
        MW.prompt_fill.appendPlainText(line)

    out_n_records = ana.df.shape[0]

    # update attribute
    MW.analysis = ana

    MW.prompt_analysis.appendPlainText(f'\n---- Filtering Analysis with: {filterstring} ---> Done! ---- \n')

    #notificate
    Notification(f'The filter reduced the total number of records from {init_n_records} to {out_n_records}.')




def diurnal_plot_trigger(MW):
    if not analysis_available(MW):
        return
    obstype = str(MW.obstype_diurnal.currentText())
    groupby = str(MW.groupby_diurnal.currentText())

    if MW.startdt_check_diurnal.isChecked():
        # get startdt
        startdtstr = str(MW.startdt_diurnal.textFromDateTime(MW.startdt_diurnal.dateTime()))
        startdt = datetime.strptime(startdtstr, '%d/%m/%Y %H:%M')

        # get_enddt
        enddtstr = str(MW.enddt_diurnal.textFromDateTime(MW.enddt_diurnal.dateTime()))
        enddt = datetime.strptime(enddtstr, '%d/%m/%Y %H:%M')

    else:
        startdt=None
        enddt=None

    # with or without reference:
    if MW.refstation_check_diurnal.isChecked():
        refstation = str(MW.refstation.currentText())
        refstation_tol = str(int(MW.ref_tollerance.value())) + 'T'


        # start prompting
        MW.prompt_analysis.appendPlainText(f'\n---- Make diurnal cycle ---- \n')

        stats, all_stats, ax, _cont, terminal, _msg = tlk_scripts.apply_diurnal_cycle_with_ref(
                                                        analysis=MW.analysis,
                                                        colorby=groupby,
                                                        obstype=obstype,
                                                        startdt=startdt,
                                                        enddt=enddt,
                                                        tollerance=refstation_tol,
                                                        refstation=refstation,
                                                        )
        if not _cont:
            # deactivate the dashboard for analyis
            activate_analysis_widgets(MW, False)
            Error(_msg[0], _msg[1])
            return
        for line in terminal:
            MW.prompt_fill.appendPlainText(line)

        # start prompting
        MW.prompt_analysis.appendPlainText(f'\n---- Make diurnal cycle ---> Done! ---- \n')

    else:

        # start prompting
        MW.prompt_analysis.appendPlainText(f'\n---- Make diurnal cycle ---- \n')

        stats, all_stats, ax, _cont, terminal, _msg = tlk_scripts.apply_diurnal_cycle_without_ref(
                                                        analysis=MW.analysis,
                                                        colorby=groupby,
                                                        obstype=obstype,
                                                        startdt=startdt,
                                                        enddt=enddt,
                                                        )
        if not _cont:
            Error(_msg[0], _msg[1])
            return
        for line in terminal:
            MW.prompt_fill.appendPlainText(line)

        # start prompting
        MW.prompt_analysis.appendPlainText(f'\n---- Make diurnal cycle ---> Done! ---- \n')


    # update attirubutes (needed to store in attributes otherwise windows do not last)
    MW.cycle_ax = ax
    MW.cycle_stats = stats

    # Open up windows
    make_a_cycle_plot(MW) #show plot
    show_cycle_stats_df(MW) #show dataframe


def anual_plot_trigger(MW):
    if not analysis_available(MW):
        return
    obstype = str(MW.obstype_anual.currentText())
    groupby = [str(MW.groupby_anual.currentText())] #as list
    agg_method = str(MW.agg_method_anual.currentText())

    if MW.startdt_check_anual.isChecked():
        # get startdt
        startdtstr = str(MW.startdt_anual.textFromDateTime(MW.startdt_anual.dateTime()))
        startdt = datetime.strptime(startdtstr, '%d/%m/%Y %H:%M')

        # get_enddt
        enddtstr = str(MW.enddt_anual.textFromDateTime(MW.enddt_anual.dateTime()))
        enddt = datetime.strptime(enddtstr, '%d/%m/%Y %H:%M')

    else:
        startdt=None
        enddt=None


    # start prompting
    MW.prompt_analysis.appendPlainText(f'\n---- Make anual cycle ---- \n')

    stats, all_stats, ax, _cont, terminal, _msg = tlk_scripts.apply_anual_cycle(
                                                    analysis=MW.analysis,
                                                    groupby=groupby,
                                                    obstype=obstype,
                                                    agg_method=agg_method,
                                                    startdt=startdt,
                                                    enddt=enddt,
                                                    )
    if not _cont:
        Error(_msg[0], _msg[1])
        return
    for line in terminal:
        MW.prompt_fill.appendPlainText(line)

    # start prompting
    MW.prompt_analysis.appendPlainText(f'\n---- Make anual cycle ---> Done! ---- \n')


    # update attirubutes (needed to store in attributes otherwise windows do not last)
    MW.cycle_ax = ax
    MW.cycle_stats = stats

    # Open up windows
    make_a_cycle_plot(MW) #show plot
    show_cycle_stats_df(MW) #show dataframe


def custom_cycle_plot_trigger(MW):
    if not analysis_available(MW):
        return
    obstype = str(MW.obstype_custom.currentText())
    agg_method = str(MW.agg_method_custom.currentText())

    groupdef_str = str(MW.groupdef_custom.text())
    groupdef_list = groupdef_str.replace(' ','').split(',')

    h_ax = str(MW.haxis_custom.currentText())


    if MW.startdt_check_custom.isChecked():
        # get startdt
        startdtstr = str(MW.startdt_custom.textFromDateTime(MW.startdt_custom.dateTime()))
        startdt = datetime.strptime(startdtstr, '%d/%m/%Y %H:%M')

        # get_enddt
        enddtstr = str(MW.enddt_custom.textFromDateTime(MW.enddt_custom.dateTime()))
        enddt = datetime.strptime(enddtstr, '%d/%m/%Y %H:%M')

    else:
        startdt=None
        enddt=None


    # start prompting
    MW.prompt_analysis.appendPlainText(f'\n---- Make custom cycle ---- \n')

    stats, all_stats, ax, _cont, terminal, _msg = tlk_scripts.apply_custom_cycle(
                                                    analysis=MW.analysis,
                                                    obstype=obstype,
                                                    aggregation=groupdef_list,
                                                    aggregation_method = agg_method,
                                                    horizontal_axis=h_ax,
                                                    startdt=startdt,
                                                    enddt=enddt
                                                    )
    if not _cont:
        # deactivate the dashboard for analyis
        Error(_msg[0], _msg[1])
        return
    for line in terminal:
        MW.prompt_fill.appendPlainText(line)

    # start prompting
    MW.prompt_analysis.appendPlainText(f'\n---- Make custom cycle ---> Done! ---- \n')


    # update attirubutes (needed to store in attributes otherwise windows do not last)
    MW.cycle_ax = ax
    MW.cycle_stats = stats

    # Open up windows
    make_a_cycle_plot(MW) #show plot
    show_cycle_stats_df(MW) #show dataframe


def get_lc_correlations(MW):
    # check if analysis is available
    if not analysis_available(MW):
        return

    # check if landcover information is available
    # find landcover columnnames in the metadf
    lc_columns = [col for col in MW.analysis.metadf.columns if (('_' in col) & (col.endswith('m')))]
    if not bool(lc_columns):
        Error('No landcover information', 'There are no landcoverfractions in the metadata. Use the Get landcover method first.')
        return

    # get parameters
    obstype = [str(MW.cor_obstype.currentText())]
    groupdef_str = str(MW.cor_group_def.text())
    groupdef_list = groupdef_str.replace(' ','').split(',')

    MW.prompt_analysis.appendPlainText(f'\n---- Get landcover correlation. ---- \n')
    cor_dict, _cont, terminal, _msg = tlk_scripts.get_lc_cor_info(
                                        analysis=MW.analysis,
                                        obstype=obstype,
                                        groupby_labels=groupdef_list)

    if not _cont:
        # deactivate the dashboard for analyis
        activate_cor_plots(MW, setvalue=False)
        Error(_msg[0], _msg[1])
        return
    for line in terminal:
        MW.prompt_fill.appendPlainText(line)

    # update dashboard
    activate_cor_plots(MW, setvalue=True)
    MW.heat_cor_group.clear()
    MW.heat_cor_group.addItems([str(group) for group in cor_dict.keys()])

    MW.prompt_analysis.appendPlainText(f'\n---- Get landcover correlation. ---> Done! ---- \n')

    Notification(f'Landcover correlations are cumputed for these groups: {list(cor_dict.keys())}')



def make_heatmap_plot(MW):

    if not bool(MW.analysis.lc_cor_dict):
        Error('No correlations to plot', 'There are no stored landcover correlations to show.')
        return

    # need string mapper because keys are not always strings while cor_group (gui spinner) is
    cor_group = str(MW.heat_cor_group.currentText())
    string_mapper = {str(key): key for key in MW.analysis.lc_cor_dict.keys()}
    key=string_mapper[cor_group]


    MW.prompt_analysis.appendPlainText(f'\n---- Creating heatmap plot. ---- \n')
    ax, _cont, terminal, _msg = tlk_scripts.create_cor_figure(analysis=MW.analysis,
                                       groupby_value=key)

    if not _cont:
        # deactivate the dashboard for analyis
        activate_cor_plots(MW, setvalue=False)
        Error(_msg[0], _msg[1])
        return
    for line in terminal:
        MW.prompt_fill.appendPlainText(line)


    MW.prompt_analysis.appendPlainText(f'\n---- Creating heatmap plot. ---> Done! ---- \n')
    # Open up windows
    MW.heatmap_ax = ax
    make_a_heatmap_plot(MW) #show plot

def display_cor_mat(MW):
    if not bool(MW.analysis.lc_cor_dict):
        Error('No correlations to plot', 'There are no stored landcover correlations to show.')
        return

    # need string mapper because keys are not always strings while cor_group (gui spinner) is
    cor_group = str(MW.heat_cor_group.currentText())
    string_mapper = {str(key): key for key in MW.analysis.lc_cor_dict.keys()}
    key=string_mapper[cor_group]

    df = MW.analysis.lc_cor_dict[key]
    df = MW.analysis.lc_cor_dict[key]['combined matrix']

    show_cor_matix_df(MW, df)





def create_scatter_cor_plot(MW):
    if not bool(MW.analysis.lc_cor_dict):
        Error('No correlations to plot', 'There are no stored landcover correlations to show.')
        return


    MW.prompt_analysis.appendPlainText(f'\n---- Creating correlation scatter plot. ---- \n')
    ax, _cont, terminal, _msg = tlk_scripts.make_scatter_cor_plot(analysis=MW.analysis)

    if not _cont:
        # deactivate the dashboard for analyis
        activate_cor_plots(MW, setvalue=False)
        Error(_msg[0], _msg[1])
        return
    for line in terminal:
        MW.prompt_fill.appendPlainText(line)


    MW.prompt_analysis.appendPlainText(f'\n---- Creating correlation scatter plot. ---> Done! ---- \n')
    # Open up windows
    MW.heatmap_ax = ax
    make_a_heatmap_plot(MW) #show plot





# =============================================================================
# Helpers
# =============================================================================

def analysis_available(MW):
    if MW.analysis is None:
        Error('No Analysis', 'There is no Analysis loaded.')
        return False
    if MW.analysis.df.empty:
        Error('Empty Analysis', 'There are no records in the analysis')
        return False
    return True

