import baecon as bc
import numpy as np
import xarray as xr


def process_data():
    return analyzed_data


def process_current_data(current_data_array: xr.DataArray, scan_parameters: list) -> dict:
    ## data_array should be measurement_data_holder in Measurement_Data object
    ## need to update for handling 2-d and N-d scans

    parameter = scan_parameters[0]
    trimmed = current_data_array.dropna(parameter)

    ## checks if all values are nan
    if trimmed.nbytes == 0:
        return
    else:
        x = trimmed.coords.get(parameter).values
        y = calculate_contrast(trimmed.values)
    return {"current": (x, y)}


def completed_processed_data(processed_data_set: xr.Dataset, scan_parameters: list) -> dict:
    ## need to update for handling 2-d and N-d scans
    complete_data = {}
    parameter = scan_parameters[0]
    if processed_data_set.nbytes == 0:
        return
    else:
        for scan_key in list(processed_data_set.keys()):
            vals = processed_data_set.get(scan_key).values
            x = processed_data_set.get(scan_key).coords.get(parameter).values
            y = np.mean(vals, axis=vals.ndim - 1)
            complete_data.update({scan_key: (x, y)})
    return complete_data


def average_processed_data(processed_data_set: xr.Dataset, scan_parameters: list) -> dict:
    ## need to update for handling multi dimensional scans
    if processed_data_set.nbytes == 0:
        return {}
    else:
        parameter = scan_parameters[0]
        data_array = processed_data_set.to_array()
        x = data_array.coords.get(parameter).values
        vals = data_array.values
        mean_scans = np.mean(vals, axis=0)
        y = mean_scans
    return {"Average": (x, y)}


def calculate_contrast(raw_samples):
    signal = raw_samples[:, 0::2]
    reference = raw_samples[:, 1::2]

    contrast = signal.mean(axis=0) / reference.mean(axis=0)

    return contrast
