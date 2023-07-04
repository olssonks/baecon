import sys
from datetime import datetime

from nicegui import ui

import baecon as bc
from baecon.GUI import gui_utils

## should be working with this, but if baecon cannot be found uncomment this
# sys.path.insert(0,"C:\\Users\\walsworth1\\Documents\\Jupyter_Notebooks\\baecon")


head_style = "color: #37474f; font-size: 200%; font-weight: 300"

date_prefix = gui_utils.holder(datetime.now().strftime("%Y_%m_%d"))
meas_number = gui_utils.holder("0")  ## should read data files in folder and update
alt_data_file_name = gui_utils.holder("")


def main(gui_fields: gui_utils.GUI_fields, meas_data: bc.Measurement_Data):
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


async def pick_file():
    result = await gui_utils.load_file(".")
    return result


async def pick_data_folder(gui_fields: gui_utils.GUI_fields):
    result = await gui_utils.load_file(".")
    gui_fields.data_folder = result
    return


async def save_as_button(
    alt_data_file_name: gui_utils.holder,
    meas_data: bc.Measurement_Data,
    date_prefix: str,
    meas_number: str,
):
    if alt_data_file_name.value in ["Alt. Data File Name", ""]:
        file = await pick_file()
        if file:
            alt_data_file_name.value = date_prefix.value + file
            gui_fields.data_file_format = "." + file.split(".")[-1]

    bc.utils.save_baecon_data(
        meas_data, alt_data_file_name.value, format=gui_fields.data_file_format
    )
    return


def update_file_name(gui_fields):
    gui_fields.data_file = (
        "_".join([date_prefix.value, meas_number.value, gui_fields.exp_name])
        + gui_fields.data_file_format
    )
    return


def update_file_format(new_format, gui_fields):
    gui_fields.data_file_format = new_format
    if "." in gui_fields.data_file:
        strip_format = ".".join(gui_fields.data_file.split(".")[:-1])
        gui_fields.data_file = strip_format + new_format
    else:
        gui_fields.data_file = gui_fields.data_file + new_format
    return


if __name__ in {"__main__", "__mp_main__"}:
    gui_fields = gui_utils.GUI_fields()
    meas_data = bc.Measurement_Data()
    main(gui_fields, meas_data)
    ui.run(port=8082)

## automatic file name generator
## "101_exp-name_date-time.zarr"
## "date-time_exp-name.zarr"
