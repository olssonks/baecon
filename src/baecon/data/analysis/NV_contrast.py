import baecon as bc
import numpy as np
import xarray as xr


def process_data(
    meas_data: bc.Measurement_Data, acquire_methods: list, scan_parameters: list
) -> tuple[dict, dict, dict]:
    current_data = process_current_data(meas_data.data_current_scan, scan_parameters)
    completed_data = completed_processed_data(meas_data, scan_parameters)
    average_data = average_processed_data(meas_data.processed_data_set, scan_parameters)
    return current_data, completed_data, average_data


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


def completed_processed_data(meas_data: bc.Measurement_Data, scan_parameters: list) -> dict:
    ## need to update for handling 2-d and N-d scans
    complete_data = {}
    parameter = scan_parameters[0]
    process_raw_and_add_to_processed(meas_data.raw_data_set, meas_data.processed_data_set)
    processed_data_set = meas_data.processed_data_set

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


def process_raw_and_add_to_processed(
    raw_data_set: xr.Dataset, processed_data_set: xr.Dataset
) -> None:
    unprocessed = list(raw_data_set.keys())
    processed = list(processed_data_set.keys())

    for scan_key in unprocessed - processed:
        raw_vals = raw_data_set.get(scan_key).values
        contrast, new_dims = calculate_contrast(raw_vals)
        completed_array = xr.DataArray(contrast, dims=new_dims)

        processed_data_set[scan_key] = completed_array

    return


def calculate_contrast(raw_data_array: xr.DataArray) -> tuple[np.array, list[str]]:
    raw_dims = raw_data_array.dims
    raw_samples = raw_data_array.values
    shape = raw_samples.shape
    samples_axis = len(raw_dims)
    number_of_samples = shape[samples_axis]
    samples_indices = np.arange(number_of_samples)

    signal = raw_samples.take(samples_indices[0::2], axis=samples_axis)
    reference = raw_samples.task(samples_axis[1::2], axis=samples_axis)

    contrast_values = signal / reference
    dims_without_sample_axis = raw_dims[:-1]
    return contrast_values, dims_without_sample_axis
