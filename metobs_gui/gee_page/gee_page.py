
import os
from pathlib import Path
import metobs_toolkit


from metobs_gui.tlk_scripts import gui_wrap, get_function_defaults
import metobs_gui.path_handler as path_handler
from metobs_gui.extra_windows import HtmlDialog
from metobs_gui.errors import Error, Notification
import metobs_gui.common_functions as common_func
from metobs_gui.dataframelab import DataDialog
from metobs_gui.extra_windows import  DatasetTimeSeriesDialog

promptvar = "prompt_geedata" #name of the plaintext prompt on this page
geemanagers = metobs_toolkit.default_GEE_datasets

# =============================================================================
# init page
# =============================================================================
def init_page(MW):

    setup_spinners(MW)


# =============================================================================
# Setup
# =============================================================================
def setup_spinners(MW):
    geedataset_names = list(geemanagers.keys())
    #info and plot spinners
    MW.geedataset_info_spinner.clear()
    MW.geedataset_plot_spinner.clear()
    MW.geedataset_info_spinner.addItems(geedataset_names)
    MW.geedataset_plot_spinner.addItems(geedataset_names)


    #dynamic datasets
    dynamic_geedatasets = [key for key, value in geemanagers.items() if isinstance(value, metobs_toolkit.GEEDynamicDatasetManager)]
    MW.dynamic_dataset_spinner.clear()
    MW.dynamic_dataset_spinner.addItems(dynamic_geedatasets)

    #Setup modelobstype
    _update_modelobstypes(MW) #fake trigger



    
# =============================================================================
# Triggers
# =============================================================================

def setup_triggers(MW):
    
    #Spinner changes

    MW.dynamic_dataset_spinner.currentIndexChanged.connect(lambda: _update_modelobstypes(MW))

    #Get buttons
    MW.get_lcz.clicked.connect(lambda: _react_get_lcz(MW))    
    MW.get_altitude.clicked.connect(lambda: _react_get_altitude(MW))
    MW.get_landcover.clicked.connect(lambda: _react_get_landcover(MW))

    MW.extract_gee_button.clicked.connect(lambda: _react_get_gee_timeseries(MW))
    
    MW.get_info_geepage.clicked.connect(lambda: _react_get_info(MW))
    MW.show_datalab_geepage.clicked.connect(lambda: _react_show_datalab(MW))
    MW.plot_dataset_geepage.clicked.connect(lambda: _react_plot_dataset(MW))
    MW.spatial_plot_geepage.clicked.connect(lambda: _react_spatial_plot(MW))
    MW.show_gee_info.clicked.connect(lambda: _react_get_geedataset_info(MW))

    MW.browse_gee_button.clicked.connect(lambda: _browse_gee_csv_file(MW))
    MW.import_gee_from_csv_button.clicked.connect(lambda: _react_gee_from_csv(MW))
    #radiobox statchanges
    MW.gee_similar_timespan.stateChanged.connect(lambda: _react_similar_timespan(MW))

   

# =============================================================================
# reactions
# =============================================================================

def _browse_gee_csv_file(MW):
    fpath=common_func.browse_for_file(MW, 'Select GEE CSV file')
    MW.gee_csv_path.setText(fpath) #update text

def _react_gee_from_csv(MW):
    prompt = getattr(MW, promptvar )
    #Check if file exists
    trgfile = Path(MW.gee_csv_path.text())
    if not trgfile.exists:
        Error(f'The file {trgfile} does not exist!')
    
    #get model to interpret the csv for 
    geemanager=geemanagers[MW.dynamic_dataset_spinner.currentText()]

    #Get default values of the method
    func_kwargs = get_function_defaults(MW.Dataset.import_gee_data_from_file)

    #Update the defaults
    func_kwargs['filepath'] = str(trgfile)
    func_kwargs['geedynamicdatasetmanager'] = geemanager
    
    # start prompting
    prompt.appendPlainText('\n---- Importing GEE data from CSV  ---- \n')

    _return, succes, stout = gui_wrap(
                        func=MW.Dataset.import_gee_data_from_file,
                        func_kwargs=func_kwargs,
                        log_level=MW.loglevel.currentText(),
                        plaintext=prompt)
    # write output to prompt
    prompt.appendPlainText(str(stout))

    if not succes:
        Error('Error when importing GEE data from CSV.', stout)
        return

    return




def _react_similar_timespan(MW):
    if MW.gee_similar_timespan.isChecked():
        MW.gee_startdt.setEnabled(False)
        MW.gee_enddt.setEnabled(False)
    else:
        MW.gee_startdt.setEnabled(True)
        MW.gee_enddt.setEnabled(True)



def _react_get_gee_timeseries(MW):
    prompt = getattr(MW, promptvar )
    
    #Scrape the info
    geemanager=geemanagers[MW.dynamic_dataset_spinner.currentText()]
    selected_modelobs = [select.text() for select in MW.listed_modelobs.selectedItems()]
    if MW.gee_similar_timespan.isChecked():
        startdt=None
        enddt=None
    else:
        startdt = common_func.get_current_datetime_from_widget(
            datetimeedit=MW.gee_startdt
            )
        enddt = common_func.get_current_datetime_from_widget(
            datetimeedit=MW.gee_enddt
            )
    get_all_bands=MW.get_all_bands_box.isChecked()

    #Get default values of the method
    func_kwargs = get_function_defaults(MW.Dataset.get_gee_timeseries_data)

    #Update the defaults
    func_kwargs['geedynamicdatasetmanager'] = geemanager
    func_kwargs['startdt_utc'] = startdt
    func_kwargs['enddt_utc'] = enddt
    func_kwargs['target_obstypes'] = selected_modelobs
    func_kwargs['get_all_bands'] = get_all_bands

    # start prompting
    prompt.appendPlainText('\n---- Extracting timeseries from GEE ---- \n')

    _retdf, succes, stout = gui_wrap(
                        func=MW.Dataset.get_gee_timeseries_data,
                        func_kwargs=func_kwargs,
                        log_level=MW.loglevel.currentText(),
                        plaintext=prompt)
    if not succes:
        Error('Error when extracting GEE timeseries data.', stout)
        return
    # write output to prompt
    prompt.appendPlainText(str(stout))
    return




def _update_modelobstypes(MW):
    #extract the present modelobs from the selected GEEmanager
    geemanager = geemanagers[MW.dynamic_dataset_spinner.currentText()]
    present_modelobstypes = list(geemanager.modelobstypes.keys())
    
    #update the lst
    MW.listed_modelobs.clear()
    MW.listed_modelobs.addItems(present_modelobstypes)


def _react_get_lcz(MW):
    prompt = getattr(MW, promptvar)

    # start prompting
    prompt.appendPlainText('\n---- Get LCZ from GEE ---- \n')
    import logging
    _lcz, succes, stout = gui_wrap(
                        func=MW.Dataset.get_LCZ,
                        func_kwargs={'overwrite': True},
                        plaintext=prompt,
                        log_level=MW.loglevel.currentText())
    if not succes:
        Error('Error when extracting LCZ.', stout)
        return
    # write output to prompt
    # prompt.appendPlainText(str(stout))

    prompt.appendPlainText('\n---- Get LCZ from GEE ---> Done! ---- \n')
    Notification('LCZ is added to the metadf.')
    return
 

def _react_get_altitude(MW):
    prompt = getattr(MW, promptvar )
    # start prompting
    prompt.appendPlainText('\n---- Get Altitude from GEE ---- \n')

    _alt, succes, stout = gui_wrap(
                    func=MW.Dataset.get_altitude,
                    func_kwargs={'overwrite': True},
                    plaintext=prompt,
                    log_level=MW.loglevel.currentText())
    if not succes:
        Error('Error when extracting altitude.', stout)
        return

    prompt.appendPlainText('\n---- Get Alitutde from GEE ---> Done! ---- \n')
    Notification('Altitude is added to the metadf.')
    return
 

def _react_get_landcover(MW):
    prompt = getattr(MW, promptvar )
    # start prompting
    prompt.appendPlainText('\n---- Get landcover fractions from GEE ---- \n')
    
    bufferrad = int(MW.lc_radius.value())
    aggbool = MW.lc_agg.isChecked()
   
    
    _lcfrac, succes, stout = gui_wrap(
                        func=MW.Dataset.get_landcover_fractions,
                        func_kwargs={'buffers': [bufferrad],
                                    'aggregate': aggbool},
                        plaintext=prompt,
                        log_level=MW.loglevel.currentText())
    if not succes:
        Error('Error when extracting landcover fractions', stout)
        return

    prompt.appendPlainText('\n---- Get landcover fractions from GEE ---> Done! ---- \n')
    Notification(f'landcover fractions for {bufferrad}m are added to the metadf.')
    return




def _react_get_info(MW):
    prompt = getattr(MW, promptvar)

    common_func.display_info_in_plaintext(
        plaintext=prompt,
        metobs_obj=MW.Dataset,
    )

def _react_show_datalab(MW):
    MW._dlg = DataDialog(dataset=MW.Dataset) #launched when created

def _react_plot_dataset(MW):
    MW._dlg = DatasetTimeSeriesDialog(dataset=MW.Dataset)#launched when created

def _react_spatial_plot(MW):
    prompt = MW.prompt_geedata
    #scrape the info
    geemanager=geemanagers[MW.geedataset_plot_spinner.currentText()]
    
    #target an html file in tmp folder
    trgfilepath = Path(path_handler.TMP_dir).joinpath("geestatic_plot.html")

    #construct kwargs
    func_kwargs = get_function_defaults(MW.Dataset.make_gee_plot)
    func_kwargs['geedatasetmanager'] = geemanager
    func_kwargs['save'] = True,
    func_kwargs['outputfolder']=str(trgfilepath.parent)
    func_kwargs['filename']=str(trgfilepath.name)
    func_kwargs['overwrite'] = True

    #create the map
    _map, succes, stout = gui_wrap(
                func = MW.Dataset.make_gee_plot,
                func_kwargs=func_kwargs,
                plaintext=prompt,
                log_level=MW.loglevel.currentText())
    
    if not succes:
        Error('Error when creating a geestatic spatialplot.', stout)
        return
    
    
    MW._dlg = HtmlDialog(str(trgfilepath))

def _react_get_geedataset_info(MW):
    prompt = getattr(MW, promptvar)

    #get target dataset
    trg_datasetname = MW.geedataset_info_spinner.currentText()
    common_func.display_info_in_plaintext(
        plaintext=prompt,
        metobs_obj=geemanagers[trg_datasetname],
    )


    

