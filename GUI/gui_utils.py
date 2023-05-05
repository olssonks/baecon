from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field

import sys
sys.path.insert(0,'C:\\Users\\walsworth1\\Documents\\Jupyter_Notebooks\\baecon')
import baecon as bc


from nicegui import ui
import plotly.graph_objects as go

@dataclass
class holder:
    value: any = ""
    def update(self, new_value):
        self.value = new_value
        

@dataclass
class Plot_Settings:
    method = ''
    properties = ''
    fig = ''
    plot = ''
    
@dataclass
class GUI_fields:
    """The GUI objects can be bound to these attributes, eliminating the need
       to pass values between differet cards.
    """
    plot: plot object
    exp_file: str/path
    scan_file: str/path
    instrument_file:dict
    data_file: str/path

@dataclass
class GUI_Measurement_Configuration:
    """Data structure for holding all the configuration needed to run measurement.
        The GUI uses the structure to keep track of parameters, then feeds it
        to baecon to run the measurement. This structure is used instead of 
        Measurement_Settings, as that structure holds actual devices which can 
        be tricky to update directly from value changes in the GUI.
        
    """    
    acquisition_devices: dict = field(default_factory=dict)
    scan_devices: dict = field(default_factory=dict)
    scan_collection: dict = field(default_factory=dict)
    averages: int = 1


class load_file(ui.dialog):

    def __init__(self, directory: str, *,
                 upper_limit: Optional[str] = ..., show_hidden_files: bool = False) -> None:
        """Local File Picker

        This is a simple file picker that allows you to select a file from the local filesystem where NiceGUI is running.

        :param directory: The directory to start in.
        :param upper_limit: The directory to stop at (None: no limit, default: same as the starting directory).
        :param multiple: Whether to allow multiple files to be selected.
        :param show_hidden_files: Whether to show hidden files.
        """
        super().__init__()

        self.path = Path(directory).expanduser()
        if upper_limit is None:
            self.upper_limit = None
        else:
            self.upper_limit = Path(directory if upper_limit == ... else upper_limit).expanduser()
        self.show_hidden_files = show_hidden_files

        with self, ui.card():
            self.grid = ui.aggrid({
                'columnDefs': [{'field': 'name', 'headerName': 'File'}],
                'rowSelection':'single',
            }, html_columns=[0]).classes('w-96').on('cellDoubleClicked', self.handle_double_click)
            with ui.row().classes('w-full justify-end'):
                ui.button('Cancel', on_click=self.close).props('outline')
                ui.button('Ok', on_click=self._handle_ok)
        self.update_grid()

    def update_grid(self) -> None:
        paths = list(self.path.glob('*'))
        if not self.show_hidden_files:
            paths = [p for p in paths if not p.name.startswith('.')]
        paths.sort(key=lambda p: p.name.lower())
        paths.sort(key=lambda p: not p.is_dir())

        self.grid.options['rowData'] = [
            {
                'name': f'📁 <strong>{p.name}</strong>' if p.is_dir() else p.name,
                'path': str(p),
            }
            for p in paths
        ]
        if self.upper_limit is None and self.path != self.path.parent or \
                self.upper_limit is not None and self.path != self.upper_limit:
            self.grid.options['rowData'].insert(0, {
                'name': '📁 <strong>..</strong>',
                'path': str(self.path.parent),
            })
        self.grid.update()

    async def handle_double_click(self, msg: dict) -> None:
        self.path = Path(msg['args']['data']['path'])
        if self.path.is_dir():
            self.update_grid()
        else:
            self.submit(str(self.path.resolve()))

    async def _handle_ok(self):
        rows = await ui.run_javascript(f'getElement({self.grid.id}).gridOptions.api.getSelectedRows()')
        full_path = str(Path(self.path.resolve(), rows[0]['name']))
        self.submit(full_path)
        

def available_devices():
    device_path = bc.Devices_directory
    contents = list(Path(device_path).glob('*'))
    devices = [content for content in contents if content.is_dir()]
    
    return
    
def load_gui_config(file_name)->GUI_Measurement_Configuration:
    loaded_config = bc.utils.load_config(file_name)
    gui_config = GUI_Measurement_Configuration()
    try:
        gui_config.acquisition_devices = loaded_config['acquisition_devices']
        gui_config.scan_devices = loaded_config['scan_devices']
        gui_config.scan_collection = loaded_config['scan_collection']
        gui_config.averages = loaded_config['averages']
        return gui_config
    except KeyError as e:
        msg = f'No {e} configuration found in {file_name}'
        return msg