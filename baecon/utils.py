import baecon as bc

import toml, yaml, json, os #for config file operations

import sys, fileinput, argparse

## for file_chooser
from pathlib import Path
from typing import Optional

#from nicegui import ui


def load_config(file:str, options = None)->dict:
    """Loads configuration file `file` and returns dictionary of configurations.
        File type may be `.toml`, `.yaml`, or `.json`.

    Args:
        file (str): Configuration file to load.
        options (optional): Can be used in the future if functionality 
        need extendsion, like encoding type.

    Returns:
        dict: Configuration dictionary
    """    
    file = os.path.normpath(file)
    _, file_exetension = os.path.splitext(file)
    configuration = load_functions[file_exetension](file, options)
    return configuration

def dump_config(config:dict, file:str, options = None)->None:
    """Saves configuration dictionary into `file`.
        File type may be `.toml`, `.yaml`, or `.json`.

    Args:
        config (dict): Configuration dictionary to load
        file (str): Configuration file to load.
        options (optional): Can be used in the future if functionality 
        need extendsion, like encoding type.

    Returns:
        dict: Configuration dictionary
    """    

    file = os.path.normpath(file)
    _, file_exetension = os.path.splitext(file)
    dump_functions[file_exetension](config, file, options)
    return
    
def toml_load(file:str, options = None)->dict:
    """Reads `toml` file and returns `dict`. 

    Args:
        file (str): path of `toml` file.
        options (optional): Can be used in the future if functionality 
        need extendsion, like encoding type.

    Returns:
        dict: Dictionary of `toml` file contents.
    """
    with open(file,'r') as f:
        loaded_toml = toml.load(f)
    return loaded_toml 


def yaml_load(file:str, options = None)->dict:
    """Reads `yaml` file and returns `dict`. 

    Args:
        file (str): path of `yaml` file.
        options (optional): Can be used in the future if functionality 
        need extendsion, like encoding type

    Returns:
        dict: Dictionary of `yaml` file contents.
    """
    with open(file,'r') as f:
        loaded_yaml = yaml.safe_load(f)
    return loaded_yaml
    
    
def json_load(file:str, options = None)->dict:
    """Reads `json` file and returns `dict`. 

    Args:
        file (str): path of `json` file.
        options (optional): Can be used in the future if functionality 
        need extendsion, like encoding type

    Returns:
        dict: Dictionary of `json` file contents.
    """
    with open(file,'r') as f:
        loaded_json = json.loads(f)
    return loaded_json


def toml_dump(config:dict, file:str, options = None)->None:
    """Write configuration dictionary (`config`) to a  `toml` file.
    Args:
        config (dict): Configuration dictionary to save.
        file (str): path of `toml` file.
        options (optional): Can be used in the future if functionality 
        need extendsion, like encoding type

    Returns:
        None
    """    
    with open(file, 'w') as f:
        toml.dump(config, f)
    return
    
    
def yaml_dump(config:dict, file:str, options = None)->None:
    """Write configuration dictionary (`config`) to a  `yaml` file.
    Args:
        config (dict): Configuration dictionary to save.
        file (str or path): name or path of `yaml` file.
        options (optional): Can be used in the future if functionality 
        need extendsion, like encoding type

    Returns:
        None
    """
    with open(file, 'w') as f:
        yaml.dump(config, f)
    return
    
    
def json_dump(config:dict, file:str, options = None)->None:
    """Write configuration dictionary (`config`) to a  `json` file.
    Args:
        config (dict): Configuration dictionary to save.
        file (str): path of `toml` file.
        options (optional): Can be used in the future if functionality 
        need extendsion, like encoding type

    Returns:
        None
    """
    with open(file, 'w') as f:
        json.dump(config, f)
    return

load_functions = {'.toml':toml_load, '.yaml':yaml_load, '.json':json_load}
dump_functions = {'.toml':toml_dump, '.yaml':yaml_dump, '.json':json_dump}


def set_instrument_directory(Instruments_directory:str):
    """Sets default instruments directory in `Instruments` to the input
        directory.

    Args:
        Instruments_irectory (str): Directory of Instruments
    """
    for line in fileinput.FileInput('instrument.py',inplace=1):
        if line.startswith('Instruments_directory'):
            print('Instruments_directory = \'%s\'' % Instruments_directory)
        else:
            sys.stdout.write(line)
    return


def generate_measurement_config_from_file(config_list_file:str, out_file:str)->None:
    """Generates a Measurement_Settings object from file containing list of 
        individual configuration files, then saves Measurement_Settings to a 
        measurement configuration file. config_list_file will be a dict like 
        file (e.g., json, yaml, toml) with structure:
        {'acquisition_instruments': {'instrument_name': configuration_file_name, ...},
        'scan_instruments': {'instrument_name': configuration_file_name, ...}, 
        'scan_collections': {'scan_name': configuration_file_name, ...}
        'averages': (int)
        }
    Args:
        config_list_file (str): Name of file to load.
        out_file (str): Name of file to save configuration of the generated 
        Measurement_Settings
    """    
    ms = bc.Measurement_Settings()
    file_list = load_config(config_list_file)
    for file in list(file_list['acquisition_instruments'].values):
        bc.add_instrument(file, ms.acquisition_instruments)
    for file in list(file_list['scan_instruments'].values):
        bc.add_instrument(file, ms.scan_instruments)
    for file in list(file_list['scan_collection'].values):
        bc.add_scan(file, ms.scan_collection)
    ms.averages = file_list['averages']
    bc.save_measurement_config(ms, out_file)
    return

def command_parser():
    parser = argparse.ArgumentParser()
    
    parser.add_argument('-c', '--config_file',
        metavar='C',
        default='None',
        help='Measurement configuration file'
        )
    
    parser.add_argument('-g', '--gen_config',
        metavar='G',
        default='None',
        help='Generate measurement configuration from file with list of configuration files.'
        )
    return

# class local_file_picker(ui.dialog):

#     def __init__(self, directory: str, *,
#                  upper_limit: Optional[str] = ..., show_hidden_files: bool = False) -> None:
#         """Local File Picker

#         This is a simple file picker that allows you to select a file from the local filesystem where NiceGUI is running.

#         :param directory: The directory to start in.
#         :param upper_limit: The directory to stop at (None: no limit, default: same as the starting directory).
#         :param show_hidden_files: Whether to show hidden files.
#         """
#         super().__init__()

#         self.path = Path(directory).expanduser()
#         if upper_limit is None:
#             self.upper_limit = None
#         else:
#             self.upper_limit = Path(directory if upper_limit == ... else upper_limit).expanduser()
#         self.show_hidden_files = show_hidden_files

#         with self, ui.card():
#             self.grid = ui.aggrid({
#                 'columnDefs': [{'field': 'name', 'headerName': 'File'}],
#                 'rowSelection': 'single',
#             }, html_columns=[0]).classes('w-96').on('cellDoubleClicked', self.handle_double_click)
#             with ui.row().classes('w-full justify-end'):
#                 ui.button('Cancel', on_click=self.close).props('outline')
#                 ui.button('Ok', on_click=self._handle_ok)
#         self.update_grid()

#     def update_grid(self) -> None:
#         paths = list(self.path.glob('*'))
#         if not self.show_hidden_files:
#             paths = [p for p in paths if not p.name.startswith('.')]
#         paths.sort(key=lambda p: p.name.lower())
#         paths.sort(key=lambda p: not p.is_dir())

#         self.grid.options['rowData'] = [
#             {
#                 'name': f'📁 <strong>{p.name}</strong>' if p.is_dir() else p.name,
#                 'path': str(p),
#             }
#             for p in paths
#         ]
#         if self.upper_limit is None and self.path != self.path.parent or \
#                 self.upper_limit is not None and self.path != self.upper_limit:
#             self.grid.options['rowData'].insert(0, {
#                 'name': '📁 <strong>..</strong>',
#                 'path': str(self.path.parent),
#             })
#         self.grid.update()

#     async def handle_double_click(self, msg: dict) -> None:
#         self.path = Path(msg['args']['data']['path'])
#         if self.path.is_dir():
#             self.update_grid()
#         else:
#             self.submit([str(self.path.resolve())])

#     async def _handle_ok(self):
#         rows = await ui.run_javascript(f'getElement({self.grid.id}).gridOptions.api.getSelectedRows()')
#         full_path = [str(Path(self.path.resolve(), rows[0]['name']))]
#         self.submit(full_path)