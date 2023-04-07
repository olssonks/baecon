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

def consecutive_measurement(scans, 
                            acquisition_methods, 
                            data_queue,
                            abort:abort)->None:
    
    total_depth = len(scans)
    current_depth = 0
    parameter_holder = {}
    
    scan_list = make_scan_list(scans)
    
    scan_recursion(scan_list, acquisition_methods, data_queue, 
                        parameter_holder, total_depth, current_depth,
                        abort)
    return
    
def make_scan_list(scans):
    scan_list = []
    for key in list(scans.keys()):
        scan = scans[key]['scan']
        scan_list.append(scan)
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
        
    m_t=threading.Thread(target=measure_thread, args=(ms, data_cue, abort_flag,))
    d_t=threading.Thread(target=data_thread, args=(meas_data, data_cue, abort_flag,))
    a_t=threading.Thread(target=abort_monitor, args=(abort_flag,))
    m_t.start()
    d_t.start()
    a_t.start()
    
    return meas_data