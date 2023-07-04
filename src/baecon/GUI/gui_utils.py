import asyncio
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import plotly.graph_objects as go
from nicegui import ui

import baecon as bc

## should be working with this, but if baecon cannot be found uncomment this
# sys.path.insert(0,"C:\\Users\\walsworth1\\Documents\\Jupyter_Notebooks\\baecon")


@dataclass
class holder:
    """Used for passing values between functions and GUI inputs.
    `NiceGUI` uses `lambda` and `async` functions which can which don't always
    work right for methods with arguments. This :py:class:`holder` helps
    circumvent this issue, letting methods be defined without arguments.

    An alternative to this methods is to use :py:obj:`partial` from :py:mod:`functools`.
    """

    value: any = ""

    def update(self, new_value):
        self.value = new_value


@dataclass
class Plot_Settings:
    method = ""
    properties = ""
    fig = ""
    plot = ""


@dataclass
class GUI_fields:
    """The GUI objects can be bound to these attributes, allowing passing
    between cards.
    """

    plot_data: dict = field(default_factory=dict)  ## {'name': (x_data, y_data)}
    exp_name: str = ""
    exp_file: str = ""
    engine_name: str = ""
    engine_file: str = ""
    scan_file: str = ""
    averages: int = 1
    data_auto_save: bool = ""
    data_folder: str = ""
    data_file: str = ""
    data_file_format: str = ""
    data_analysis: str = ""  ### Probably a seperate Window
    plot_active: bool = False
    abort_measurement: bool = False


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
    def __init__(
        self,
        directory: str,
        *,
        upper_limit: Optional[str] = ...,
        show_hidden_files: bool = False,
    ) -> None:
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
            self.upper_limit = Path(
                directory if upper_limit == ... else upper_limit
            ).expanduser()
        self.show_hidden_files = show_hidden_files

        with self, ui.card():
            self.grid = (
                ui.aggrid(
                    {
                        "columnDefs": [{"field": "name", "headerName": "File"}],
                        "rowSelection": "single",
                    },
                    html_columns=[0],
                )
                .classes("w-96")
                .on("cellDoubleClicked", self.handle_double_click)
            )
            with ui.row().classes("w-full no-wrap items-end"):
                self.file_name = ui.input(placeholder="Choose File Name").classes("w-full")
                ui.button("Cancel", on_click=self.close).props("outline")
                ui.button("Ok", on_click=self._handle_ok)
        self.update_grid()

    def update_grid(self) -> None:
        paths = list(self.path.glob("*"))
        if not self.show_hidden_files:
            paths = [p for p in paths if not p.name.startswith(".")]
        paths.sort(key=lambda p: p.name.lower())
        paths.sort(key=lambda p: not p.is_dir())

        self.grid.options["rowData"] = [
            {
                "name": f"📁 <strong>{p.name}</strong>" if p.is_dir() else p.name,
                "path": str(p),
            }
            for p in paths
        ]
        if (
            self.upper_limit is None
            and self.path != self.path.parent
            or self.upper_limit is not None
            and self.path != self.upper_limit
        ):
            self.grid.options["rowData"].insert(
                0,
                {
                    "name": "📁 <strong>..</strong>",
                    "path": str(self.path.parent),
                },
            )
        self.grid.update()
        return

    async def handle_double_click(self, msg: dict) -> None:
        self.path = Path(msg["args"]["data"]["path"])
        if self.path.is_dir():
            self.update_grid()
        else:
            self.submit(str(self.path.resolve()))
        return

    async def _handle_ok(self):
        rows = await ui.run_javascript(
            f"getElement({self.grid.id}).gridOptions.api.getSelectedRows()"
        )
        try:
            if not self.file_name.value == "":
                full_path = str(Path(self.path.resolve(), self.file_name.value))
            else:
                full_path = str(Path(self.path.resolve(), rows[0]["name"]))
            self.submit(full_path)
        except IndexError:
            ## Index error happend is you pres the OK button without selecing a file.
            pass
        return


async def pick_file():
    result = await load_file(".")
    return result


def available_devices():
    device_path = bc.Devices_directory
    contents = list(Path(device_path).glob("*"))
    devices = [content for content in contents if content.is_dir()]
    return devices


def name_from_path(file_path):
    try:
        file_name = file_path.split("\\")[-1]
        return file_name
    except AttributeError:
        ## logging here
        return


def to_gui_fields_config(gui_fields:GUI_fields):
    config = gui_fields.__dict__
    config.update({"plot_data":{}}) ## Don't want to save data in config
    return config

def from_gui_fields_config(config:dict, gui_fields:GUI_fields):
    fields = config.get("GUI_Fields")
    for attr in fields:
        if hasattr(gui_fields, attr):
            gui_fields.__setattr__(attr, fields[attr])
    return


