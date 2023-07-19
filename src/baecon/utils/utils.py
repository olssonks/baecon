import argparse
import fileinput
import importlib
import json
import os
import sys

import toml
import yaml

import baecon as bc


def load_config(file: str, options=None) -> dict:
    """Loads configuration file ``file`` and returns dictionary of configurations.
       File type may be ``.toml``, ``.yml``, or ``.json``.

    Args:
        file (str): Configuration file to load.
        options (optional): Can be used in the future if functionality
        need extendsion, like encoding type.

    Returns:
        dict: Configuration dictionary

    """
    try:
        file = os.path.normpath(file)
        _, file_exetension = os.path.splitext(file)
        configuration = load_functions[file_exetension](file, options)
        return configuration
    except TypeError as e:
        pass  ## logging here
    return


def dump_config(config: dict, file: str, options=None) -> None:
    """Saves configuration dictionary into ``file``.
       File type may be ``.toml``, ``.yml``, or ``.json``. If no file type is
       given, ``.toml`` is used.

    Args:
        config (dict): Configuration dictionary to load
        file (str): Configuration file to load.
        options (optional): Can be used in the future if functionality
            need extendsion, like encoding type.

    """
    try:
        file = os.path.normpath(file)
        _, file_exetension = os.path.splitext(file)
        if file_exetension == "":
            file_exetension = ".toml"
            file = file + ".toml"
        dump_functions[file_exetension](config, file, options)
    except TypeError as e:
        pass  ## logging here
    return


def toml_load(file: str, options=None) -> dict:
    """Reads ``toml`` file and returns ``dict``.

    Args:
        file (str): path of ``toml`` file.
        options (optional): Can be used in the future if functionality
            need extendsion, like encoding type.

    Returns:
        dict: Dictionary of ``toml`` file contents.
    """
    with open(file) as f:
        loaded_toml = toml.load(f)
    return loaded_toml


def yaml_load(file: str, options=None) -> dict:
    """Reads ``yaml`` file and returns ``dict``.

    Args:
        file (str): path of ``yaml`` file.
        options (optional): Can be used in the future if functionality
            need extendsion, like encoding type

    Returns:
        dict: Dictionary of ``yaml`` file contents.
    """
    with open(file) as f:
        loaded_yaml = yaml.safe_load(f)
    return loaded_yaml


def json_load(file: str, options=None) -> dict:
    """Reads ``json`` file and returns ``dict``.

    Args:
        file (str): path of ``json`` file.
        options (optional): Can be used in the future if functionality
            need extendsion, like encoding type

    Returns:
        dict: Dictionary of ``json`` file contents.
    """
    with open(file) as f:
        loaded_json = json.loads(f)
    return loaded_json


def toml_dump(config: dict, file: str, options=None) -> None:
    """Write configuration dictionary (``config``) to a ``toml`` file.

    Args:
        config (dict): Configuration dictionary to save.
        file (str): path of ``toml`` file.
        options (optional): Can be used in the future if functionality
            need extendsion, like encoding type

    """
    with open(file, "w") as f:
        toml.dump(config, f)
    return


def yaml_dump(config: dict, file: str, options=None) -> None:
    """Write configuration dictionary (``config``) to a  ``yaml`` file.

    Args:
        config (dict): Configuration dictionary to save.
        file (str or path): name or path of ``yaml`` file.
        options (optional): Can be used in the future if functionality
            need extendsion, like encoding type

    """
    with open(file, "w") as f:
        yaml.dump(config, f)
    return


def json_dump(config: dict, file: str, options=None) -> None:
    """Write configuration dictionary (``config``) to a  ``json`` file.

    Args:
        config (dict): Configuration dictionary to save.
        file (str): path of ``toml`` file.
        options (optional): Can be used in the future if functionality
            need extendsion, like encoding type

    """
    with open(file, "w") as f:
        json.dump(config, f)
    return


load_functions = {".toml": toml_load, ".yml": yaml_load, ".json": json_load}
dump_functions = {".toml": toml_dump, ".yml": yaml_dump, ".json": json_dump}


## Probablyt don't want to use this.
def set_device_directory(Devices_directory: str):
    """Sets default devices directory in :py:class:`Device` to the input
       directory.

    Args:
        Devices_directory (str): New directory for the devices.
    """
    for line in fileinput.FileInput("./device/device.py", inplace=True):
        if line.startswith("Devices_directory"):
            print("Devices_directory = \'%s\'" % Devices_directory)  ## shhould be logging
        else:
            sys.stdout.write(line)
    return


def generate_measurement_config_from_file(config_list_file: str, out_file: str) -> None:
    """Generates measurement configuration from list of indiviual files, yielding
       a single file for the measurement.

        The `config_list_file` is a list of files of seperate configurations, e.g.,
        configuration for individual scans, devices etc.This function
        loads each individual file into a :py:class:`Measurement_Settings`
        object, then measurement configuration file. config_list_file will be a dict like
        file (e.g., json, yaml, toml) with structure:

        ``{'acquisition_devices': {'device_name': configuration_file_name, ...},
        'scan_devices': {'device_name': configuration_file_name, ...},
        'scan_collections': {'scan_name': configuration_file_name, ...}
        'averages': (int)}``

    Args:
        config_list_file (str): Name of list file to load.
        out_file (str): Name of file for saving the configuration of the generated
        Measurement_Settings.
    """
    acq_insts, scan_insts, scans = {}, {}, {}
    file_list = load_config(config_list_file)
    for inst_name, file in list(file_list["acquisition_devices"].items()):
        config = load_config(file)
        acq_insts.update({inst_name: config})
    for inst_name, file in list(file_list["scan_devices"].items()):
        config = load_config(file)
        scan_insts.update({inst_name: config})
    for scan_name, file in list(file_list["scan_collection"].items()):
        config = load_config(file)
        scans.update({scan_name: config})

    meas_config = {
        "acquisition_devices": acq_insts,
        "scan_devices": scan_insts,
        "scan_collection": scans,
        "averages": file_list["averages"],
    }

    dump_config(meas_config, out_file)
    return


def save_measurement_config(ms: bc.Measurement_Settings, out_file: str) -> None:
    """Generatres configuration dictioary from Measurement_Settings object
       and saves to specified file.

    Args:
        ms (Measurement_Settings): Measurement settings to save.
        out_file (str): Name of file to save.
    """
    meas_settings = bc.generate_measurement_config(ms)
    dump_config(meas_settings, out_file)
    return


def save_scan_collection():
    return


def save_device():
    return


def save_baecon_data(
    md: bc.Measurement_Data, file_name: str, format: str = ".zarr", options=None
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


def arg_parser():
    """Argument parser for command line interface.

        * ``-c``, ``--config_file``: Full measurement configuration file.
        * ``-g``, ``--gen_file``: File listing invididual config files for use
            with :py:func:`generate_measurement_config_from_file`.
        * ``-e``, ``--engine``: Measurement :py:mod:`engine` to use.
            **currently not implemented but there could a standard engine, OptBayes engine, and others**
        * ``-o``, ``--output``: Output file for saving data, or for saving a
            generated config file.

    Returns:
        dict: parsed arguements
    """
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-c",
        "--config_file",
        metavar="C",
        default="None",
        help="Measurement configuration file.",
    )

    parser.add_argument(
        "-g",
        "--gen_config",
        metavar="G",
        default="None",
        help="""Generate measurement configuration from file with list of
            configuration files. Use with `generate_measurement_configuration`
            tool.
        """,
    )

    parser.add_argument(
        "-e",
        "--engine",
        metavar="E",
        default="None",
        help="""Measurement engine to use.
        """,
    )

    parser.add_argument(
        "-o",
        "--output_file",
        metavar="E",
        default="None",
        help="""Output file to save to.
        """,
    )
    args = parser.parse_args()
    return args


def load_module_from_path(file_path: str):
    """Loads module from specified path.
       This is used to load specific :py:class:`Device`
       analysis file for :py:mod:`data`.

    Args:
        file_path (str): String or path to file of module.

    Returns:
        (python module): Module that was loaded
    """
    try:
        file_name = file_path.split("\\")[-1]

        to_import = os.path.splitext(file_name)[0]

        inst_path = os.path.abspath(file_path)
        spec = importlib.util.spec_from_file_location(to_import, inst_path)
        device_module = importlib.util.module_from_spec(spec)
        sys.modules[to_import] = device_module
        spec.loader.exec_module(device_module)
        return device_module
    except AttributeError as e:
        print(
            f"Tried to load a module from a path with: {file_path} but failed"
        )  ## shhould be logging
        return


# def baecon_install_directory():
#     pathlib.Path(__file__).parent.resolve()
#     return pathlib.Path(__file__).parent.resolve()
