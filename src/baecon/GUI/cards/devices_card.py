import os
from functools import partial
from pathlib import Path
from typing import Any

from nicegui import app, ui, events

import baecon as bc
from baecon.GUI import gui_utils


devices_catagory_holder = gui_utils.Holder()

devices_card_holder = gui_utils.Holder({})

device_column_holder = gui_utils.Holder()

""":todo:
    Devices currenlty can only apear in the cards. Adding custom pages for devices
    would be good, so for things like pulse generators can display the pulse
    pattern, or for cameras show an image for aligning etc.
"""


def main(
    gui_fields: gui_utils.GUI_fields,
    meas_settings: bc.Measurement_Settings,
    devices_catagory: str,
):
    """
    Main function for the Devices GUI card.
        Both scan_devices and acquisition_devices use this card.

    Flow:
        * Device card is constructed and populated based on gui_config
          and devices_catagory.
        * On pressing add or remove device buttons, the devices_catagory_holder will
          be updated based on the button text, and the device will be added
          to gui_config.
        * After device is added/removed, the list of devices is updated by
          devices_catagory_holder as the key for the correct card in
          devices_card_holder.

    **This flow is a bit clumsy, but I do not know how to best pass or bind
    the values so work with the async functions.**

    `functools.partial` can be used to provide args to async functions.

    Args:
        gui_config (gui_utils.GUI_Measurement_Configuration): The dictionary of
            Measurement_Settings determined from the GUI fields. At time of
            measurement, this is passed to baecon.
        meas_settings (bc.Measurement_Settings): Object defining the entire
            measurement.
        devices_catagory (str): "Scan Devices" or "Acquisition Devices" to
            make the respective cards.
    """

    devices_catagory_holder.update(devices_catagory)

    add_label, remove_label = add_remove_button_labels(devices_catagory_holder)

    with ui.column().classes("w-full h-full place-content-around") as device_column:
        device_column_holder.update(device_column)
        ui.label(
            devices_catagory_holder.value
        )  ## the label of this column is used to index whethers its the scan card or aqcuisition card
        devices_card_holder.value.update({devices_catagory: ui.card().classes("w-full")})
        with devices_card_holder.value[devices_catagory]:
            show_devices(devices_catagory, gui_fields, meas_settings)
        with ui.column().classes("w-full"):
            ## async functions don't work with on_click and args
            ## on_click will pass the event e when calling method without args
            ## functools partial method doesn't work when trying to use event as an arg
            async def add_fix(e):
                await add_device_button(e, devices_catagory, gui_fields, meas_settings)

            ui.button(add_label, on_click=add_fix).classes("w-full")
            ## Remove function isn't async
            ui.button(
                remove_label,
                on_click=lambda: remove_device_button(
                    devices_catagory, gui_fields, meas_settings
                ),
            ).classes("w-full")

    return update_devices_card, (devices_catagory,)


# def update_card(
#     gui_fields: gui_utils.GUI_fields,
#     meas_settings: bc.Measurement_Settings,
# ):
#     device_column = device_column_holder.value
#     update_devices_card(device_column, gui_fields, meas_settings)
#     return


def update_devices_card(
    device_category: str,
    gui_fields: gui_utils.GUI_fields,
    meas_settings: bc.Measurement_Settings,
):
    """Updates the card listing devices when a device is added or removed."""
    devices_catagory = device_category  # device_column.default_slot.children[0].text
    card = devices_card_holder.value[devices_catagory]
    card.clear()
    with card:
        show_devices(device_category, gui_fields, meas_settings)
    return


def add_remove_button_labels(devices_catagory_holder: gui_utils.Holder) -> tuple:
    """Chooses the button labels for either ``Scan Devices`` or ``Acquisition Device``.

    Args:
        devices_catagory_holder (gui_utils.holder): Holder object for which
            device catagory the card is.

    Returns:
        tuple: The labels for the buttons for add_device_button and
            remove_device_button.
    """
    # devices_catagory = device_column
    if devices_catagory_holder.value == "Scan Devices":
        add_label = "Add Scan Device"
        remove_label = "Remove Scan Device"
    elif devices_catagory_holder.value == "Acquisition Devices":
        add_label = "Add Acqui. Device"
        remove_label = "Remove Acqui. Device"
    else:
        print('Devices must be "Scan Devices" or "Acquisition Devices".')
        add_label = "Try again"
        remove_label = "Remove Acqui Device"
    return (add_label, remove_label)


## might not need this functin anymore
## could remove this func and just use add_device_dialog when clicking Add Device button
async def add_device_button(
    click_event,
    device_category: str,
    gui_fields: gui_utils.GUI_fields,
    meas_settings: bc.Measurement_Settings,
):
    """
    Async function for calling the add_device_dialog window.
        Catagory of device is determined from the click_event_arg.

    Args:
        click_event (nicegui event): Click information passed to this function
            from the button element. The text of the button is used to determine
            which catagory of device to work with.
    """
    await add_device_dialog(device_category, gui_fields, meas_settings)
    return


async def add_device_dialog(
    device_category: str,
    gui_fields: gui_utils.GUI_fields,
    meas_settings: bc.Measurement_Settings,
):
    """
    Dialog window for choosing a device to add.
        The list of devices is populated
        by the "Instruments" directory in baecon. When adding a device you choose
        the working name, or nickname for the device in the experiment, which is
        different than the device class.

    Once the working name and device type are selected, the device will
    be loaded on into gui_config_holder with the

    """
    device_name_holder = gui_utils.Holder()
    device_type_holder = gui_utils.Holder()

    with ui.dialog() as dialog, ui.card():
        device_gui_enabled = gui_utils.Holder(False)
        device_load_last = gui_utils.Holder(True)
        ## use bind_value not bind_enabled, which makes the check box not clickable
        ui.checkbox("Launch in Device Gui", value=False).bind_value(
            device_gui_enabled, "value"
        )

        grid = generate_device_list(device_name_holder)
        with ui.row().classes('w-full no-wrap'):
            with ui.column():
                ui.button(
                    "Choose Device",
                    on_click=partial(
                        choose_device,
                        *(
                            grid,
                            dialog,
                            device_category,
                            device_type_holder,
                            device_name_holder,
                            device_gui_enabled,
                            device_load_last,
                            gui_fields,
                            meas_settings,
                        ),
                    ),
                )
                ui.button("Cancel", on_click=(dialog.close)).props("outline")
            with ui.column():
                ui.radio(
                    {
                        1: 'Load last device configuration.',
                        0: "Choose configuration to load.",
                    },
                    value=1,
                ).bind_value(device_load_last, "value")
    dialog.open()
    return


def generate_device_list(device_name_holder: gui_utils.Holder):
    """Generates the list of devices available to load in `baecon`.

    Reads :py:obj:`baecon.DEVICES_DIRECTORY` and populates the
    :py:class:`aggrid<nicegui.ui.aggrid>`.

    Args:
        device_name_holder (gui_utils.Holder): Holder for working name of device.

    Returns:
        aggrid: The :py:class:`aggrid<nicegui.ui.aggrid>` listing the available devices.
    """
    ui.input(
        "Device Name",
        placeholder="Choose Working Name (e.g., SG1)",
        on_change=lambda e: device_name_holder.update(e.value),
    ).classes("w-full")
    rows = [{"name": device} for device in available_devices()]
    grid = ui.aggrid(
        {
            "columnDefs": [{"field": "name", "headerName": "File"}],
            "rowData": rows,
            "rowSelection": "single",
        }
    ).classes("w-96")
    return grid


## Would be good to have less arguments, but not pack them into a tuple or something
async def choose_device(
    grid: ui.aggrid,
    dialog: ui.dialog,
    device_category: str,
    device_type_holder: gui_utils.Holder,
    device_name_holder: gui_utils.Holder,
    device_gui_enabled: gui_utils.Holder,
    device_load_last: gui_utils.Holder,
    gui_fields: gui_utils.GUI_fields,
    meas_settings: bc.Measurement_Settings,
):
    """Loads chosen :py:class:`Device<baecon.device.Device>`.

    On clicking the `Choose Device`, the device is loaded with

    Args:
        device_gui_enabled (gui_utils.Holder): Boolean indicating to open
            device specific gui.
        grid (ui.aggrid): Table showing available device types.
        dialog (ui.dialog): Pop-up dialog holding for choosing a device.
        device_category (str): Scan or acquisition device.
        device_type_holder (gui_utils.Holder): Holder for type of
            device, e.g. SG380 or NIDAQ_Base.
        device_name_holder (gui_utils.Holder): Holder for chosen name.
        gui_fields (gui_utils.GUI_fields): Object holding all the fields in
            :py:func:`baecon.GUI.baecon_GUI.main`.
        meas_settings (bc.Measurement_Settings): _description_
    """
    if device_name_holder.value == "":  # noqa: PLC1901
        ui.notify(
            "Please Choose Working Name",
            position="center",
            type="negative",
            timeout=1000,
        )
    else:
        row = await grid.get_selected_row()
        device_type_holder.update(row["name"])
        await add_device_configs(
            device_category,
            device_name_holder,
            device_type_holder,
            device_load_last,
            gui_fields,
            meas_settings,
        )

        if device_gui_enabled.value:
            open_device_gui(device_category, device_name_holder, meas_settings)

        dialog.close()
    return


async def add_device_configs(
    device_category: str,
    device_name_holder: gui_utils.Holder,
    device_type_holder: gui_utils.Holder,
    device_load_last: gui_utils.Holder,
    gui_fields: gui_utils.GUI_fields,
    meas_settings: bc.Measurement_Settings,
):
    """
    Adds selected device to :py:class:`meas_settings<baecon.base.Measurement_Settings>`.

    Args:
        device_type_holder (gui_utils.holder): Holder for selected device type, e.g. SG380.
        device_name_holder (gui_utils.holder): Holder for device name input.
        meas_settings (bc.Measurement_Settings): Object defining the entire
            measurement.
    """
    devices_catagory = device_category
    device_config_holder = gui_utils.Holder()
    if not device_load_last.value:
        device_config = await device_configuration_dialog(
            device_name_holder, device_type_holder
        )
    else:
        device_config = get_device_config(
            device_load_last, device_name_holder, device_type_holder
        )

    if devices_catagory == "Scan Devices":
        meas_settings.scan_devices.update({device_name_holder.value: device_config})
        bc.add_device(device_config, meas_settings.scan_devices)
    else:
        meas_settings.acquisition_devices.update({device_name_holder.value: device_config})
        bc.add_device(device_config, meas_settings.acquisition_devices)

    ui.notify(
        f"{device_name_holder.value} has been added to the devices.",
        position="top",
        type="positive",
    )
    update_devices_card(device_category, gui_fields, meas_settings)
    return


async def device_configuration_dialog(
    device_name_holder: gui_utils.Holder,
    device_type_holder: gui_utils.Holder,
):
    device_directory = bc.DEVICES_DIRECTORY / device_type_holder.value
    file = await gui_utils.load_file(device_directory)
    config = bc.utils.load_config(file)
    return config


def open_device_gui(device_category: str, device_name_holder, meas_settings) -> None:
    devices_catagory = device_category
    if devices_catagory == "Scan Devices":
        device = meas_settings.scan_devices.get(device_name_holder.value)
    else:
        device = meas_settings.acquisition_devices.get(device_name_holder.value)

    ## part of work around to open device gui in new tab
    gui_router, gui_name = device.get_device_gui()

    async def gui():
        await ui.run_javascript(f"window.open(\'/{gui_name}\', \'_blank\');", timeout=1000.0)

    app.include_router(gui_router)
    ## storage.general needs to JSON encodable which device is not
    app.storage.__setattr__(gui_name, device)
    ui.timer(0.1, gui, once=True)
    return


def get_device_config(
    device_load_last: gui_utils.Holder,
    device_name_holder: gui_utils.Holder,
    device_type_holder: gui_utils.Holder,
) -> dict:
    """Checks for default configuration file in the directory of the selected
    device.
    Generates and returns configuration dictionary for the device.
    :todo:
            May want to rethink this. Devices can just have their defaults
            defined within their class.
    Args:
        device_type_holder (gui_utils.holder): Holder for selected device type.
        device_name_holder (gui_utils.holder): Holder for device name input.

    Returns:
        dict: Dictionary with the default configuration for the device.
    """

    # device_path = os.path.join(bc.DEVICES_DIRECTORY, device_type_holder.value)
    device_directory = bc.DEVICES_DIRECTORY / device_type_holder.value
    config_names = {0: "default", 1: "last_config"}

    config_file = None
    for item in device_directory.iterdir():  ## items are absolute Paths
        if config_names[device_load_last.value] in str(item):
            config_file = str(item)
            break

    device_config = device_load_config(config_file, device_name_holder, device_type_holder)

    return device_config


def device_load_config(
    file: str, device_name_holder: gui_utils.Holder, device_type_holder: gui_utils.Holder
):
    if file is not None:
        config = bc.utils.load_config(file)
    else:
        print(
            f"Error loading configuration file. No default or last found.\
               Using {device_type_holder.value} class defaults."
        )
        config = {}

    config.update({"name": device_name_holder.value})
    config.update({"device": device_type_holder.value})
    return config


def remove_device_button(
    device_category: str,
    gui_fields: gui_utils.GUI_fields,
    meas_settings: bc.Measurement_Settings,
):
    """Opens dialog to select device and removes it.

    Args:
        click_event: `nicegui` event object for the remove device button. The
            category (scan or aquisition) is selected based on the label of the
            button, which is given by `click_event.sender.text`.
    """
    # device_category = click_event.sender.text

    if "Scan" in device_category:
        devices_catagory_holder.value = "Scan Devices"
        device_list = meas_settings.scan_devices
    else:
        devices_catagory_holder.value = "Acquisition  Devices"
        device_list = meas_settings.acquisition_devices

    def del_device():
        device_list.pop(selected_device.value)
        update_devices_card(device_category, gui_fields, meas_settings)

    with ui.dialog() as dialog, ui.card():
        devices = list(device_list.keys())
        selected_device = ui.select(devices, label="Choose Device to remove").classes("w-96")
        with ui.row():
            ui.button("Cancel", on_click=(dialog.close)).props("outline")
            remove_button = ui.button("Remove Device", on_click=del_device)
            remove_button.on("click", dialog.close)
    dialog.open()
    return


def show_devices(
    device_category: str,
    gui_fields: gui_utils.GUI_fields,
    meas_settings: bc.Measurement_Settings,
):
    """Populates the device card with currently chosen devices.
    Adds the scan and acquisition devices listed in `meas_settings`.

    Args:
        meas_settings (bc.Measurement_Settings): Object defining the entire
            measurement.
    """
    devices_catagory = device_category
    if devices_catagory == "Scan Devices":
        device_list = meas_settings.scan_devices
    else:
        device_list = meas_settings.acquisition_devices
    with ui.column().classes("w-full"):
        for name, device in device_list.items():
            with ui.expansion(f"{name} ({device.__module__})").classes("w-full text-center"):
                with ui.column().classes("w-full"):
                    device_buttons(name, device_category, meas_settings)
                    device_tabs(
                        name,
                        device.configuration,
                        device_category,
                        gui_fields,
                        meas_settings,
                    )
    return


def device_buttons(device_name: str, category: str, meas_settings: bc.Measurement_Settings):
    device_name_holder = gui_utils.Holder(device_name)
    with ui.column().classes("w-full"):
        with ui.row().classes("w-full no-wrap"):
            ui.button(
                "Launch Device GUI",
                on_click=lambda: open_device_gui(
                    category, device_name_holder, meas_settings
                ),
            ).classes("w-full")
            ui.button("Reconnect").classes("w-full")
        with ui.row().classes("w-full no-wrap items-center bg-secondary"):
            ui.label("Output:")
            ui.radio(
                {1: "On", 0: "Off"},
                value=1,
                on_change=lambda e: device_output(e.value, device_name, meas_settings),
            ).props("inline")
    return


def device_tabs(
    device_name: str,
    device_configuration: dict,
    device_category: str,
    gui_fields: gui_utils.GUI_fields,
    meas_settings: bc.Measurement_Settings,
):
    """Creates the drop down tabs for all the devices.
    Within the drop down, tabs are create for all the attributes of the
    device, which are `parameters`, `latent_parameters`, and any other
    custom attribute for that the device type.

    Args:
        device_name (str): Working name of the device.
        device_configuration (dict): The `configuration` attribute of the Device
            containing all information do set up a device.
        meas_settings (bc.Measurement_Settings): _description_
    """
    ## device_parameters are: parameters, latent_parameters, etc.
    with ui.tabs().classes("w-full") as tabs:
        for param_name, entry in list(device_configuration.items()):
            if isinstance(entry, dict):
                ui.tab(param_name).classes("w-full")
        ui.tab("Save/Load").classes("w-full")

    with ui.tab_panels(tabs, value="parameters").classes("w-full"):
        for param_name, entry in list(device_configuration.items()):
            if isinstance(entry, dict):
                with ui.tab_panel(param_name).classes("w-full"):
                    list_parameters(
                        device_name, device_configuration[param_name], meas_settings
                    )
        with ui.tab_panel("Save/Load").classes("w-full h-full"):
            save_load_tab(device_category, device_name, gui_fields, meas_settings)
    return


def save_load_tab(
    device_category: str,
    device_name: str,
    gui_fields: gui_utils.GUI_fields,
    meas_settings: bc.Measurement_Settings,
):
    with ui.column().classes("w-full h-full"):
        devices_catagory = device_category
        if devices_catagory == "Scan Devices":
            device_files = gui_fields.scan_dev_files
        else:
            device_files = gui_fields.acq_dev_files
        device_files.update({device_name: ""})
        ui.input("File", placeholder="Choose device configuration file").classes(
            "w-full h-full"
        ).bind_value(device_files, f"{device_name}").props(
            "type=textarea autogrow rounded outlined"
        )
        with ui.row().classes("w-full no-wrap"):
            ## Better way to do this?
            async def load_fix(e):
                await load_button(e, device_category, gui_fields, meas_settings)

            async def save_fix(e):
                await save_button(e, device_category, gui_fields, meas_settings)

            async def save_as_fix(e):
                await save_as_button(e, device_category, gui_fields, meas_settings)

            ui.button(
                "Load Device",
                on_click=load_fix,
            ).classes("w-full")
            ui.button("Save Device As", on_click=save_as_fix).classes("w-full")
            save_button = ui.button("Save Device", on_click=save_fix).classes("w-full")

    app.on_disconnect(
        partial(
            save_as_last_config, *(save_button, device_category, gui_fields, meas_settings)
        )
    )

    return


async def save_button(
    button_event,
    device_category: str,
    gui_fields: gui_utils.GUI_fields,
    meas_settings: bc.Measurement_Settings,
) -> None:
    device, device_files, _ = determine_device(
        button_event, device_category, gui_fields, meas_settings
    )
    device.update_configuration()
    file = device_files.get(device.name)
    if file is not None:
        bc.utils.dump_config(device.configuration, file)
    return


async def save_as_button(
    button_event,
    device_category: str,
    gui_fields: gui_utils.GUI_fields,
    meas_settings: bc.Measurement_Settings,
) -> None:
    device, device_files, _ = determine_device(
        button_event, device_category, gui_fields, meas_settings
    )
    device_directory = bc.DEVICES_DIRECTORY / f"{device.configuration.get('device')}"
    file = await gui_utils.pick_file(device_directory)
    if file is not None:
        device.update_configuration()
        device_files.update({device.name: file})
        bc.utils.dump_config(device.configuration, file)
    return


def determine_device(
    gui_event,
    devices_catagory: str,
    gui_fields: gui_utils.GUI_fields,
    meas_settings: bc.Measurement_Settings,
) -> tuple[bc.Device, dict]:
    ## more  efficient way to get device name??
    element = gui_event.sender
    found_element = gui_utils.find_gui_element(element, 'q-expansion-item')
    device_name = found_element._props["label"]

    if devices_catagory == "Scan Devices":
        devices = meas_settings.scan_devices
        device_files = gui_fields.scan_dev_files
    else:
        devices = meas_settings.acquisition_devices
        device_files = gui_fields.acq_dev_files
    device: bc.Device = [devices[key] for key in devices.keys() if key in device_name][0]
    return device, device_files, devices


async def load_button(
    button_event,  ## ClickEventArgs
    device_catory: str,
    gui_fields: gui_utils.GUI_fields,
    meas_settings: bc.Measurement_Settings,
):
    device, device_files, devices = determine_device(
        button_event, device_catory, gui_fields, meas_settings
    )
    ## locate expansion item for this device, based on the button

    device_directory = bc.DEVICES_DIRECTORY / f"{device.configuration.get('device')}"
    file = await gui_utils.pick_file(device_directory)
    if file is not None:
        device_config = bc.utils.load_config(file)
        bc.add_device(device_config, devices)
        device_files.update({device_config.get("name"): file})
        update_devices_card(device_catory, gui_fields, meas_settings)
    return


def list_parameters(
    device_name: str, parameters: dict, meas_settings: bc.Measurement_Settings
):
    """Generates a tab and lists the supplied parameters for a device. Here
    parameters includes the devices `parameters`, `latent_parameters`, and
    other parameter dicts specific to the device.

    Args:
        device_name (str): Working name of device for which the tab is being made.
        parameters (dict): Dictionary of parameters for which to create input fields.
        meas_settings (bc.Measurement_Settings): _description_
    """
    with ui.column().classes("w-full"):
        for param_name, value in list(parameters.items()):
            with ui.row().classes("w-full no-wrap items-center bg-secondary"):
                ui.label(param_name).classes("w-full justify-right")
                ui.input(
                    label=param_name,
                    value=value,
                    on_change=lambda e: update_parameter(
                        e.value, e.sender._props["label"], device_name, meas_settings
                    ),
                )
    return


def device_output(value: int, device_name: str, meas_settings: bc.Measurement_Settings):
    """Turns the device on or off.

    Args:
        value (int): On or off values (1 or 0).
        device_name (str): Device being controlled
        meas_settings (bc.Measurement_Settings): _description_
    """
    if device_name in meas_settings.scan_devices:
        device = meas_settings.scan_devices[device_name]
    elif device_name in meas_settings.acquisition_devices:
        device = meas_settings.scan_devices[device_name]
    else:
        pass  ## put logging here
    device.enable_output(value)
    return


def update_parameter(
    value: Any, parameter: str, device_name: str, meas_settings: bc.Measurement_Settings
):
    """Updates the device with the new parameter value.
    Args:
        value (Any): New value of parameter.
        parameter (str): Parameter to set to new value.
        device_name (str): Name of device that's have its value changed.
        meas_settings (bc.Measurement_Settings): _description_
    """
    if device_name in meas_settings.scan_devices:
        device = meas_settings.scan_devices[device_name]
    elif device_name in meas_settings.acquisition_devices:
        device = meas_settings.scan_devices[device_name]
    else:
        pass  ## put logging here

    device.write(parameter, value)
    ## also change value in device configuration
    update_device_configuration(value, parameter, device)
    return


def update_device_configuration(value: Any, parameter: str, device: bc.Device):
    """Update the `configuration` atrribute of the `Device` with a new parameter
    value.

    Args:
        value (Any): Value to update
        parameter (str): Parameter to update.
        device (bc.Device): Device to update.
    """
    for _config_key, config_val in device.configuration.items():
        if isinstance(config_val, dict) and (parameter in config_val.keys()):
            config_val.update({parameter: value})
    return


def available_devices() -> list:
    """Reads the modules in the `Devices` folder and returns list.

    Returns:
        list: _List of `Device` modules available.
    """
    device_path = bc.DEVICES_DIRECTORY
    contents = os.listdir(device_path)
    devices = [content for content in contents if os.path.isdir(device_path / content)]
    return devices


## Not working, the column holding the expansion elements is empty when calling it on shutdown
## not sure when these elements are removed
async def save_as_last_config(
    button_element,
    devices_catagory: str,
    gui_fields: gui_utils.GUI_fields,
    meas_settings: bc.Measurement_Settings,
):
    dummy_event = events.ClickEventArguments(
        sender=button_element, client=button_element.client
    )  ## app.on_shutdown doesn't pass event args

    device, device_files, _ = determine_device(
        dummy_event, devices_catagory, gui_fields, meas_settings
    )
    device.update_configuration()
    device_directory = bc.DEVICES_DIRECTORY / f"{device.configuration.get('device')}"
    file = device_directory / "last_config.toml"
    if file is not None:
        bc.utils.dump_config(device.configuration, file)
    return


async def prep_shutdown():
    return


if __name__ in {"__main__", "__mp_main__"}:
    gui_fields = gui_utils.GUI_fields()

    meas_config = bc.utils.load_config(
        "C:\\Users\\walsworth1\\Documents\\Jupyter_Notebooks\\baecon\\tests\\generated_config.toml"
    )

    meas_settings = bc.make_measurement_settings(meas_config)

    main(gui_fields, meas_settings, "Scan Devices")
    app.on_disconnect(app.shutdown)
    ui.run(port=8082, reload=False)
