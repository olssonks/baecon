'''

Procedure
    -load instruments
    -load DAQ
    -make measurement
        - make scan array from given parameter, min, max, order
            - multi-dimension possible
        - tell DAQ how to measure (# of reads, images, etc.)
    -run measurement
        - start DAQ
        - start scanning methods
    -plot/analyze results
    -save raw and processed data

'''
from . instrument import Instrument
from ._base import Measurement_Data, Measurement_Settings, abort

from dataclasses import dataclass
from typing import Union

import numpy as np
import xarray as xr

import queue
import threading
import copy


def scan_recursion(scan_list:dict, acquisition_methods:dict, data_queue:queue.Queue,
                    parameter_holder:dict, total_depth:int, present_depth:int,
                    abort)->None:

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
    
    
# scans = {'sg1-frequency': {'settings':'settings',
#                            'scan': {'instrument': 'SG380',
#                                     'parameter': 'frequency',
#                                     'schedule': np.linspace(1,2,3),
#                                     'repititions': 1,
#                                     'randomize': False,
#                                     'note':''}
#                            },
#          'ps-tau': {'settings':'settings',
#                            'scan': {'instrument': 'Pulse_Streamer',
#                                     'parameter': 'tau',
#                                     'schedule': np.linspace(10,20,3),
#                                     'repititions': 1,
#                                     'randomize': False,
#                                     'note':''}
#                            }
#          }

# consecutive_measurement(scans, {}, {}, abort_flag)


# # flag = [1]     
# # def normal(flag):
# #     while flag[0]==1:
# #         print(np.random.random(1))
# #         time.sleep(2)
# #         if flag[0]=='abort':
# #             print('The while loop is now closing')


# # def get_input(flag):
# #     keystrk=input('Press a key \n')
# #     # thread doesn't continue until key is pressed
# #     print('You pressed: ', keystrk)
# #     flag[0]=False
# #     print('flag is now:', flag)

# # n=threading.Thread(target=normal, args=(flag,))
# # i=threading.Thread(target=get_input, args=(flag,))
# # n.start()
# # i.start()

data_cue = queue.Queue()

def measure_thread(ms:Measurement_Settings, data_queue, abort:abort):
    scans = ms.scan_collection
    acq_methods = ms.acquisition_instruments
    for idx in np.arange(ms.averages, dtype=np.int32):
        consecutive_measurement(scans, acq_methods, data_queue, abort)
        data_queue.put(['scan_done'])
    data_queue.put(['measurement_done'])
    return
    
def data_thread(md:Measurement_Data, data_queue, abort:abort):
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
    return

def get_scan_data(data_arrays, data_queue, data_done, abort): 
    while not (data_done == 'scan_done' or data_done == 'measurement_done'):
        if abort.flag:
            break
        new_data = data_queue.get(timeout = 5)
        print(new_data)
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
        else: 
            print('Input not understood')
    return
    
def main(ms:Measurement_Settings, md:Measurement_Data):
    
    
    m_t=threading.Thread(target=measure_thread, args=(abort_flag,))
    d_t=threading.Thread(target=data_thread, args=(abort_flag,))
    a_t=threading.Thread(target=abort_monitor, args=(abort_flag,))
    m_t.start()
    d_t.start()
    a_t.start()
    
    return