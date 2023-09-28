import baecon as bc
import numpy as np
import xarray as xr


def process_data(
    meas_data: bc.Measurement_Data,
    acquisition_methods: list[str],
    scan_parameters: list[str],
) -> tuple[dict, dict, dict]:
    current_data = process_current_data(
        meas_data.data_current_scan, acquisition_methods, scan_parameters
    )
    completed_data = completed_processed_data(
        meas_data, acquisition_methods, scan_parameters
    )
    average_data = average_processed_data(meas_data.processed_data_set, scan_parameters)
    return current_data, completed_data, average_data


def process_current_data(
    current_data_arrays: dict[str, xr.DataArray],
    acquisition_methods: list,
    scan_parameters: list,
) -> dict:
    ## data_array should be measurement_data_holder in Measurement_Data objecth
    ## need to update for handling 2-d and N-d scans
    trimmed_arrays = {}

    for acq in acquisition_methods:
        trimmed = current_data_arrays.get(acq)
        for param in scan_parameters:
            trimmed = trimmed.dropna(param)
        trimmed_arrays.update({acq: trimmed})

    ## for 1D (should make specifci function, then one for 2D)
    trimmed: xr.DataArray = trimmed_arrays.get(acquisition_methods[0])
    parameter = scan_parameters[0]
    acq_method = acquisition_methods[0]
    ## checks if all values are nan
    if trimmed.nbytes == 0:
        return
    else:
        contrast = calculate_contrast(trimmed, acq_method)
        x = contrast.coords.get(parameter).values
        y = contrast.values
    return {"current": (x, y)}


def completed_processed_data(
    meas_data: bc.Measurement_Data, acquisition_methods: list[str], scan_parameters: list
) -> dict:
    ## need to update for handling 2-d and N-d scans
    complete_data = {}
    parameter = scan_parameters[0]
    process_raw_and_add_to_processed(
        meas_data.raw_data_set, meas_data.processed_data_set, acquisition_methods
    )
    processed_data_set = meas_data.processed_data_set

    if processed_data_set.nbytes == 0:
        return
    else:
        for scan_key in list(processed_data_set.keys()):
            vals = processed_data_set.get(scan_key).values
            x = processed_data_set.get(scan_key).coords.get(parameter).values
            # y = np.mean(vals, axis=vals.ndim - 1)
            complete_data.update({scan_key: (x, vals)})
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
    raw_data_set: xr.Dataset, processed_data_set: xr.Dataset, acquisition_methods: list[str]
) -> None:
    unprocessed = set(raw_data_set.keys())
    processed = set(processed_data_set.keys())
    acq_method = acquisition_methods[0]
    for scan_key in unprocessed - processed:  ## does not work with lists, but should????
        raw_data_array = raw_data_set.get(scan_key)
        contrast = calculate_contrast(raw_data_array, acq_method)

        processed_data_set[scan_key] = contrast

    return


def calculate_contrast(
    raw_data_array: xr.DataArray, acquisition_methood: str
) -> xr.DataArray:
    samples_indices = raw_data_array.coords[acquisition_methood].values

    signal = raw_data_array.isel({acquisition_methood: samples_indices[0::2]}).mean(
        dim=acquisition_methood
    )
    reference = raw_data_array.isel({acquisition_methood: samples_indices[1::2]}).mean(
        dim=acquisition_methood
    )

    contrast = signal / reference
    return contrast
