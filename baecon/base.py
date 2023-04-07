from .device import Device, Devices_directory

import importlib
import inspect
import os
import sys
import json
from dataclasses import dataclass, field
import numpy as np


@dataclass
class Measurement_Settings:
    """Data structure for holding measurement settings which are acquisition
    devices, scan devices, scan collection, and averages (repeats)
    of the scan to perform.

    Attributes:
        acquisition_devices (dict): Dictionary holding the acquisition 
            devices to be used during the measurement. Entries are of the
            form: ``{inst_name: device}`` using :class:`Device`.
        scan_devices (dict): Dictionary holding the scan
            devices to be used during the measurement. Entries are of the
            form: ``{inst_name: device}`` using :class:`Device`.
        scan_collection (dict): Dictionary holding the scans to perform
            during the measurement. Entries are of the form:
            ``{scan_name: scan_settings}``. The *scan_name* is a combination
            of the scan device for that scan, and the device parameter
            that is being scanned, e.g., *SG1-frequency*.
        averages (int): Number of times to repeat the measurement. No averaging
            is done in the measurement function, but is instead handled when analyzing
            the data with :py:mod:`baecon.data`.
    """

    acquisition_devices: dict = field(default_factory=dict)
    scan_devices: dict = field(default_factory=dict)
    scan_collection: dict = field(default_factory=dict)
    averages: int = 1


def make_measurement_settings(meas_config: dict) -> Measurement_Settings:
    """Make a Measurement_Settings object from configurations in meas_configs 
        dictionary, which has keys *acquisition_devices*,
        *scan_devices*, and *scan_collection* (i.e., the attributes of a
        Measurement settings object).

    Args:
        meas_configs (dict): Dictionary with configurations for 
        * :attr:`Measurement_Settings.acquisistion_devices` 
        * :attr:`Measurement_Settings.scan_devices`
        * :attr:`Measurement_Settings.scan_collection`

    Returns:
        Measurement_Settings: Measurement_Settings object.
    """
    ms = Measurement_Settings()
    for device_config in list(meas_config['acquisition_devices'].values()):
        add_device(device_config, ms.acquisition_devices)
    for device_config in list(meas_config['scan_devices'].values()):
        add_device(device_config, ms.scan_devices)
    for scan_settings in list(meas_config['scan_collection'].values()):
        add_scan(scan_settings,
                 ms.scan_devices[scan_settings['name']],
                 ms)
    ms.averages = meas_config['averages']
    return ms


def generate_measurement_config(ms: Measurement_Settings):
    """Make configuration dictionary from Measurement_Settings object.
        Configuration file will be a dict like file (e.g., ``json``, ``yaml``, 
        ``toml``) with structure.
        ``{'acquisition_devices': {'device_name': configuration, ...},
        'scan_devices': {'device_name': configuration, ...}, 
        'scan_collections': {'scan_name': settings, ...}
        }``

    Args:
        ms (Measurement_Settings): Measurement settings from which to generate 
        the configuration.
    """
    acq_insts, scan_insts, scans = {}, {}, {}
    for key in list(ms.acquisition_devices.keys()):
        acq_insts.update({key: ms.acquisition_devices[key].configuration})
    for key in list(ms.scan_devices.keys()):
        scan_insts.update({key: ms.scan_devices[key].configuration})
    for key in list(ms.scan_collection.keys()):
        scans.update({key: ms.scan_collection[key]['settings']})

    meas_config = {'acquisition_devices': acq_insts,
                   'scan_devices': scan_insts,
                   'scan_collection': scans,
                   'averages': ms.averages}
    return meas_config


def add_device(device_config: dict, devices: dict):
    """Adds an device object constructed from the configuration in 
        config_file to the device dictionary devices. This dictionary 
        will be the :attr:`Measurement_Settings.acquisition_devices` or 
        :attr:`Measurement_Settings.scan_devices`.

    Args:
        config_file (str): file name of device configurations
        devices (dict): dictionary of measurement devices (acquisition or scan)
    """

    device = make_device(device_config)
    devices.update({device.name: device})
    return


def make_device(config: dict) -> dict:
    """Import the device module give by config['device'] and makes
        an device of that module type (e.g., SG380). 
        Returns a dictionary of configurations, now with the device object
        as the value of the 'device' entry.

    Args:
        config (dict): :class:`Device` configuration

    Returns:
        dict: New device configuration with device object.
    """
    try:
        to_import = config["device"]
    except KeyError as e:
        print(
            f"make_device() could not find {e} not found in device configuration.")

    inst_path = os.path.abspath(
        f'{Devices_directory}\\{to_import}\\{to_import}.py')
    spec = importlib.util.spec_from_file_location(to_import, inst_path)
    device_module = importlib.util.module_from_spec(spec)
    sys.modules[to_import] = device_module
    spec.loader.exec_module(device_module)
    available_modules = dict(inspect.getmembers(
        device_module, inspect.isclass))
    device = available_modules[to_import](config)
    print(f'dev: {device}')
    # full_device = config
    # full_device.update({'device': device})
    return device


def add_scan(scan_settings: dict,
             scan_device: Device,
             ms: Measurement_Settings):
    """Makes scan collection based in input scan_collection dictionary 
        and adds the collection to :class:`Measurement_Settings`

    Args:
        scan_collection (dict): Scan collection dictionary.
        ms (Measurement_Settings): :class:`Measurement_Settings` to be
        updated with scan collection.
    """
    scan = make_scan(scan_settings, scan_device)
    try:
        ms.scan_collection.update(scan)
    except TypeError:
        pass
    return


def make_scan(scan_settings: dict, device: Device) -> dict:
    """Makes a scan dictionary from the input scan settings. Returns 
        scan to add to :attr:`Measurement_Settings.scan_collection`.

    Args:
        scan_settings (dict): Settings for a single scan.

    Returns:
        dict: scan dictionary to add to scan collection.
    """
    # scan_settings = clean_scan_settings(scan_settings)

    try:
        if not scan_settings['device'] == device.__class__.__name__:
            print('Settings do not match selected device')
            return
        scan_key = f"{device.name}-{scan_settings['parameter']}"
        scan_settings.update({'name': device.name})
        scan = {'device': device,
                'parameter': scan_settings['parameter'],
                'schedule': make_scan_schedule(scan_settings),
                'repetitions': scan_settings['repetitions'],
                'randomize': scan_settings['randomize']}
    except KeyError as e:
        print('make_scan could not find {e} in the supplied scan_settings.')

    return {scan_key: {'settings': scan_settings, 'scan': scan}}


def make_scan_schedule(scan_settings: dict) -> np.ndarray:
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

    For example:
    ``scan_settings = {'name': 'SG1', 'device': 'SG380', 'parameter': frequency,
    'min': 1, 'max': 2, 'points': 5, 'repetitions': 2, 'randomize': False, 'note': ''}``

    yields schedule: ``np.ndarray([1.0, 1.25, 1.5, 1.75, 2.0, 1.0, 1.25, 
                                    1.5, 1.75, 2.0])``

    Args:
        scan_settings (dict): Scan settings

    Returns:
        np.ndarray: np.ndarray with scan schedule
    """

    def linear():
        array = np.linspace(
            scan_settings['min'], scan_settings['max'], scan_settings['points'])
        return np.tile(array, scan_settings['repetitions'])

    def log():
        array = np.logspace(
            scan_settings['min'], scan_settings['max'], scan_settings['points'])
        return np.tile(array, scan_settings['repetitions'])

    def custom():
        array = np.array(custom_schedule(scan_settings['note']))
        return np.tile(array, scan_settings['repitions'])

    def constant():
        return np.tile(scan_settings['min'], scan_settings['repetitions'])
    schedule = {'linear': linear, 'log': log,
                'custom': custom, 'constant': constant}
    return schedule[scan_settings['scale']]()


def custom_schedule(note: str) -> np.ndarray:
    """Create a custom scan schedule from a saved file specified in the 
        note setting as `custom: file_name`. File type should be `.txt` 
        or `.npy`. 

        :todo:
        The method can be expand with other file types. May want to change
        to `'custom'` using a method supplied by `'note'`.

    Args:
        note (str): _description_

    Returns:
        np.ndarray: _description_
    """

    file_name = json.loads(note)['custom']
    file_type = os.path.splitext(file_name)[-1]
    with open(file_name, 'r') as f:
        if 'npy' in file_type:
            array = np.load(f, 'r')
        else:
            array = np.loadtxt(f)
    return array


def load_custom_scan_file():
    return

# how to implement method to add/change scan settings??
# def define_scan_settings():
#     scan_settings = {'device': '', 'parameter': '',
#         'minimum': 0, 'maximum': 0, 'points': 1,
#         'repetitions': 1, 'scale': 'linear', 'randomize': False,
#         'note': ''}
#     return scan_settings
