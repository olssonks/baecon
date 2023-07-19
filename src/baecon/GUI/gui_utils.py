from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from nicegui import ui

import baecon as bc


GUI_UTILS_DIRECTORY = Path(__file__).parent.resolve()

DATA_DIRECTORY = Path(__file__).parent.parent.resolve() / "Configuration_Files/Data"

EXPERIMENT_DIRECTORY = (
    Path(__file__).parent.parent.resolve() / "Configuration_Files/Experiments"
)

ENGINE_DIRECTORY = Path(__file__).parent.parent.resolve() / "Configuration_Files/Engines"

SCANS_DIRECTORY = Path(__file__).parent.parent.resolve() / "Configuration_Files/Scans"

GUI_PORT = 8666


@dataclass
class Holder:
    """Used for passing values between functions and GUI inputs.
    `NiceGUI` uses `lambda` and `async` functions which can which don't always
    work right for methods with arguments. This :py:class:`Holder` helps
    circumvent this issue, letting methods be defined without arguments.

    An alternative to this methods is to use :py:obj:`partial` from :py:mod:`functools`.
    """

    value: any = ""

    def update(self, new_value):
        self.value = new_value


GUI_CARD_HOLDER = Holder()


@dataclass
class Plot_Settings:
    """Currently not used for anything. Could hold plot formatting/setting.

    These plot maybe passed to :py:mod:`engine_card` and :py:mod:`data_card`.

    """

    method = ""
    properties = ""
    fig = ""
    plot = ""


## Might need to use this to make sure fields in the cards get updated
@dataclass
class All_GUI_Elements:
    """
    Holds list of all elements (i.e. cards) in the GUI.
    Used to update all the fields when loading experiments.
    """

    elements: list = field(default_factory=list)


@dataclass
class GUI_fields:
    """Object holding all the fields in :py:func:`baecon.GUI.baecon_GUI.main`.

    These fields mostly correspond to file names and paths for various :py:mod:`baecon`
    objects, e.g. scan device file name or data file name an path.

    .. note:: The dictionary containing the plot data is held here. This is not the full
         data, but a slightly reduced data set which looks good for plotting. The format
         of this data is defined by :py:mod:`baecon.GUI.cards.plot_card`

    .. todo:: Should data_card be object defining plot data format?? Engine might be
         better for that.

    """

    plot_data: dict = field(default_factory=dict)  ## {'name': (x_data, y_data)}
    scan_dev_files: dict = field(default_factory=dict)  ## {device name: file}
    acq_dev_files: dict = field(default_factory=dict)  ## {device name: file}
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


class load_file(ui.dialog):
    def __init__(
        self,
        directory: str,
        *,
        upper_limit: Optional[str] = ...,
        show_hidden_files: bool = False,
    ) -> None:
        """Local File Picker

        This is a simple file picker that allows you to select a file from the local file
        system where NiceGUI is running.

        This module has been adapted from the :py:mod:`nicegui` example "local_file_picker'.
        Args:
            directory (str):The directory to start in.
            upper_limit (Optional[str], optional): The directory to stop at
                (None: no limit, default: same as the starting directory). Defaults to ....
            show_hidden_files (bool, optional): Whether to show hidden files.
                Defaults to False.
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
            ## [0] is the parent path to ./baecon/src/baecon
            path_cutoff = [
                path.resolve().__str__()
                for path in self.path.parents
                if "baecon" not in path.resolve().__str__()
            ][0]
            ui.label(f"Directory: {self.path.relative_to(path_cutoff)}")
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
            if not self.file_name.value == "":  # noqa: PLC1901
                full_path = str(Path(self.path.resolve(), self.file_name.value))
            else:
                full_path = str(Path(self.path.resolve(), rows[0]["name"]))
            self.submit(full_path)
        except IndexError:
            ## Index error happend is you pres the OK button without selecing a file.
            pass
        return


async def pick_file(directory) -> str:
    """Opens a GUI window to pick a file.

    Returns:
        str: String/path of the file location.
    """
    result = await load_file(directory)
    return result


def available_devices() -> list[str]:
    """Generates a list of devices that are available in the list directorty

    Returns:
        list[str]: List of devices available in the Devices directory.
    """
    device_path = bc.DEVICES_DIRECTORY
    contents = list(Path(device_path).glob("*"))
    devices = [content for content in contents if content.is_dir()]
    return devices


def name_from_path(file_path: str) -> str:
    """Strips path of all directories, returning just the file name and type.

    Args:
        file_path (str): Path to file of interest.

    Returns:
        str: File name, including file type.
    """
    try:
        file_name = file_path.split("\\")[-1]
        return file_name
    except AttributeError:
        ## logging here
        return


def to_gui_fields_config(gui_fields: GUI_fields) -> dict:
    """Generates a dictionary from :py:class:`GUI_fields <baecon.GUI.gui_utils.GUI_fields>`.
       This dictionary then defines an experiment.

       Also, the ``plot_data`` field is set to an empty dictionary. We
       don't want to save plot data in this configuration dictionary, the data
       saving is handled by :py:mod:`Data Card <baecon.GUI.cards.data_card>`.

    Args:
        gui_fields (GUI_fields): GUI_fields object for the current GUI configuration.

    Returns:
        dict: Dictionary of with the fields info from the GUI_fields object.
    """
    config = gui_fields.__dict__
    config.update({"plot_data": {}})  ## Don't want to save data in config
    return config


def from_gui_fields_config(config: dict, gui_fields: GUI_fields) -> None:
    """Fills a :py:class:`GUI_fields <baecon.GUI.gui_utils.GUI_fields>` from dictionary.

    Args:
        config (dict): Dictionary with configuration information.
        gui_fields (GUI_fields): Object to put dictionary info into.
    """
    fields = config.get("GUI_Fields")
    for attr in fields:
        if hasattr(gui_fields, attr):
            gui_fields.__setattr__(attr, fields[attr])
    return


def set_gui_cards(card_dict):
    GUI_CARD_HOLDER.update(card_dict)
    return


def update_everything(gui_fields: GUI_fields, meas_settings: bc.Measurement_Settings):
    """Updates all the elements of the GUI.
       For certain GUI elements not bound to one of the :py:class:`GUI_fields <baecon.GUI.gui_utils.GUI_fields>`

    Args:
        gui_fields (GUI_fields): _description_
        meas_settings (bc.Measurement_Settings): _description_
    """
    for _, card_info in GUI_CARD_HOLDER.value.items():
        card_info['function'](*card_info['args'], gui_fields, meas_settings)
    return


def find_gui_element(element, element_tag):
    element = search_element_parents(element, element_tag)
    if element is None:
        ## place holder for search children elements
        pass
    return element


# def search_element_parents(element, element_tag):
#     test_parent_slot = element.parent_slot
#     while not (test_parent_slot is None or test_parent_slot.parent.tag == element_tag):
#         test_parent_slot = test_parent_slot.parent.parent_slot
#     return test_parent_slot


def search_element_parents(element: ui.element, element_tag: str):
    """Find parent to `element` with the tag `element_tag`.

    The :py:attr:`parent`, which has a :py:attr:`tag`, is held in :py:attr:`parent_slot`
     of `element`.


    Args:
        element (_type_): _description_
        element_tag (_type_): _description_

    Returns:
        _type_: _description_
    """
    test_parent = element.parent_slot.parent
    while not (test_parent is None or test_parent.tag == element_tag):
        test_parent = test_parent.parent_slot.parent
    return test_parent

    ## this is needs to be more complex as elements can have multiple children


def search_element_children(element, element_tag):
    test_parent_slot = element.parent_slot
    while not (test_parent_slot is None or test_parent_slot.parent.tag == element_tag):
        test_parent_slot = test_parent_slot.parent.parent_slot
    return t


# def find_gui_element(element, element_tag):
#     found_element = None
#     test_parent_slot = element.parent_slot
#     while test_parent_slot is not None:
#         if test_parent_slot.parent.tag == element_tag:
#             found_element = test_parent_slot.parent
#             break
#         else:
#             test_parent_slot = test_parent.parent_slot
#     if not found_element:

#     return test_parent


if __name__ in {"__main__", "__mp_main__"}:
    ui.run(port=8082)
