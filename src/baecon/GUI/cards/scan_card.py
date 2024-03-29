from functools import partial

from nicegui import ui

import baecon as bc
from baecon.GUI import gui_utils

scan_settings = bc.define_scan_settings()

## name of the device is displayed intstead of device type
scan_headers = {
    "name": "Device",
    "parameter": "Parameter",
    "min": "Min.",
    "max": "Max.",
    "points": "Points",
    "repetitions": "Repetitions",
    "scale": "Scale",
    "randomize": "Randomize",
    "note": "Note",
}

header_widths = [300, 300, 150, 150, 150, 300, 300, 300, 300]
card_width = "1000px"


gui_config_holder = gui_utils.Holder()

file_holder = gui_utils.Holder()
scan_name = gui_utils.Holder("pick a file")

scan_table_holder = gui_utils.Holder()
table_args_holder = gui_utils.Holder()

head_style = "color: #37474f; font-size: 200%; font-weight: 300"


def main(
    gui_fields: gui_utils.GUI_fields,
    meas_settings: bc.Measurement_Settings,
    meas_data: bc.Measurement_Data,
):
    with ui.column().classes("w-full"):
        ui.label("Measurment Scans").style(head_style)
        save_load(gui_fields, meas_settings)

        with ui.row().style(f"width: {card_width}").classes("no-wrap"):
            primary_buttons(gui_fields, meas_settings)
            table_args_holder.value = scan_table_args(gui_fields, meas_settings)
            scan_table_holder.value = ui.aggrid({"rowSelection": "single"}).classes("w-full")
            update_table()

    return update_scan_card, ()  ## empty tuple used for extra args ??


def update_scan_card(
    gui_fields: gui_utils.GUI_fields, meas_settings: bc.Measurement_Settings
):
    for scan_name, collection in meas_settings.scan_collection.items():
        scan_from_settings({scan_name: collection['settings']}, gui_fields, meas_settings)
    return


def save_load(gui_fields: gui_utils.GUI_fields, meas_settings: bc.Measurement_Settings):
    """Section of the GUI where the name of the scan, file name, save, and load
    buttons are derined.

    Args:
        gui_fields (gui_utils.GUI_fields): _description_
        scan_collection (dict): _description_
    """

    with ui.row().style(f"width: {card_width}").classes("no-wrap items-center"):
        ui.input(label="Scan Collection Name", placeholder="pick file").bind_value(
            gui_fields, "scan_file"
        ).classes("w-full relative-right text-right")
        ui.button("Save", on_click=partial(save_collection, *(gui_fields, meas_settings)))
        ui.button(
            "Save as", on_click=partial(save_as_collection, *(gui_fields, meas_settings))
        )
        ui.button("Load", on_click=partial(load_collection, *(gui_fields, meas_settings)))
    return


async def save_collection(
    gui_fields: gui_utils.GUI_fields, meas_settings: bc.Measurement_Settings
):
    """Saves scan collection to config file.

    Args:
        gui_fields (gui_utils.GUI_fields): _description_
    """

    file = gui_fields.scan_file
    if file:
        gui_fields.scan_file = file
        scan_name.value = name_from_file(file)
        ## settings is a dict of the settings defining the scan, this dict is saved
        scan_dict = {}
        for key in meas_settings.scan_collection.keys():
            scan_dict.update({key: meas_settings.scan_collection[key]["settings"]})
        bc.utils.dump_config(scan_dict, gui_fields.scan_file)
    return


async def save_as_collection(
    gui_fields: gui_utils.GUI_fields, meas_settings: bc.Measurement_Settings
):
    """Saves scan collection to config file.

    Args:
        gui_fields (gui_utils.GUI_fields): _description_
    """

    file = await gui_utils.pick_file(gui_utils.SCANS_DIRECTORY)
    if file:
        gui_fields.scan_file = file
        scan_name.value = name_from_file(file)
        ## settings is a dict of the settings defining the scan, this dict is saved
        scan_dict = {}
        for key in meas_settings.scan_collection.keys():
            scan_dict.update({key: meas_settings.scan_collection[key]["settings"]})
        bc.utils.dump_config(scan_dict, gui_fields.scan_file)
    return


async def load_collection(
    gui_fields: gui_utils.GUI_fields, meas_settings: bc.Measurement_Settings
):
    """Opens dialog to pick scan configuration file and adds to current scan.

    Args:
        gui_fields (gui_utils.GUI_fields): _description_
        meas_settings (bc.Measurement_Settings): _description_
    """
    file = await gui_utils.pick_file(gui_utils.SCANS_DIRECTORY)
    if file:
        gui_fields.scan_file = file
        scan_name.value = name_from_file(file)
        scan_config = bc.utils.load_config(gui_fields.scan_file)
        scan_from_settings(scan_config, gui_fields, meas_settings)
    return


def name_from_file(file: str):
    name = file.split("\\")[-1]
    return name


def primary_buttons(
    gui_fields: gui_utils.GUI_fields, meas_settings: bc.Measurement_Settings
):
    """Buttons for calling the `add_scan_dialog` and `remove-device` methods.

    Args:
        gui_fields (gui_utils.GUI_fields): _description_
        meas_settings (bc.Measurement_Settings): _description_
    """
    with ui.column():
        avgs = ui.number("Averages").bind_value(gui_fields, "averages")
        avgs.on("update:model-value", avgs.update)
        ## without lambda the add_scan_dialog opens on start up (don't know why ???)
        ui.button(
            "Add", on_click=lambda: add_scan_dialog(gui_fields, meas_settings)
        ).classes("w-full")
        ## don't use lambda here, breaks async of remove device
        ui.button(
            "Remove", on_click=partial(remove_scan, *(gui_fields, meas_settings))
        ).classes("w-full")
    return


def update_table():
    """Updates the can scan table.
    The scan table, a `ui.aggrid` object, is held in the global variable
    `scan_table_holder`. Columns and rows are accessed through the `options`
    attribute of `ui.aggrid`.
    """
    scan_table_holder.value.options["columnDefs"] = table_args_holder.value["columnDefs"]
    scan_table_holder.value.options["rowData"] = table_args_holder.value["rowData"]
    scan_table_holder.value.update()
    return


def scan_table_args(
    gui_fields: gui_utils.GUI_fields, meas_settings: bc.Measurement_Settings
) -> dict:
    """Create a dictionary from `bc.Measurement_Settings.scan_collection` to
    populate the scan table.

    Args:
        gui_fields (gui_utils.GUI_fields): _description_
        meas_settings (bc.Measurement_Settings): _description_

    Returns:
        dict: Dictionary with column and row information for he scan table.
    """
    scans = meas_settings.scan_collection
    column_defs = []
    row_data = []

    for idx, key in enumerate(scan_headers.keys()):
        column_defs.append(
            {
                "headerName": f"{scan_headers[key]}",
                "field": f"{key}",
                "editable": True,
                "resizable": True,
                "suppressSizeToFit": False,
                "initialWidth": header_widths[idx],
            }
        )
    for key in scans.keys():
        row = {}
        settings = scans[key]["settings"]
        for setting in scan_headers.keys():
            row.update({f"{setting}": settings[setting]})
        row_data.append(row)

    return {"columnDefs": column_defs, "rowData": row_data}


def add_scan_dialog(
    gui_fields: gui_utils.GUI_fields, meas_settings: bc.Measurement_Settings
):
    """Pop-up dialog to input scan settings for a new scan.

    Args:
        gui_config (gui_utils.GUI_Measurement_Configuration): _description_
        meas_settings (bc.Measurement_Settings): _description_
    """
    scan_settings_holder = gui_utils.Holder()

    def update_scan_collection():
        """Adds the fields from the scan settings dialog to the `bc.Measurement_Settings`
        and the scan table.

        """
        new_settings = scan_settings_holder.value
        new_scan = {f'{new_settings["name"]}-{new_settings["parameter"]}': new_settings}
        # scan_key = f'{new_settings["name"]}-{new_settings["parameter"]}'
        # meas_settings.scan_collection.update({scan_key: new_settings})
        scan_from_settings(new_scan, gui_fields, meas_settings)
        table_args_holder.value = scan_table_args(gui_fields, meas_settings)
        return

    with ui.dialog() as dialog, ui.card():
        with ui.column().classes("w-full"):
            ui.label("Scan Settings").classes("text-h3")
            scan_settings_holder.value = choose_device_and_paramters(meas_settings)
            choose_settings(scan_settings_holder.value)
            make_button = ui.button("Make Scan", on_click=update_scan_collection)
            make_button.on("click", dialog.close)
            make_button.on("click", update_table)
    dialog.open()
    return


def scan_from_settings(
    scan_config: dict,
    gui_fields: gui_utils.GUI_fields,
    meas_settings: bc.Measurement_Settings,
):
    """Creates a `scan_collection` from a configuration dictionary and adds it
    `meas_settings.scan_collection`.

    Args:
        scan_config (dict): Configuration of the scan, comes the from
            `add_scan_dialog` or a loaded file.
        gui_fields (gui_utils.GUI_fields): _description_
        meas_settings (bc.Measurement_Settings): _description_
    """
    for _scan_idx, scan_key in enumerate(scan_config.keys()):
        device_name = scan_config[scan_key]["name"]
        if device_name not in meas_settings.scan_devices:
            print(f"Specified device {device_name} not listed in Scan Devices.")
        else:
            scan_device = meas_settings.scan_devices[device_name]
            bc.add_scan(scan_config[scan_key], scan_device, meas_settings)
    table_args_holder.value = scan_table_args(gui_fields, meas_settings)
    update_table()
    return


def choose_device_and_paramters(meas_settings: bc.Measurement_Settings) -> dict:
    selected_settings = scan_settings.copy()
    """Inputs for choosing the device and parameter for the scan.
    When the device is selected, the parameter input will read the `parameters`
    attribute of the device, and populate the parameter input with the `parameters`.

    Returns:
        dict: Diction of scan settings.
    """
    ui.select(
        list(meas_settings.scan_devices.keys()),
        label="Device Name",
        on_change=lambda e: (
            selected_settings.update({"name": e.value}),
            selected_settings.update(
                {"device": meas_settings.scan_devices[e.value].configuration["device"]}
            ),
            param_update(e.value),
        ),
    ).classes("w-full")
    param_select = ui.select(
        ["choose device"],
        label="parameter",
        on_change=lambda e: selected_settings.update({"parameter": e.value}),
    ).classes("w-full")

    def param_update(selected_device):
        ## adds the parameters of the device to the list UI object param_select
        param_select.options = list(
            meas_settings.scan_devices[selected_device].parameters.keys()
        )
        param_select.update()

    return selected_settings


def choose_settings(selected_settings: dict) -> dict:
    """Choose the values for the scan.
    The input fields are bound to the values in the `selected_settings dict`.
    The GUI input fields are given labels based on the keys in `selected_settings`;
    this is necessary to properly bind the values.
    Args:
        selected_settings (dict): Dictionary of scan settings to add.

    Returns:
        dict: Scan settings to add.
    """
    remaining_keys = [
        key
        for key in list(scan_settings.keys())
        if not (key == "name" or key == "parameter" or key == "device")
    ]
    for scan_key in remaining_keys:
        with ui.row().classes("w-full"):
            if (
                isinstance(scan_settings[scan_key], str)
                and not scan_key == "scale"
                and not scan_key == "randomize"
            ):
                ui.input(
                    scan_key,
                    value=scan_settings[scan_key],
                    on_change=lambda e: selected_settings.update(
                        {e.sender._props["label"]: e.value}
                    ),
                ).classes("w-full")
            elif scan_key == "points":
                get_points(selected_settings, scan_key)
            elif scan_key == "scale":
                ui.select(
                    ["linear", "log", "custom", "constant"],
                    label="scale",
                    value="linear",
                ).classes("w-full")
            elif scan_key == "randomize":
                ui.select([True, False], label="randomize", value=False).classes("w-full")
            else:
                ui.number(
                    scan_key,
                    on_change=lambda e: selected_settings.update(
                        {e.sender._props["label"]: e.value}
                    ),
                )

    return selected_settings


def get_points(selected_settings: dict, scan_key: str) -> None:
    """Choose whether input field for scan points is the step size or number of
       points.

       If input is `points`, an array of from `min` to `max` is made using the
       given number of points.
       If input is `step_size`, an array from `min` to `max` is made with the given
       step size.
       Number of points generatred for step size is rounded to nearest integer,
       leading the actual step size to be slight different from the input value.

    Args:

        selected_settings (dict): Scan settings to add.
        scan_key (str): The key for accessing the value in the scan settings
            dictionary. In this function, `scan_key` should always be `points`.
    """

    def steps_to_points(selected_settings, input_value, stepsize_or_points):
        try:
            if stepsize_or_points.value == "step size":
                span = selected_settings["max"] - selected_settings["min"]
                points = round(span / input_value)
                selected_settings.update({"points": points})
            else:
                selected_settings.update({"points": input_value})
        except ZeroDivisionError:
            pass  ## probably don't need logging, zero division only happens when typing input
        return

    ui.number(
        scan_key,
        value=selected_settings[scan_key],
        on_change=lambda e: steps_to_points(selected_settings, e.value, stepsize_or_points),
    )
    stepsize_or_points = ui.radio(["points", "step size"], value="points")
    return


async def remove_scan(
    gui_fields: gui_utils.GUI_fields, meas_settings: bc.Measurement_Settings
):
    """Removes the scan selected in the scan table from both the scan table and
    the `meas_settings`.

    Args:
        gui_fields (gui_utils.GUI_fields): _description_
        meas_settings (bc.Measurement_Settings): _description_
    """
    row = await scan_table_holder.value.get_selected_row()
    name = f'{row["name"]}-{row["parameter"]}'
    del meas_settings.scan_collection[name]
    table_args_holder.value = scan_table_args(gui_fields, meas_settings)
    update_table()
    return


if __name__ in {"__main__", "__mp_main__"}:
    meas_config = bc.utils.load_config(
        "C:\\Users\\walsworth1\\Documents\\Jupyter_Notebooks\\baecon\\tests\\generated_config.toml"
    )

    meas_settings = bc.make_measurement_settings(meas_config)

    gui_fields = gui_utils.GUI_fields()

    with ui.card():
        main(gui_fields, meas_settings)

    ui.run(port=8082)
