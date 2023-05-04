import sys
sys.path.insert(0,'C:\\Users\\walsworth1\\Documents\\Jupyter_Notebooks\\baecon')
import time
import baecon as bc

import queue, threading, copy, asyncio
from dataclasses import dataclass, field
import numpy as np
import xarray as xr

from nicegui import ui, app
import plotly.graph_objects as go

@dataclass
class abort:
    """Used to stop all threads with keyboard input ``'abort'``.
    
    """   
    flag = False
    
@dataclass
class Measurement_Data:
    """Data structure for handling data in ``baecon``.
    
    Attributes:
        data_template (:py:mod:`xarrray.DataArray`): A template of how the data
            will be stored for the measurement. For each full scan collection
            a copy of the template is supplied for storing the data for that 
            scan collection. One full scan will fill the entire array.
        data_set (:py:mod:`xarrray.Dataset`): The full data for the measurement.
            After a scan collection, the :py:mod:`xarrray.DataArray` is added to
            the `data_set`. When taking multiple runs of the scan collection, i.e,
            :py:attr:`Measurement_Settings.averages`, each average will be an 
            :py:mod:`xarrray.DataArray` within ``data_set``. Additionally, all
            the measurement settings are are saved as metadtata held in the 
            attributes of `data`.
        processed_data (:py:mod:`xarrray.Dataset`): Processed data returned from
            :py:func:`data_from_module`.
    Methods:
        assign_measurement_settings (:py:class:`baecon.base.Measurement_Settings`): 
            creates and stores ``data_template``, and stores the measurement
            settings in ``data_set``.
    """    
    data_template: xr.DataArray = field(default_factory=xr.DataArray)
    data_measurement_holder: xr.DataArray = field(default_factory=xr.DataArray)
    data_set: xr.Dataset = field(default_factory=xr.Dataset)
    processed_data: xr.Dataset = field(default_factory=xr.Dataset)
    def assign_measurement_settings(self, ms:bc.Measurement_Settings)->None:
        self.data_template = bc.create_data_template(ms)
        settings = bc.generate_measurement_config(ms)
        self.data_set.assign_attrs(settings)
        
def scan_recursion(scan_list:dict, acquisition_methods:dict, data_queue:queue.Queue,
                    parameter_holder:dict, total_depth:int, present_depth:int,
                    abort:abort, data_arrays)->None:
    """Peforms measurement scan with supplied. 
       At each parameter all acquisiton
       deivces will be called in the order they appear in `acquisition_methods`.
       The scan is performed recursively in the order the scans a listed in
       `scan_list`.


    Args:
        scan_list (dict): Scans to perform.
        acquisition_methods (dict): Devices that will acquire data on each measurement
        data_queue (queue.Queue): Holder of data used to pass data from the measurement
            thread to the data thread.
        parameter_holder (dict): Current list of parameter settings. Used to
            keep track of recursion in data.
        total_depth (int): The total number of scans, i.e. how many nested loops
            are used in the scan.
        present_depth (int): Depth of current position in nested loops. Used to 
            keep track of recursion.
        abort (abort): :py:class:abort used to break loop recursion.
    """    
    if present_depth == total_depth - 1:
        scan_now = scan_list[present_depth]
        for val in scan_now['schedule']:
            parameter_holder[scan_now['parameter']] = val
            scan_now['device'].write(scan_now['parameter'], val)
            #time.sleep(0.5)   # Add a delay in sec before next scan
            data = {}
            print(parameter_holder)
            for acq_name, acq_method in list(acquisition_methods.items()):
                data[acq_name] = acq_method.read()
            # data_queue.put({'parameters': parameter_holder.copy(), 
            #                 'data': data}
            # )
            new_data = {'parameters': parameter_holder.copy(), 'data': data}
            data = new_data['data']
            for acq_key in list(data.keys()):
                data_arrays[acq_key].loc[new_data['parameters']] = data[acq_key]
            if abort.flag == 'abort':
                break
    else:
        scan_now = scan_list[present_depth]
        for idx in scan_now['schedule']:
            parameter_holder[scan_now['parameter']] = idx
            scan_recursion(scan_list, acquisition_methods, data_queue,
                    parameter_holder, total_depth, present_depth+1, abort, data_arrays)
            if abort.flag == 'abort':
                break
    return

def consecutive_measurement(scan_collection:dict, 
                            acquisition_devices:dict, 
                            data_queue:queue.Queue,
                            abort:abort, data_arrays)->None:
    """Performs measurement in order of scans listed in scan_collection. 
       The scan underneath will finish before the scan above moves on to the 
       next point.
    
    Args:
        scan_collection (dict): Collection of scans for the measurement to perform
        acquisition_devices (dict): Devices for acquiring data
        data_queue (queue.Queue): Queue use to pass measurement to the data thread
        abort (abort): Exits measurement if ``abort.flag == True``
    """
    total_depth = len(scan_collection)
    current_depth = 0
    parameter_holder = {}
    
    scan_list = make_scan_list(scan_collection)
    
    scan_recursion(scan_list, acquisition_devices, data_queue, 
                        parameter_holder, total_depth, current_depth,
                        abort, data_arrays)
    return
    
def make_scan_list(scan_collection:dict)->list:
    """Builds a list of scans from the scan settings of each entry in the 
       scan collection.

    Args:
        scan_collection (dict): Scan collection from :py:class:`Measurement_Settings`

    Returns:
        list: List of scans to perform
    """    
    try:
        scan_list = []
        for key in list(scan_collection.keys()):
            scan = scan_collection[key]['scan']
            scan_list.append(scan)
    except KeyError as e:
        print('engine could not find {e} in the scan settings {scan_collection[key]}')
    return scan_list


def measure_thread(ms:bc.Measurement_Settings, data_queue, abort:abort, data_arrays):
    scans = ms.scan_collection
    acq_methods = ms.acquisition_devices
    for idx in np.arange(ms.averages, dtype=np.int32):
        consecutive_measurement(scans, acq_methods, data_queue, abort, data_arrays)
        data_queue.put(['scan_done'])
    data_queue.put(['measurement_done'])
    return
    
def abort_monitor(abort:abort):
    while abort.flag == False:
        keystrk=input('Input "abort" to end measurement \n')
        if keystrk == "abort":
            abort.flag = keystrk
            break
        elif abort.flag==True:
            break
        else: 
            print('Input not understood')
    return