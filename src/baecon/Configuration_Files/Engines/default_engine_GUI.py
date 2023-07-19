""":note:
   This is the default engine. We should be able to add/import additional
   engines, like one based on OptBayes.

   This engine performs the scans recursively in the order they are listed
   in the scan_collection.

   ``for i in scan1: for j in scan2: for k in scan3: ...``

"""

import asyncio
import copy
import queue
import threading
from dataclasses import dataclass

import baecon as bc
import numpy as np
import xarray as xr

## should be working with this, but if baecon cannot be found uncomment this
# import sys
# sys.path.insert(0,'C:\\Users\\walsworth1\\Documents\\Jupyter_Notebooks\\baecon')


@dataclass
class abort:
    """Used to stop all threads with keyboard input ``'abort'``."""

    abort_measurement = False


def scan_recursion(
    scan_list: dict,
    acquisition_methods: dict,
    data_queue: queue.Queue,
    parameter_holder: dict,
    total_depth: int,
    present_depth: int,
    abort: abort,
) -> None:
    """Peforms measurement scan with parameters given in :arg:`paramater_holder`.

       At each parameter all acquisiton deivces will be called in the order they
       appear in `acquisition_methods`.The scan is performed recursively in the
       order scans are listed in`scan_list`.

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
        abort (bool): Used to break loop recursion. Exits measurement if ``True``
    """
    if present_depth == total_depth - 1:
        scan_now = scan_list[present_depth]
        for val in scan_now["schedule"]:
            parameter_holder[scan_now["parameter"]] = val
            scan_now["device"].write(scan_now["parameter"], val)
            # time.sleep(0.5)   # Add a delay in sec before next scan
            data = {}
            for acq_name, acq_method in list(acquisition_methods.items()):
                data[acq_name] = acq_method.read()
            data_queue.put({"parameters": parameter_holder.copy(), "data": data})
            # time.sleep(0.01)
            if abort.abort_measurement:
                break
    else:
        scan_now = scan_list[present_depth]
        for idx in scan_now["schedule"]:
            parameter_holder[scan_now["parameter"]] = idx
            scan_recursion(
                scan_list,
                acquisition_methods,
                data_queue,
                parameter_holder,
                total_depth,
                present_depth + 1,
                abort,
            )
            if abort.abort_measurement:
                break
    return


def consecutive_measurement(
    scan_collection: dict, acquisition_devices: dict, data_queue: queue.Queue, abort: abort
) -> None:
    """Performs measurement in order of scans listed in scan_collection.
       The scan underneath will finish before the scan above moves on to the
       next point.

    Args:
        scan_collection (dict): Collection of scans for the measurement to perform
        acquisition_devices (dict): Devices for acquiring data
        data_queue (queue.Queue): Queue use to pass measurement to the data thread
        abort (bool): Exits measurement if ``True``
    """
    total_depth = len(scan_collection)
    current_depth = 0
    parameter_holder = {}

    scan_list = make_scan_list(scan_collection)

    scan_recursion(
        scan_list,
        acquisition_devices,
        data_queue,
        parameter_holder,
        total_depth,
        current_depth,
        abort,
    )
    return


def make_scan_list(
    scan_collection: dict,
) -> list[dict[bc.Device, str, np.ndarray]]:
    """Builds a list of scans from the scan settings of each entry in the
       scan collection.

    Args:
        scan_collection (dict): Scan collection from :py:class:`Measurement_Settings`

    Returns:
        list[dict[bc.Device, str, np.ndarray]]: List of scans to perform with
        the specified device, device parameter (str), and numpy array of values
        to scan over.
    """
    try:
        scan_list = []
        for key in list(scan_collection.keys()):
            scan = scan_collection[key]["scan"]
            scan_list.append(scan)
    except KeyError:
        print("engine could not find {e} in the scan settings {scan_collection[key]}")
    return scan_list


def measure_thread(ms: bc.Measurement_Settings, data_queue: queue.Queue, abort: abort):
    """Thread that performs measurements.

       Value from the measurements are put in a Queue object (`data_queue`), which
       are then used in the :py:meth:`data_thread`. When a scan is finished,
       "scan_done" is put in the queue and "measurement_done" is put in the
       queue when the measurement is done.

    Args:
        ms (bc.Measurement_Settings): Measurement_settings object specifying the measurement to do.
        data_queue (queue.Queue): Used to move data between the measure and data threads.
        abort (abort): Exits measurement if ``True``
    """
    scans = ms.scan_collection
    acq_methods = ms.acquisition_devices
    for idx in np.arange(ms.averages, dtype=np.int32):
        consecutive_measurement(scans, acq_methods, data_queue, abort)
        data_queue.put(["scan_done"])
        print(f"measurement {idx} done")
        if abort.abort_measurement:
            break
    data_queue.put(["measurement_done"])
    return


def data_thread(md: bc.Measurement_Data, data_queue: queue.Queue, abort: abort) -> None:
    """Recieves data from the `measure_thread` and stores it in a Measurement_Data
       object.

       The data is organized in the Measurement_Data by the aquisition key
       and number of averages, e.g., "DAQ1-3", starting at zero.

    Args:
        md (bc.Measurement_Data): Measurement_Data object for storing the measured data.
        data_queue (queue.Queue): Used to move data between the measure and data threads.
        abort (abort): Exits measurement if ``True``
    """
    print("start data thread")
    data_done = ""
    idx = 0
    # md.data_measurement_holder = copy.deepcopy(md.data_template)
    while not data_done == "measurement_done":
        md.data_current_scan = copy.deepcopy(md.data_template)
        data_done = get_scan_data(md.data_current_scan, data_queue, data_done, abort)
        if abort.abort_measurement:
            break
        if "scan_done" in data_done:
            for acq_key in list(md.data_current_scan.keys()):
                md.data_set[f"{acq_key}-{idx}"] = md.data_current_scan[acq_key]
            data_done = ""
            idx += 1
    abort.abort_measurement = True
    md.data_current_scan = copy.deepcopy(md.data_template)
    return


def get_scan_data(
    data_arrays: xr.DataArray, data_queue: queue.Queue, data_done: str, abort: abort
) -> str:
    """Retrives data from queue and stores the data.

       While loop looks for new values in `data_queue` and stores it in a
       DataArray, which itself is held in `Measurement_Data`. The while loop is
       exited when ["scan_done"] or ["measurement_done"] are read from the queue.
       The data comes in a form of a dictionary with at least two entries (length 2).
    Args:
        data_arrays (xr.DataArray): DataArray corresponding to the specific parameter being scanned.
        data_queue (queue.Queue): Used to move data between the measure and data threads.
        data_done (str): Used to communicate "scan_done" or "measurement_done" to the data thread.
        abort (abort): abort (abort): Exits measurement if ``True``

    Returns:
        str: "scan_done" or "measurement_done"
    """
    while not (data_done == "scan_done" or data_done == "measurement_done"):
        if abort.abort_measurement:
            break
        new_data = data_queue.get(timeout=10000)
        if len(new_data) == 1:
            data_done = new_data[0]
        else:
            data = new_data["data"]
            for acq_key in list(data.keys()):
                data_arrays[acq_key].loc[new_data["parameters"]] = data[acq_key]
    return data_done


def abort_monitor(abort: abort):
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


# def get_data(data_array):
#     trimmed = data_array.dropna("frequency")
#     x = trimmed.coords["frequency"].values
#     y = np.mean(trimmed.values, axis=0)
#     return x, y


# def calc_avg_data(data_set):
#     data_array = data_set.to_array()
#     x = data_array.coords["frequency"].values
#     vals = data_array.values
#     mean_samps = np.mean(vals, axis=vals.ndim - 1)
#     mean_scans = np.mean(mean_samps, axis=0)
#     y = mean_scans
#     return x, y


async def perform_measurement(
    ms: bc.Measurement_Settings,
    md: bc.Measurement_Data,
    abort: abort,
) -> bc.Measurement_Data:
    """The core method of the engine, which starts the measurement and data threads.
       All :py:class:`engine` have this method.

    Args:
        ms (bc.Measurement_Settings): _description_
        md (_type_): _description_
        abort (_type_): _description_

    Returns:
        bc.Measurement_Data: _description_
    """
    data_cue = queue.Queue()

    m_t = threading.Thread(
        target=measure_thread,
        args=(
            ms,
            data_cue,
            abort,
        ),
    )
    d_t = threading.Thread(target=data_thread, args=(md, data_cue, abort))
    m_t.start()
    d_t.start()
    return


async def main(ms, md, abort):
    task = asyncio.create_task(perform_measurement(ms, md, abort))
    await task
    return task


if __name__ in {"__main__", "__mp_main__"}:
    meas_config = bc.utils.load_config(
        "C:\\Users\\walsworth1\\Documents\\Jupyter_Notebooks\\baecon\\tests\\generated_config.toml"
    )

    ## Need to update using plot_card
    # ms = bc.make_measurement_settings(meas_config)

    # md = Measurement_Data()
    # md.data_template = bc.create_data_template(ms)
    # md.assign_measurement_settings(ms)
    # md.data_current_scan = copy.deepcopy(md.data_template)

    # fig = go.Figure()

    # with ui.card():
    #     plot1 = ui.plotly(fig).classes("w-full h-25")
    #     plot1.update()

    # # app.on_shutdown(main)
    # abort_flag = abort()

    # def trigger_abort():
    #     abort_flag.abort_measurement = True

    # def ppp():
    #     plot_data(plot1, md)

    # check = abort()

    # def make_check():
    #     check.abort_measurement = not check.abort_measurement

    # ui.button("clci", on_click=partial(main, *(ms, md, abort_flag)))
    # ui.button("abort", on_click=trigger_abort)
    # line_updates = ui.timer(0.15, partial(plot_data, *(plot1, md)), active=False)
    # line_checkbox = ui.checkbox("active").bind_value(line_updates, "active")
    # ui.button("Check", on_click=make_check)
    # line_checkbox.bind_value(check, "abort_measurement")
    # ui.run(port=8081)
