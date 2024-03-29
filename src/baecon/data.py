""":note:
    Most analysis will occur with specifically imported modules per experiment.
    Module will have a main function *analyze_data* that will return the
    reduced data to plot.

    Need to think about how to pass data from the measurement thread to the
    data analysis and plotting thread. May need an object that is just the
    most recent data taken, and not the full :py:mod:`xarrray.DataArray` object.

.. todo::

    - add some basic analysis functions like averaging samples
    - Saving reduced data?? May want to make another data structure,
      the processed data may not have the same dimensions as
      the `Measurement_Data.dataset`

"""

from dataclasses import dataclass, field

import numpy as np
import xarray as xr

import baecon as bc


@dataclass
class Measurement_Data:
    """Data structure for handling data in ``baecon``.

    Attributes:
        data_template (:py:mod:`xarrray.DataArray`): A template of how the data
            will be stored for the measurement. For each full scan collection
            a copy of the template is supplied for storing the data for that
            scan collection. One full scan will fill the entire array.
        data_current_scan (:py:mod:`xarrray.DataArray`): Holds the data
            for the currently running scan. After scan is finished, this data
            is add to ``data_set``.
        data_set (:py:mod:`xarrray.Dataset`): The full data for the measurement.
            After a scan collection, the :py:mod:`xarrray.DataArray` is added to
            the ``data_set``. When taking multiple runs of the scan collection, i.e,
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

    def assign_measurement_settings(self, ms: bc.Measurement_Settings) -> None:
        self.data_template = bc.create_data_template(ms)
        measurement_config = bc.generate_measurement_config(ms)
        self.data_set.attrs["measurement_config"] = measurement_config
        self.data_set.attrs["scan_parameters"] = [
            scan_setting["parameter"]
            for scan_setting in measurement_config["scan_collection"].values()
        ]
        self.data_set.attrs["acquire_methods"] = list(
            measurement_config["acquisition_devices"].keys()
        )


def create_data_template(Measurement_Setings: bc.Measurement_Settings) -> xr.DataArray:
    """Creates an xarray.DataArray object based on the measurement settings.
        The dimenions will be based on the parameters to scan in
        Measurement_Settings.scan_collection and the samples to read in
        Measurement_Settings.acquisition_devices.
        This template is used to create entries for storing the data in
        a Measurement_Data.data_set object.

    Args:
        Measurement_Setings (Measurement_Settings): Current settings of the measurement

    Returns:
        xr.DataArray: xarray.DataArray object with dimenions of parameters to scan
                    and acquisition samples to read. Values are initialized to np.nan
    """
    template = {}
    scans = Measurement_Setings.scan_collection
    acquisitions = Measurement_Setings.acquisition_devices

    for acq_key in list(acquisitions.keys()):
        coords = {}
        sample_array = np.arange(acquisitions[acq_key].acq_data_size)
        for scan_key in list(scans.keys()):
            coords.update(
                {scans[scan_key]["scan"]["parameter"]: scans[scan_key]["scan"]["schedule"]}
            )
        coords.update({f"{acq_key}": sample_array})
        dimensions = []
        for arr in list(coords.values()):
            dimensions.append(arr.size)

        template[acq_key] = xr.DataArray(
            np.full(dimensions, np.nan), dims=list(coords.keys()), coords=coords
        )
    return template


## include some basic functions for analyzing the data
## but mainly import modules of Data_Analysis folder
## main function in module will be 'analyze_data'


def data_from_module(data: Measurement_Data, file_name: str):
    """Load module and perform its analysis.

    This allows for different analysis to be performed (and plotted) during
    the measurement. This function is mostly useful for the GUI.

    Args:
        data (Measurement_Data): :py:class:`Measurement_Data` from the meaurement.
        file_name (str): File/path name for the data analysis module to load.

    Returns:
        _type_: _description_
    """

    analysis_module = bc.utils.load_module_from_path(file_name)

    reduced_data = analysis_module.analyze_data(data)

    return reduced_data


def save_baecon_data(
    md: Measurement_Data, file_name: str, format: str = ".zarr", options=None
) -> None:
    """Saves measurement data to choice of ``format``.
       The default format is a Zarr group file. Possible formats:
       ``zarr``, ``netcdf``, ``hdf5``, and ``csv``.

    ``zarr`` and ``netcdf`` play well with :py:mod:`xarray`. For the other
    formats data is coverted :py:mod:`pandas` then saved.

    .. todo::
        Need to check settings saved as metadata correctly

        Possible formats to implement in the future: parquet, feather.

    Args:
        md (:py:mod:`Measurement_Data`): Configuration of measurement.
        file_name (str): File name for saving data.
        format (str, optional): File format to use, defaults to '.zarr'
        options (optional): Options for extension in the future, likely
        chunking and compression.
    """

    def use_zarr():
        if options:
            md.data_set.to_zarr(file_name, **options)
        else:
            md.data_set.to_zarr(file_name, mode="w")
        return

    def use_netcdf():
        if options:
            md.data_set.to_netcdf(file_name, **options)
        else:
            md.data_set.to_netcdf(file_name)
        return

    def use_hdf5():
        df = md.data_set.to_pandas()
        if options:
            df.to_hdf(file_name, **options)
        else:
            df.to_hdf(file_name)
        return

    def use_csv():
        df = md.data_set.to_dataframe()
        df.to_csv(file_name)
        return

    formats = {".zarr": use_zarr, ".nc": use_netcdf, ".h5": use_hdf5, ".csv": use_csv}

    formats[format]()
    return
