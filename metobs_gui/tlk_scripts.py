#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 31 09:40:08 2023

@author: thoverga
"""

#%% Load vlinder toolkit (not shure what is best)
import sys
from io import StringIO
import pprint
import warnings

from PyQt5.QtWidgets import QSpinBox, QDoubleSpinBox
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt



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
import inspect
import logging




#%% Helpers

class CapturingPrint(list):
    """ Capture piped stout as a list of strings. """
    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self
    
    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        del self._stringio    # free up some memory
        sys.stdout = self._stdout
        
    def __str__(self):
        returnstr = ''
        for stoutline in self:
            returnstr+=f'{stoutline}\n'
        return returnstr
    
    def __repr__(self):
        return str(self)

# Custom warning handler
class WarningCapture:
    def __init__(self):
        self.captured_warnings = []

    def __enter__(self):
        self._original_showwarning = warnings.showwarning
        warnings.showwarning = self._capture_warning
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        warnings.showwarning = self._original_showwarning

    def _capture_warning(self, message, category, filename, lineno, file=None, line=None):
        warning_msg = warnings.formatwarning(message, category, filename, lineno, line)
        self.captured_warnings.append(warning_msg)

    def __str__(self):
        return "\n".join(self.captured_warnings)
    


def gui_wrap(func, func_kwargs, plaintext=None, log_level=logging.INFO):
    """ A wrapper for the GUI to call a function safely with logging. """
    # Attach to the root logger to catch all logs
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    log_handler = StringIO()
    stream_handler = logging.StreamHandler(log_handler)
    stream_handler.setLevel(log_level)
    formatter = logging.Formatter('%(levelname)s - %(asctime)s - %(message)s')
    stream_handler.setFormatter(formatter)
    root_logger.addHandler(stream_handler)

    print(f'Executing Metobs command: \n* {func}')
    print(pprint.pformat(func_kwargs))

    if plaintext is not None:
        plaintext.appendPlainText(f'Executing Metobs command: \n* {func} with:')
        plaintext.appendPlainText(pprint.pformat(func_kwargs))
    
    try:
        
        QApplication.setOverrideCursor(Qt.WaitCursor) #set cursor to busy
        with CapturingPrint() as printed_output, WarningCapture() as captured_warnings:
            ret = func(**func_kwargs)
        
        # Log success
        print(f'Successful execution! \nstdout: \n{printed_output}')
        if captured_warnings.captured_warnings:
            print(f'Warnings: \n{captured_warnings}')
        
        if plaintext is not None:
            plaintext.appendPlainText(f'Successful execution! \nstdout: \n{printed_output}')
            if captured_warnings.captured_warnings:
                plaintext.appendPlainText(f'Warnings: \n{captured_warnings}')
        
        # Add logs to plaintext
        if plaintext is not None:
            stream_handler.flush()
            log_handler.seek(0)
            plaintext.appendPlainText(f'Logs:\n{log_handler.getvalue()}')
        
        #scroll to the end of plaintext
        if plaintext is not None:
            plaintext.moveCursor(plaintext.textCursor().End)
        
        QApplication.restoreOverrideCursor()
        return ret, True, printed_output
    
    except Exception as e:
        # Log unexpected exceptions
        msg = str(e)
        print(f'EXCEPTION occurred: {msg}')
        if plaintext is not None:
            plaintext.appendPlainText(f'EXCEPTION occurred:\n {msg}')
            stream_handler.flush()
            log_handler.seek(0)
            plaintext.appendPlainText(f'Logs:\n{log_handler.getvalue()}')
            plaintext.moveCursor(plaintext.textCursor().End)
        QApplication.restoreOverrideCursor()
        return None, False, msg
    
    except SystemExit:
        # Log system exit exceptions
        _type, msg, _traceback = sys.exc_info()
        print(f'SystemExit occurred: {msg}')
        if plaintext is not None:
            plaintext.appendPlainText(f'SystemExit occurred:\n {msg}')
            stream_handler.flush()
            log_handler.seek(0)
            plaintext.appendPlainText(f'Logs:\n{log_handler.getvalue()}')
            plaintext.moveCursor(plaintext.textCursor().End)
            QApplication.restoreOverrideCursor()
        return None, False, msg
    finally:
        QApplication.restoreOverrideCursor()
        root_logger.removeHandler(stream_handler)
    

def get_function_defaults(func):
    """
    Returns a dictionary of parameter names and their default values for the given function.
    
    Parameters:
        func (function): The function to inspect.
    
    Returns:
        dict: A dictionary with parameter names as keys and their default values as values.
    """
    signature = inspect.signature(func)
    return {
        param.name: param.default
        for param in signature.parameters.values()
        if param.default is not inspect.Parameter.empty
    }


def get_function_docstring(func):
    return str(func.__doc__)