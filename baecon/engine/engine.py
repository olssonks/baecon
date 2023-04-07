import baecon as bc

import queue, threading, copy
from dataclasses import dataclass
import numpy as np


@dataclass
class abort:
    flag = False

def scan_recursion(scan_list:dict, acquisition_methods:dict, data_queue:queue.Queue,
                    parameter_holder:dict, total_depth:int, present_depth:int,
                    abort:abort)->None:
    """Peforms measurement scan with supplied. At each parameter all acquisiton
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
        abort (abort): :class:abort used to break loop recursion.
    """    
    if present_depth == total_depth - 1:
        scan_now = scan_list[present_depth]
        for idx in scan_now['schedule']:
            parameter_holder[scan_now['parameter']] = idx
            data = {}
            for acq_name, acq_method in list(acquisition_methods.items()):
                data[acq_name] = acq_method.read()
            data_queue.put({'parameters': parameter_holder.copy(), 
                            'data': data}
            )
            if abort.flag == 'abort':
                break
    else:
        scan_now = scan_list[present_depth]
        for idx in scan_now['schedule']:
            parameter_holder[scan_now['parameter']] = idx
            scan_recursion(scan_list, acquisition_methods, data_queue,
                    parameter_holder, total_depth, present_depth+1, abort)
            if abort.flag == 'abort':
                break
    return

def consecutive_measurement(scan_collection:dict, 
                            acquisition_devices:dict, 
                            data_queue:queue.Queue,
                            abort:abort)->None:
    """Performs measurement in order of scans listed in scan_collection. The scan underneath will
        finish before the scan above moves on to the next point.

    Args:
        scans (dict): _description_
        acquisition_methods (dict): _description_
        data_queue (queue.Queue): _description_
        abort (abort): _description_
    """   
    total_depth = len(scan_collection)
    current_depth = 0
    parameter_holder = {}
    
    scan_list = make_scan_list(scan_collection)
    
    scan_recursion(scan_list, acquisition_devices, data_queue, 
                        parameter_holder, total_depth, current_depth,
                        abort)
    return
    
def make_scan_list(scan_collection:dict)->list:
    """Builds a list of scans from the scan settings of each entry in the
        scan collection.

    Args:
        scan_collection (dict): Scan collection from :class:`Measurement_Settings`

    Returns:
        list: _description_
    """    
    try:
        scan_list = []
        for key in list(scan_collection.keys()):
            scan = scan_collection[key]['scan']
            scan_list.append(scan)
    except KeyError as e:
        print('engine could not find {e} in the scan settings {scan_collection[key]}')
    return scan_list


def measure_thread(ms:bc.Measurement_Settings, data_queue, abort:abort):
    scans = ms.scan_collection
    acq_methods = ms.acquisition_devices
    for idx in np.arange(ms.averages, dtype=np.int32):
        consecutive_measurement(scans, acq_methods, data_queue, abort)
        data_queue.put(['scan_done'])
    data_queue.put(['measurement_done'])
    return
    
def data_thread(md:bc.Measurement_Data, data_queue, abort:abort):
    print('start data thread')
    data_done = ''
    idx = 0
    while not data_done == 'measurement_done':
        data_arrays = copy.deepcopy(md.data_template)
        data_done = get_scan_data(data_arrays, data_queue, data_done, abort)
        if not data_queue.empty():
            for acq_key in list(data_arrays.keys()):
                md.data_set[f'{acq_key}_{idx}'] = data_arrays[acq_key]
            idx+=1
        if abort.flag:
                break
        if data_done == 'scan_done':
            data_done = ''
    abort.flag = True
    print('Measurement Done, press enter.')
    return

def get_scan_data(data_arrays, data_queue, data_done, abort): 
    while not (data_done == 'scan_done' or data_done == 'measurement_done'):
        if abort.flag:
            break
        new_data = data_queue.get(timeout = 5)
        if len(new_data) == 1:
            data_done = new_data[0]
        else:
            data = new_data['data']
            for acq_key in list(data.keys()):
                data_arrays[acq_key].loc[new_data['parameters']] = data[acq_key]
    return data_done

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


def perform_measurement(ms:bc.Measurement_Settings)->bc.Measurement_Data:
    
    abort_flag = abort()
    data_cue = queue.Queue()

    meas_data = bc.Measurement_Data()
    meas_data.data_template = bc.create_data_template(ms)
    meas_data.put_measurement_settings(ms)
        
    m_t=threading.Thread(target=measure_thread, args=(ms, data_cue, abort_flag,))
    d_t=threading.Thread(target=data_thread, args=(meas_data, data_cue, abort_flag,))
    a_t=threading.Thread(target=abort_monitor, args=(abort_flag,))
    m_t.start()
    d_t.start()
    a_t.start()
    
    while (m_t.is_alive() or d_t.is_alive() or a_t.is_alive()):
        pass
    
    return meas_data