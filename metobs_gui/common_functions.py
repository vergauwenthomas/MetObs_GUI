# import metobs_gui.template_func as template_func
from pathlib import Path
import json
import pandas as pd


from PyQt5.QtWidgets import QFileDialog

from metobs_gui.tlk_scripts import gui_wrap 
from metobs_gui.errors import Error
import metobs_gui.path_handler as path_handler
from metobs_toolkit.io_collection.filereaders import CsvFileReader

# ------------------------------------------
#    Formatting
# ------------------------------------------

def get_current_datetime_from_widget(datetimeedit, fmt="%d/%m/%Y %H:%M"):
        
    # get string format 
    dtstr = str(datetimeedit.textFromDateTime(datetimeedit.dateTime()))
    return pd.to_datetime(dtstr, format=fmt)
    


# ------------------------------------------
#    Displaying
# ------------------------------------------

def display_jsonfile_in_plaintext(plaintext, jsonfile, indent=2, cleanup=True):
    """Display the template json file on the page. """
    #read template json

    if not Path(jsonfile).exists:
        raise FileNotFoundError(f'{jsonfile} is not found.')
    
    dict = path_handler.read_json(jsonfile)
    
    #write to the text displayer
    if cleanup:
        plaintext.clear()
        plaintext.setPlainText(json.dumps(dict, indent=indent))
    else:
        plaintext.appendPlainText(json.dumps(dict, indent=indent))

    plaintext.moveCursor(plaintext.textCursor().End)

def display_info_in_plaintext(plaintext, metobs_obj, cleanup=False):

    text = '==============================\n' 
    outputtext, succes, stout = gui_wrap(
        func=metobs_obj.get_info,
        func_kwargs={'printout': False})
    
    text += outputtext
    text += '==============================\n\n'
   
    if not succes:
        Error(f'.get_info() error on {metobs_obj}. |n{stout}')
    if cleanup:
        plaintext.clear()
        plaintext.setPlainText(text)
    else:
        plaintext.appendPlainText(text)
    
    plaintext.moveCursor(plaintext.textCursor().End)



# ------------------------------------------
#    Reading data
# ------------------------------------------

def read_csv_file(filepath, nrows=None):            
    datareader = CsvFileReader(file_path=filepath, is_url=False)
    data = datareader.read(nrows=nrows)
    return data


# ------------------------------------------
#    Others
# ------------------------------------------

def browse_for_file(MW, displ_text='Select file', base=str(Path.home())) -> str:
    fname=QFileDialog.getOpenFileName(MW, displ_text, base)
    return fname[0]
   