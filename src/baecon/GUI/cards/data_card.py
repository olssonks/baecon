"""
.. note::
    This module has an example of how to add a logging decorator to all functions.
"""

# from datetime import datetime
import sys
from time import localtime, strftime

from nicegui import ui

import baecon as bc
from baecon.GUI import gui_utils
from baecon.utils.baecon_logger import add_logging_to_all

head_style = "color: #37474f; font-size: 200%; font-weight: 300"

## Ruff has issues with datetime module
date_prefix = gui_utils.Holder(strftime("%Y_%m_%d", localtime()))
meas_number = gui_utils.Holder("0")  ## should read data files in folder and update
alt_data_file_name = gui_utils.Holder("")

functions = [
    name
    for (name, thing) in locals().items()
    if (callable(thing) and thing.__module__ == __name__)
]


def main(gui_fields: gui_utils.GUI_fields, meas_data: bc.Measurement_Data) -> None:
    """Section of the GUI which controls data configuration.
       Configuration includes name, path, file type, and auto-save.

    Args:
        gui_fields (gui_utils.GUI_fields): GUI fields for the current measurement.
        meas_data (bc.Measurement_Data): Current measurement data object,
            which will be saved.
    """
    gui_fields.data_file = (
        "_".join([date_prefix.value, meas_number.value, gui_fields.exp_name])
        + gui_fields.data_file_format
    )
    with ui.column():
        with ui.row():
            ui.label("Data").style(head_style)
            ui.checkbox("Auto Save").bind_value(gui_fields, "data_auto_save")
        with ui.row():
            ui.label("File: ")
            ui.label().bind_text(gui_fields, "data_file")

    with ui.expansion("Save Info").classes("w-full"):
        with ui.row().classes("w-full no-wrap items-center"):
            ui.button("Pick:", on_click=pick_data_folder).classes("text-left")
            ui.input(placeholder="Data Location").bind_value(gui_fields, "data_folder")

        with ui.column():
            with ui.row():
                ui.label("Date Prefix: ")
                ui.label().bind_text(date_prefix, "value")
                ui.label("Meas. Number: ")
                ui.label().bind_text(meas_number, "value")

            with ui.row().classes("w-full no-wrap items-center"):
                ui.input(placeholder="Alt. Data File Name").classes("w-full").bind_value(
                    alt_data_file_name, "value"
                )

        with ui.row().classes("w-full no-wrap items-center"):
            ui.label("Data Format:")
            ui.radio(
                [".zarr", ".nc", ".csv"],
                value=".zarr",
                on_change=lambda e: update_file_format(e.value, gui_fields),
            ).props("inline").bind_value(gui_fields, "data_file_format")

        with ui.row():
            ui.button("Save")
            ui.button(
                "Save as:",
                on_click=save_as_button(
                    alt_data_file_name, meas_data, date_prefix, meas_number
                ),
            ).classes("text-left")

        with ui.row().classes("w-full no-wrap items-center"):
            ui.input("analysis method").classes("w-full")
            ui.button("Load")

    return


async def pick_data_folder(gui_fields: gui_utils.GUI_fields) -> None:
    """Pick the directory to load/save data.
       The ``data_folder`` attribute in the GUI fields is set to the chosen directory.

    Args:
        gui_fields (gui_utils.GUI_fields): GUI fields for the current measurement.
    """
    result = await gui_utils.pick_file(gui_utils.DATA_DIRECTORY)
    gui_fields.data_folder = result
    return


async def save_as_button(
    alt_data_file_name: gui_utils.Holder,
    meas_data: bc.Measurement_Data,
    date_prefix: str,
    meas_number: str,
) -> None:
    """Save data to a different file name. Called when clicking the "Save as" button.

    Args:
        alt_data_file_name (gui_utils.Holder): Holds the new name for the data file.
        meas_data (bc.Measurement_Data): Data from the measurement.
        date_prefix (str): File type to save data.
        meas_number (str): Nth+1 measurement for when N measurements in the current directory
    """
    if alt_data_file_name.value in ["Alt. Data File Name", ""]:
        file = await gui_utils.pick_file()
        if file:
            alt_data_file_name.value = date_prefix.value + file
            gui_fields.data_file_format = "." + file.split(".")[-1]

    bc.data.save_baecon_data(
        meas_data, alt_data_file_name.value, format=gui_fields.data_file_format
    )
    return


def update_file_name(gui_fields: gui_utils.GUI_fields) -> None:
    """Updates the data file name.
       This is called in the experiment card, such that the data file name
       is updated with current experiment name.

    Args:
        gui_fields (_type_): GUI fields for the current measurement.
    """
    gui_fields.data_file = (
        "_".join([date_prefix.value, meas_number.value, gui_fields.exp_name])
        + gui_fields.data_file_format
    )
    return


def update_file_format(new_format: str, gui_fields: gui_utils.GUI_fields) -> None:
    """Updates the data file format based on a change in the GUI.
       Changes the GUI fields for the data file format and the data file path.

    Args:
        new_format (str): New format for the data.
        gui_fields (gui_utils.GUI_fields): GUI fields for the current measurement.
    """
    gui_fields.data_file_format = new_format
    if "." in gui_fields.data_file:
        strip_format = ".".join(gui_fields.data_file.split(".")[:-1])
        gui_fields.data_file = strip_format + new_format
    else:
        gui_fields.data_file = gui_fields.data_file + new_format
    return


add_logging_to_all(sys.modules[__name__])

if __name__ in {"__main__", "__mp_main__"}:
    gui_fields = gui_utils.GUI_fields()
    meas_data = bc.Measurement_Data()
    main(gui_fields, meas_data)
    ui.run(port=8082)
