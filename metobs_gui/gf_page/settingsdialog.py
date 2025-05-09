from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QDialog, QCheckBox, QComboBox, QLineEdit, QSpinBox
import ast
from pathlib import Path

from metobs_gui.path_handler import GUI_dir
from metobs_gui.tlk_scripts import get_function_docstring

class SettingsDialog(QDialog):
    """ Parent abstract"""
    def __init__(self, uifilepath, trgobstype, func):
        super().__init__()
        loadUi(uifilepath, self)
        self.open()

        self.funcname = func.__name__
        self.docstr = func.__doc__

        self.obstype_spin.clear()
        self.obstype_spin.addItems([trgobstype])
        self.obstype_spin.setEnabled(False)

class InterpolationSettingsDialog(SettingsDialog):
    def __init__(self, trgobstype, func):
        
        super().__init__(uifilepath=Path(GUI_dir).joinpath('gf_page').joinpath('interpolation_settings_dialog.ui'),
                          trgobstype=trgobstype,
                          func=func)

        self.use_max_lead_dist.toggled.connect(self.max_leading_distance.setEnabled)
        self.use_max_trail_dist.toggled.connect(self.max_trailing_distance.setEnabled)

        self.doc.setHtml(format_rawtring_to_htmltext(self.docstr))
    def get_settings(self):
        #Read the settings and set as as dict

        if self.use_max_lead_dist.isChecked():
            max_lead_dist = f'{get_val(self.max_leading_distance)}min'
        else:
            max_lead_dist = None

        if self.use_max_trail_dist.isChecked():
            max_trail_dist = f'{get_val(self.max_trailing_distance)}min'
        else:
            max_trail_dist = None


        settings = {
            'target_obstype': get_val(self.obstype_spin),
            'overwrite_fill': get_val(self.overwrite_box),
            'method': get_val(self.method_spinner),
            'method_kwargs': get_val(self.methodkwargs_edit, True),
            'max_consec_fill':get_val(self.max_consec_spinner),
            'n_leading_anchors':get_val(self.n_lead_spinner),
            'n_trailing_anchors': get_val(self.n_trail_spinner),
            'max_lead_to_gap_distance':max_lead_dist,
            'max_trail_to_gap_distance':max_trail_dist}
        #Set function name
        settings['MetObs_method'] = self.funcname
        return settings
    
class RawModeldataGFSettingsDialog(SettingsDialog):
    def __init__(self, trgobstype,func):
        super().__init__(uifilepath=Path(GUI_dir).joinpath('gf_page').joinpath('raw_modeldata_settings_dialog.ui'),
                          trgobstype=trgobstype,
                          func=func)
        self.doc.setHtml(format_rawtring_to_htmltext(self.docstr))
    def get_settings(self):
        #Read the settings and set as as dict

        settings = {
            'target_obstype': get_val(self.obstype_spin),
            'overwrite_fill': get_val(self.overwrite_box)
            }
        #Set function name
        settings['MetObs_method'] = self.funcname
        return settings

class DebiasModeldataGFSettingsDialog(SettingsDialog):
    def __init__(self, trgobstype, func):
        super().__init__(uifilepath=Path(GUI_dir).joinpath('gf_page').joinpath('debias_modeldata_settings_dialog.ui'),
                          trgobstype=trgobstype,
                          func=func)
        self.doc.setHtml(format_rawtring_to_htmltext(self.docstr))
    def get_settings(self):
        #Read the settings and set as as dict

        settings = {
            'target_obstype': get_val(self.obstype_spin),
            'overwrite_fill': get_val(self.overwrite_box),
            'leading_period_duration': f'{get_val(self.lead_duration)}h',
            'min_leading_records_total': get_val(self.n_lead),
            'trailing_period_duration': f'{get_val(self.trail_duration)}h',
            'min_trailing_records_total': get_val(self.n_trail),
            }
        #Set function name
        settings['MetObs_method'] = self.funcname
        return settings
    
class DiurnalDebiasModeldataGFSettingsDialog(SettingsDialog):
    def __init__(self, trgobstype, func):
        super().__init__(uifilepath=Path(GUI_dir).joinpath('gf_page').joinpath('diurnal_debias_modeldata_settings_dialog.ui'),
                          trgobstype=trgobstype,
                          func=func)
        self.doc.setHtml(format_rawtring_to_htmltext(self.docstr))
    def get_settings(self):
        #Read the settings and set as as dict

        settings = {
            'target_obstype': get_val(self.obstype_spin),
            'overwrite_fill': get_val(self.overwrite_box),
            'leading_period_duration': f'{get_val(self.lead_duration)}h',
            'trailing_period_duration': f'{get_val(self.trail_duration)}h',
            'min_debias_sample_size': get_val(self.n_sample)
            }
        
        #Set function name
        settings['MetObs_method'] = self.funcname
        return settings

class WeightedDiurnalDebiasModeldataGFSettingsDialog(SettingsDialog):
    def __init__(self, trgobstype, func):
        super().__init__(uifilepath=Path(GUI_dir).joinpath('gf_page').joinpath('weighted_diurnal_debias_modeldata_settings_dialog.ui'),
                          trgobstype=trgobstype,
                          func=func)

        self.doc.setHtml(format_rawtring_to_htmltext(self.docstr))

    def get_settings(self):
        #Read the settings and set as as dict

        settings = {
            'target_obstype': get_val(self.obstype_spin),
            'overwrite_fill': get_val(self.overwrite_box),
            'leading_period_duration': f'{get_val(self.lead_duration)}h',
            'trailing_period_duration': f'{get_val(self.trail_duration)}h',
            'min_lead_debias_sample_size': get_val(self.n_lead_sample),
            'min_trail_debias_sample_size': get_val(self.n_trail_sample)
            }
        
        #Set function name
        settings['MetObs_method'] = self.funcname
        return settings










def format_rawtring_to_htmltext(rawstr):
    return rawstr.replace('\n', '<br>').replace(' ', '&nbsp;')



def get_val(widget, as_dict=False):
    if isinstance(widget, QCheckBox):
        return widget.isChecked()
    elif isinstance(widget, QComboBox):
        return widget.currentText()
    elif isinstance(widget, QSpinBox):
        return widget.value()
    elif isinstance(widget, QLineEdit):
        string = widget.text()
        if as_dict:
            return ast.literal_eval(string)
        else:
            return string
    else:
        raise TypeError(f'The {type(widget)} is not implemented.')
