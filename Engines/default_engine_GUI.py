''':note:
   This is the default engine. We should be able to add/import additional 
   engines, like one based on OptBayes.

   This engine performs the scans recursively in the order they are listed
   in the scan_collection.

   ``for i in scan1: for j in scan2: for k in scan3: ...``
   
'''

import sys
sys.path.insert(0,'C:\\Users\\walsworth1\\Documents\\Jupyter_Notebooks\\baecon')
import time
import baecon as bc
from nicegui import ui, app
import plotly.graph_objects as go

import queue, threading, copy
import asyncio
from dataclasses import dataclass
import numpy as np

import time

@dataclass
class abort:
    """Used to stop all threads with keyboard input ``'abort'``.
    
    """   
    flag = False

def scan_recursion(scan_list:dict, acquisition_methods:dict, data_queue:queue.Queue,
                    parameter_holder:dict, total_depth:int, present_depth:int,
                    abort:abort)->None:
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
            time.sleep(0.001)   # Add a delay in sec before next scan
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
                        abort)
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
        if abort.flag:
                break
        if 'scan_done' in data_done:
            for acq_key in list(data_arrays.keys()):
                md.data_set[f'{acq_key}_{idx}'] = data_arrays[acq_key]
            data_done = ''
            idx+=1
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


def perform_measurement(ms:bc.Measurement_Settings, 
                        md:bc.Measurement_Data)->bc.Measurement_Data:
    
    abort_flag = abort()
    data_cue = queue.Queue()
        
    m_t=threading.Thread(target=measure_thread, args=(ms, data_cue, abort_flag,))
    d_t=threading.Thread(target=data_thread, args=(md, data_cue, abort_flag,))
    a_t=threading.Thread(target=abort_monitor, args=(abort_flag,))
    
    m_t.start()
    d_t.start()
    a_t.start()
    while (m_t.is_alive() or d_t.is_alive() or a_t.is_alive()):
        pass
    
    return
    
def simple_plot(dataset):
    with ui.card():
        scatter = go.Scatter()
        fig = go.Figure()
        plot = ui.plotly(fig)

    def update_plot():
        x, y= get_data(dataset.data_set)
        fig.data = []
        fig.add_trace(go.Scatter(x=x, y=y))
        plot.update()
    ui.timer(0.1, update_plot)
    ui.run(port=8666)
    return
    
def get_data(data_array):
    trimmed = data_array.dropna('frequency')
    x = trimmed.coords['frequency'].values
    y = trimmed.to_array().values.mean(axis=1)
    return x, y


def main():
    # meas_config = bc.utils.load_config("C:\\Users\\walsworth1\\Documents\\Jupyter_Notebooks\\baecon\\tests\\generated_config.toml")
    
    # ms = bc.make_measurement_settings(meas_config)
    # scans = ms.scan_collection
    # acq_methods = ms.acquisition_devices
    
    # meas_data = bc.Measurement_Data()
    # meas_data.data_template = bc.create_data_template(ms)
    # meas_data.assign_measurement_settings(ms)
    
    abort_flag = abort()
    data_cue = queue.Queue()
    # for idx in np.arange(ms.averages, dtype=np.int32):
    #     consecutive_measurement(scans, acq_methods, data_cue, abort)
    data = perform_measurement(ms,md)
    #bc.utils.save_baecon_data(data, 'C:\\Users\\walsworth1\\Documents\\Jupyter_Notebooks\\baecon\\tests\\test_data.zarr', format='.zarr')  

if __name__ in {"__main__", "__mp_main__"}:
    meas_config = bc.utils.load_config("C:\\Users\\walsworth1\\Documents\\Jupyter_Notebooks\\baecon\\tests\\generated_config.toml")
    
    ms = bc.make_measurement_settings(meas_config)
    scans = ms.scan_collection
    acq_methods = ms.acquisition_devices
    
    md = bc.Measurement_Data()
    md.data_template = bc.create_data_template(ms)
    md.assign_measurement_settings(ms)
    
    with ui.card():
        scatter = go.Scatter()
        fig = go.Figure()
        plot = ui.plotly(fig)

    def update_plot():
        x, y= get_data(md.data_set)
        fig.data = []
        fig.add_trace(go.Scatter(x=x, y=y))
        plot.update()

    
    app.on_startup(main)
    ui.timer(0.1, update_plot)
    ui.run(port=8666)