from . instrument import Instrument, Instruments_directory
from . import utils

import importlib, inspect, os, sys, json

from dataclasses import dataclass, field

import numpy as np
import xarray as xr
import pandas as pd


@dataclass
class Measurement_Settings:
    acquisition_instruments: dict = field(default_factory=dict)
    scan_instruments: dict = field(default_factory=dict)
    scan_collection: dict = field(default_factory=dict)
    averages: int =1
@dataclass
class Measurement_Data:
    data_template: xr.DataArray = field(default_factory=xr.DataArray)
    data_set: xr.Dataset = field(default_factory=xr.Dataset)



def make_measurement_settings(meas_configs:dict)->Measurement_Settings:
    """Make a Measurement_Settings object from configurations in meas_configs 
        dictionary, which has keys 'acquisition_instruments',
        'scan_instruments', and 'scan_collection' (i.e., the attributes of a
        Measurement settings object).

    Args:
        meas_configs (dict): Dictionary with configurations for 
        'aquisistion_instruments', 'scan_instruments', and 'scan_collection'.

    Returns:
        Measurement_Settings: Measurement_Settings object.
    """    
    ms = Measurement_Settings()
    for instrument_config in list(meas_configs['acquisition_instruments'].values()):
        add_instrument(instrument_config, ms.acquisition_instruments)
    for instrument_config in list(meas_configs['scan_instruments'].values()):
        add_instrument(instrument_config, ms.scan_instruments)
    for scan_settings in list(meas_configs['scan_collection'].values()):
        add_scan(scan_settings, 
                 ms.scan_instruments[scan_settings['name']],
                 ms)
    ms.averages = meas_configs['averages']
    return ms

def generate_measurement_config(ms:Measurement_Settings):
    """Make configuration dictionary from Measurement_Settings object.
        Configuration file will be a dict like file (e.g., json, yaml, toml) with structure
        {'acquisition_instruments': {'instrument_name': configuration, ...},
        'scan_instruments': {'instrument_name': configuration, ...}, 
        'scan_collections': {'scan_name': settings, ...}
        }
    Args:
        ms (Measurement_Settings): Measurement settings to generate config for.
    """
    acq_inst, scan_inst, scans = {}, {}, {}
    for key in list(ms.acquisition_instruments.keys()):
        acq_inst.update({key: ms.acquisition_instruments[key].configuration})
    for key in list(ms.scan_instruments.keys()):
        scan_inst.update({key: ms.scan_instruments[key].configuration})
    for key in list(ms.scan_collection.keys()):
        scans.update({key: ms.scan_collection[key]['settings']})
        
    meas_config = {'acquisition_instruments': acq_inst,
                     'scan_instruments': scan_inst,
                     'scan_collection': scans,
                     'averages':ms.averages}
    return meas_config

def save_measurement_config(ms:Measurement_Settings, out_file:str)->None:
    """Generatres configuration dictioary from Measurement_Settings object
        and saves to specified file.

    Args:
        ms (Measurement_Settings): Measurement settings to save.
        out_file (str): Name of file to save.
    """    
    meas_settings = generate_measurement_config(ms)
    utils.dump_config(meas_settings, out_file)
    return 
    
    
def add_instrument(instrument_config: dict, instruments: dict):
    """Adds an instrument object constructed from the configuration in 
        config_file to the instrument dictionary instruments. This dictionary 
        will be 'acquisition_instruments' or 'scan_instruments' the 
        Measurement_Settings object.

    Args:
        config_file (str): file name of instrument configurations
        instruments (dict): dictionary of measurement instruments (acquisition 
        or scan)
    """
    instrument = make_instrument(instrument_config)
    instruments.update({instrument.name: instrument})
    return
    
def make_instrument(config:dict)->dict:
    """Import the instrument module give by config['instrument'] and makes
        an instrument of that module type (e.g., SG380). 
        Returns a dictionary of configurations, now with the instrument object
        as the value of the 'instrument' entry.

    Args:
        config (dict): Instrument configuration

    Returns:
        dict: New instrument configuration with Instrument object.
    """  
    to_import = config["instrument"] 
    inst_path = os.path.abspath(f'{Instruments_directory}\\{to_import}\\{to_import}.py')
    spec = importlib.util.spec_from_file_location(to_import, inst_path)
    instrument_module = importlib.util.module_from_spec(spec)
    sys.modules[to_import] = instrument_module
    spec.loader.exec_module(instrument_module)
    available_modules = dict(inspect.getmembers(instrument_module, inspect.isclass))
    instrument = available_modules[to_import](config)
    print(f'dev: {instrument}')
    # full_instrument = config
    # full_instrument.update({'instrument': instrument})
    return instrument


def add_scan(scan_settings:dict,
             scan_instrument: Instrument, 
             ms:Measurement_Settings)->Measurement_Settings:
    """Makes scan collection based in input scan_collection dictionary 
        and adds the collection to Measurement_Settings

    Args:
        scan_collection (dict): Scan collection dictionary.
        ms (Measurement_Settings): Measurement_Settings 
        updated with scan collection.

    Returns:
        Measurement_Settings: _description_
    """
    scan = make_scan(scan_settings, scan_instrument)
    try:
        ms.scan_collection.update(scan)
    except TypeError:
        pass
    return


def make_scan(scan_settings:dict, instrument:Instrument)->dict:
    """Makes a scan dictionary from the input scan scan settings. Returns 
        scan to add to scan collection.

    Args:
        scan_settings (dict): Settings for a single scan.

    Returns:
        dict: scan dictionary to add to scan collection.
    """    
    #scan_settings = clean_scan_settings(scan_settings)
    if not scan_settings['instrument'] == instrument.__class__.__name__:
        print('Settings do not match selected instrument')
        return
    scan_key = f"{instrument.name}-{scan_settings['parameter']}"
    scan_settings.update({'name': instrument.name})
    scan = {'instrument': instrument,
            'parameter': scan_settings['parameter'],
                'schedule': make_scan_schedule(scan_settings),
                'repetitions': scan_settings['repetitions'],
                'randomize': scan_settings['randomize']}
    return {scan_key: {'settings': scan_settings, 'scan': scan}}


def make_scan_schedule(scan_settings:dict)-> np.ndarray:
    """Makes the order of parameter values to scan through (called schedule) 
        based on the scan settings 'min', 'max', 'points', and 'repititions'. 
        Returns a numpy.ndarray with the schedule.
        
        The schedules has four default scales: 'linear', 'log', 'custom', and 
        'constant'. 'linear' and 'log' generate schedules in linear or 
        log space, 'custom' uses a schedule from the user defined 
        custom_schedule method, and 'constant' generates a single value 
        based on the 'min' parameter. 'repetitions' determines how many times 
        the schedule is repeated. 'random' is utilized while the 
        measurement is running.
        
        Example:
        scan_settings = {'name': 'SG1', 'instrument': 'SG380', 
                         'parameter': frequency,
                         'min': 1, 'max': 2, 'points': 5, 'repetitions': 2, 
                         'randomize: False, 'note': ''}
        
        Return schedule: np.ndarray([1.0, 1.25, 1.5, 1.75, 2.0, 1.0, 1.25, 
                                     1.5, 1.75, 2.0])

    Args:
        scan_settings (dict): Scan settings

    Returns:
        np.ndarray: np.ndarray with scan schedule
    """    
    def linear():
        array = np.linspace(scan_settings['min'],scan_settings['max'], scan_settings['points'])
        return np.tile(array, scan_settings['repetitions'])
    def log():
        array = np.logspace(scan_settings['min'], scan_settings['max'], scan_settings['points'])
        return np.tile(array, scan_settings['repetitions'])
    def custom():
        array = np.array(custom_schedule(scan_settings['note']))
        return np.tile(array, scan_settings['repitions'])
    def constant():
        return np.tile(scan_settings['min'], scan_settings['repetitions'])
    schedule = {'linear': linear, 'log': log, 'custom': custom, 'constant': constant}
    return schedule[scan_settings['scale']]()

    
def custom_schedule(note:str)->np.ndarray:
    file_name = json.loads(note)['custom']
    l_type = os.path.splitext(file_name)[-1]
    with open(file_name, 'r') as f:
        if 'npy' in l_type:
            array = np.load(f, 'r')
        else:
            array = np.loadtxt(f)
    return array
    
## how to implement method to add/change scan settings??
# def define_scan_settings():
#     scan_settings = {'instrument': '', 'parameter': '',
#         'minimum': 0, 'maximum': 0, 'points': 1,
#         'repetitions': 1, 'scale': 'linear', 'randomize': False, 
#         'note': ''}
#     return scan_settings
    
    
def create_data_template(Measurement_Setings:Measurement_Settings)->xr.DataArray:
    """Creates an xarray.DataArray object based on the measurement settings. 
        The dimenions will be based on the parameters to scan in 
        Measurement_Settings.scan_collection and the samples to read in
        Measurement_Settings.acquisition_instruments.
        This template is used to create entries for storing the data in
        a Measurement_Data.data_set object.

    Args:
        Measurement_Setings (Measurement_Settings): Current settings of the measurement

    Returns:
        xr.DataArray: xarray.DataArray object with dimenions of parameters to scan
                    and acquisition samples to read. Values are initialized to np.nan
    """
    template = {}
    scans = Measurement_Setings.scan_collection
    acquisitions = Measurement_Setings.acquisition_instruments
    
    for acq_key in list(acquisitions.keys()):
        coords = {}
        sample_array = np.arange(acquisitions[acq_key].acq_data_size)
        for scan_key in list(scans.keys()):
            coords.update({scans[scan_key]['scan']['parameter']: 
                        scans[scan_key]['scan']['schedule']})
        coords.update({f'{acq_key}': sample_array})
        dimensions = []
        for arr in list(coords.values()):
            dimensions.append(arr.size)
        
        template[acq_key] = xr.DataArray(np.full(dimensions, np.nan),
                                        dims = list(coords.keys()),
                                        coords = coords)
    return template
