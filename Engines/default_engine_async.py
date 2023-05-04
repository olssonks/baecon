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
    data_current_scan: xr.DataArray = field(default_factory=xr.DataArray)
    data_set: xr.Dataset = field(default_factory=xr.Dataset)
    processed_data: xr.Dataset = field(default_factory=xr.Dataset)
    def assign_measurement_settings(self, ms:bc.Measurement_Settings)->None:
        self.data_template = bc.create_data_template(ms)
        measurement_config = bc.generate_measurement_config(ms)
        self.data_set.attrs['measurement_config'] = measurement_config
        self.data_set.attrs['scan_parameters'] = [scan_name for scan_name in 
                                                  list(measurement_config['scan_collection'].keys())]

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
            #time.sleep(0.5)   # Add a delay in sec before next scan
            data = {}
            for acq_name, acq_method in list(acquisition_methods.items()):
                data[acq_name] = acq_method.read()
            data_queue.put({'parameters': parameter_holder.copy(), 
                            'data': data}
            )
            time.sleep(0.01)
            if abort.flag:
                break
    else:
        scan_now = scan_list[present_depth]
        for idx in scan_now['schedule']:
            parameter_holder[scan_now['parameter']] = idx
            scan_recursion(scan_list, acquisition_methods, data_queue,
                    parameter_holder, total_depth, present_depth+1, abort)
            if abort.flag:
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
    abort.flag = False
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
    #md.data_measurement_holder = copy.deepcopy(md.data_template)
    while not data_done == 'measurement_done':
        md.data_measurement_holder = copy.deepcopy(md.data_template)
        data_done = get_scan_data(md.data_measurement_holder, data_queue, data_done, abort)
        if abort.flag:
                break
        if 'scan_done' in data_done:
            for acq_key in list(md.data_measurement_holder.keys()):
                md.data_set[f'{acq_key}_{idx}'] = md.data_measurement_holder[acq_key]
            data_done = ''
            idx+=1
    abort.flag = True
    md.data_measurement_holder = copy.deepcopy(md.data_template)
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
    # while abort.flag == False:
    #     keystrk=input('Input "abort" to end measurement \n')
    #     if keystrk == "abort":
    #         abort.flag = keystrk
    #         break
    #     elif abort.flag==True:
    #         break
    #     else: 
    #         print('Input not understood')
    return


def plot_task():

    ## using numpy isnan instead of xarray isnull (~30 us vs ~500 us)
    if not np.isnan(md.data_current_measurement['Daq1'].min().values):
        x,y = get_data(md.data_current_measurement['Daq1'])
        fig.data = []
        fig.add_trace(go.Scatter(x=x, y=y))
        for scan_key in list(md.data_set.keys()):
            x,y = get_data(md.data_set[scan_key])
            fig.add_trace(go.Scatter(x=x, y=y))
        if not len(md.data_set)==0:
            x,y = calc_avg_data(md.data_set)
            fig.add_trace(go.Scatter(x=x, y=y))
    if not len(md.data_set)==0 and np.isnan(md.data_current_measurement['Daq1'].min().values):
        fig.data=[]
        for scan_key in list(md.data_set.keys()):
            x,y = get_data(md.data_set[scan_key])
            fig.add_trace(go.Scatter(x=x, y=y))
        x,y = calc_avg_data(md.data_set)
        fig.add_trace(go.Scatter(x=x, y=y))
    plot1.update()


def get_data(data_array):
    trimmed = data_array.dropna('frequency')
    x = trimmed.coords['frequency'].values
    y = np.mean(trimmed.values, axis=0)
    return x, y
    
def calc_avg_data(data_set):
    data_array = data_set.to_array()
    x = data_array.coords['frequency'].values
    vals = data_array.values
    mean_samps = np.mean(vals, axis = vals.ndim -1)
    mean_scans = np.mean(mean_samps, axis=0)
    y = mean_scans
    return x, y

async def perform_measurement(ms:bc.Measurement_Settings, md)->bc.Measurement_Data:
    data_cue = queue.Queue()
        
    m_t=threading.Thread(target=measure_thread, args=(ms, data_cue, abort_flag,))
    d_t=threading.Thread(target=data_thread, args=(md, data_cue, abort_flag))
    m_t.start()
    d_t.start()
    return
    
async def main():
    task = asyncio.create_task(perform_measurement(ms,md))
    await task
    
    
# def perform_measurement(ms:bc.Measurement_Settings)->bc.Measurement_Data:
    
#     abort_flag = abort()
#     data_cue = queue.Queue()

#     meas_data = bc.Measurement_Data()
#     meas_data.data_template = bc.create_data_template(ms)
#     meas_data.assign_measurement_settings(ms)
        
#     m_t=threading.Thread(target=measure_thread, args=(ms, data_cue, abort_flag,))
#     d_t=threading.Thread(target=data_thread, args=(meas_data, data_cue, abort_flag,))
#     a_t=threading.Thread(target=abort_monitor, args=(abort_flag,))
#     m_t.start()
#     d_t.start()
#     a_t.start()
    
#     while (m_t.is_alive() or d_t.is_alive() or a_t.is_alive()):
#         pass
    
#     return meas_data



def run_measurement(GUI_fields):
    plot = GUI_fields.plot
    fig = go.Figure()
    plot_active = True
    
    return
    
## engine provides plot data function for ui.timer to use
## ui.timer needs to be in the plot card or engine card
def plot_data(the_plot, md:bc.Measurement_Data)->None:
    scan_parameters = md.data_set.attrs.get('scan_parameters')
    current_data    = get_current_data(md.data_current_scan, scan_parameters) ## returns dict {name: (x,y)}
    completed_data  = get_completed_data(md.data_set, scan_parameters) ## returns dict {name: (x,y)} for completed data
    average_data    = get_avg_data(md.data_set, scan_parameters)
    fig = {
        'data': [],
        'layout': {
            'margin': {'l': 15, 'r': 0, 't': 0, 'b': 15},
            'plot_bgcolor': '#E5ECF6',
            'xaxis': {'title':scan_parameters[0],'gridcolor': 'white'},
            'yaxis': {'gridcolor': 'white'},
        },
    }
    fig = main_trace_style({**current_data, **average_data})
    fig = secondary_trace_style(completed_data)
    the_plot.update_figure(fig)
    return
    
def get_current_data(data_array, scan_parameters:list):
    ## data_array should be measurement_data_holder in Measurement_Data object
    ## need to update for handling 2D scans
    parameter = scan_parameters[0]
    trimmed = data_array.dropna(parameter)
    x = trimmed.coords.get(parameter).values
    y = np.mean(trimmed.values, axis=0)
    return {'current': (x ,y)}
    
def get_completed_data(data_set, scan_parameters:list):
    ## need to update for handling 2D scans
    complete_data = {}
    parameter = scan_parameters[0]
    for scan_key in list(md.data_set.keys()):
        vals= md.data_set.get(scan_key).values
        x = md.data_set.get(scan_key).coords.get(parameter).values
        y = np.mean(vals, axis=vals.ndim -1)
        complete_data.update(scan_key, (x, y))
    x,y = calc_avg_data(md.data_set)
    fig.add_trace(go.Scatter(x=x, y=y))
    return
    
def get_avg_data(data_set, scan_parameters:list):
    ## need to update for handling 2D scans
    parameter = scan_parameters[0]
    data_array = data_set.to_array()
    x = data_array.coords.get(parameter).values
    vals = data_array.values
    mean_samps = np.mean(vals, axis = vals.ndim -1)
    mean_scans = np.mean(mean_samps, axis=0)
    y = mean_scans
    return {'Average': (x, y)}
    
def main_trace_style(fig, trace_data:dict):
    ## use for current data and average data
    for trace_name in list(trace_data.keys()):
        trace_name = list(trace_data.keys())[0]
        (x,y) = trace_data.get(trace_name)
        new_trace ={
            'type': 'scatter',
            'name': trace_name,
            'x'   : x,
            'y'   : y,
            'line': {'width': 4}
        },
        fig.get('data').append(new_trace)
    return fig
    
def secondary_trace_style(fig, trace_data:dict):
    ## use for completed data
    for idx, trace_name in enumerate(list(trace_data.keys())):
        trace_name = list(trace_data.keys())[0]
        (x,y) = trace_data.get(trace_name)
        new_trace ={
            'type'   : 'scatter',
            'name'   : trace_name,
            'x'      : x,
            'y'      : y,
            'line'   : {'width': 2},
            'opacity': max(0.5, 1 - 0.1*idx)
        },
        fig.get('data').append(new_trace)
    return fig


if __name__ in {"__main__", "__mp_main__"}:
    meas_config = bc.utils.load_config("C:\\Users\\walsworth1\\Documents\\Jupyter_Notebooks\\baecon\\tests\\generated_config.toml")
    
    ms = bc.make_measurement_settings(meas_config)
    
    md = Measurement_Data()
    md.data_template = bc.create_data_template(ms)
    md.assign_measurement_settings(ms)
    md.data_current_measurement = copy.deepcopy(md.data_template)
    
    fig = go.Figure()

    with ui.card():
        plot1 = ui.plotly(fig).classes('w-full h-25')
        plot1.update()
    
    #app.on_shutdown(main)
    abort_flag = abort()
    def trigger_abort():
        abort_flag.flag = True
    
    ui.button('clci', on_click=main)
    ui.button('abort', on_click=trigger_abort)
    ui.timer(0.1, plot_task)
    ui.run(port=8081)