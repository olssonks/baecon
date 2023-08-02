from functools import partial
from pathlib import Path
from typing import Any

from nicegui import app, events, ui

import baecon as bc
from baecon.GUI import gui_utils

devices_catagory_holder = gui_utils.Holder()

devices_card_holder = gui_utils.Holder({})

device_column_holder = gui_utils.Holder()

""":todo:
    Devices currenlty can only appear in the cards. Adding custom pages for devices
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
            ui.button(
                add_label,
                on_click=partial(
                    add_device_button, *(devices_catagory, gui_fields, meas_settings)
                ),
            ).classes("w-full")
            ## Remove function isn't async
            ui.button(
                remove_label,
                on_click=lambda: remove_device_button(
                    devices_catagory, gui_fields, meas_settings
                ),
            ).classes("w-full")

    return update_devices_card, (devices_catagory,)


def update_devices_card(
    device_category: str,
    gui_fields: gui_utils.GUI_fields,
    meas_settings: bc.Measurement_Settings,
):
    """Updates the card listing devices when a device is added or removed.

    Args:
        device_category (str): `Scan_Devices` or `Acquisition_Devices`.
        gui_fields (gui_utils.GUI_fields): All fields for the GUI.
        meas_settings (bc.Measurement_Settings): Settings that completely
            describe the measurement.
    """
    devices_catagory = device_category
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
    device_category: str,
    gui_fields: gui_utils.GUI_fields,
    meas_settings: bc.Measurement_Settings,
):
    """Async function for calling the add_device_dialog window.

    Args:
        device_category (str): `Scan_Devices` or `Acquisition_Devices`.
        gui_fields (gui_utils.GUI_fields): All fields for the GUI.
        meas_settings (bc.Measurement_Settings): Settings that completely
            describe the measurement.
    """
    await add_device_dialog(device_category, gui_fields, meas_settings)
    return


async def add_device_dialog(
    device_category: str,
    gui_fields: gui_utils.GUI_fields,
    meas_settings: bc.Measurement_Settings,
):
    """Makes a :py:class:`ui.dialog` for choosing a device to add.

       The list of devices is populated from the :py:obj:`bc.DEVICES_DIRECTORY`.
       When adding a device you choose the working name, a.k.a. nickname,
       for the device to have in the experiment, which is different than the
       device class (a.k.a type).

       The device will not be loaded without a working name.

    Args:
        device_category (str): `Scan_Devices` or `Acquisition_Devices`.
        gui_fields (gui_utils.GUI_fields): All fields for the GUI.
        meas_settings (bc.Measurement_Settings): Settings that completely
            describe the measurement.
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
        with ui.row().classes("w-full no-wrap"):
            with ui.column():
                ui.button(
                    "Choose Device",
                    on_click=partial(
                        choose_device,
                        *(
                            grid,
                            dialog,
                            device_category,
                            device_name_holder,
                            device_type_holder,
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
                        1: "Load last device configuration.",
                        0: "Choose configuration to load.",
                    },
                    value=1,
                ).bind_value(device_load_last, "value")
    dialog.open()
    return


def generate_device_list(device_name_holder: gui_utils.Holder):
    """Generates the list of devices available to load in `baecon`.

    Reads :py:obj:`baecon.DEVICES_DIRECTORY` and populates the
    :py:class:`aggrid <nicegui.ui.aggrid>`.

    Args:
        device_name_holder (gui_utils.Holder): Holder for working name of device.

    Returns:
        aggrid: The :py:class:`aggrid <nicegui.ui.aggrid>` listing the available devices.
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
    device_name_holder: gui_utils.Holder,
    device_type_holder: gui_utils.Holder,
    device_gui_enabled: gui_utils.Holder,
    device_load_last: gui_utils.Holder,
    gui_fields: gui_utils.GUI_fields,
    meas_settings: bc.Measurement_Settings,
):
    """Loads chosen :py:class:`Device <baecon.device.Device>`.

       On clicking the `Choose Device`, the device is loaded with

    Args:
        grid (ui.aggrid): Table showing available device types.
        dialog (ui.dialog): Pop-up dialog holding for choosing a device.
        device_category (str): `Scan_Devices` or `Acquisition_Devices`.
        device_name_holder (gui_utils.Holder): Holder for chosen name.
        device_type_holder (gui_utils.Holder): Holder for type of
            device, e.g. SG380 or NIDAQ_Base.
        device_gui_enabled (gui_utils.Holder): Boolean indicating to open
            device specific gui.
        device_load_last (gui_utils.Holder): Boolean; `True` indicates load `last_config`
            and `False` indicates to launch the file picker dialog.
        gui_fields (gui_utils.GUI_fields): All fields for the GUI.
        meas_settings (bc.Measurement_Settings): Settings that completely
            describe the measurement.
    """
    row = await grid.get_selected_row()
    if device_name_holder.value == "":
        ui.notify(
            "Please Choose Working Name",
            position="center",
            type="negative",
            timeout=1000,
        )
    elif row is None:
        ui.notify(
            "No Device selected",
            position="center",
            type="negative",
            timeout=1000,
        )
    else:
        device_type_holder.update(row["name"])
        await add_chosen_device(
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


async def add_chosen_device(
    device_category: str,
    device_name_holder: gui_utils.Holder,
    device_type_holder: gui_utils.Holder,
    device_load_last: gui_utils.Holder,
    gui_fields: gui_utils.GUI_fields,
    meas_settings: bc.Measurement_Settings,
):
    """Adds device using the desired configuration.

       By default, the `last_config` for the device is loaded. If no such file
       exists, the `default` config file is load. And if no such file exists
       again, the class default configurations are used.

       Alternatively, you can choose to select a configuration file to load.

    Args:
        device_category (str): `Scan_Devices` or `Acquisition_Devices`.
        device_name_holder (gui_utils.Holder): Holder for chosen name.
        device_type_holder (gui_utils.Holder): Holder for type of
            device, e.g. SG380 or NIDAQ_Base.
        device_load_last (gui_utils.Holder): Boolean; `True` indicates load `last_config`
            and `False` indicates to launch the file picker dialog.
        gui_fields (gui_utils.GUI_fields): All fields for the GUI.
        meas_settings (bc.Measurement_Settings): Settings that completely
            describe the measurement.
    """
    devices_catagory = device_category
    gui_utils.Holder()
    if not device_load_last.value:
        device_config = await device_configuration_dialog(device_type_holder)
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
    device_type_holder: gui_utils.Holder,
) -> dict:
    """Opens dialog for choosing a configuration file for the device.

    Args:
        device_type_holder (gui_utils.Holder): Holds the type (e.g. SG380) for
            the device.

    Returns:
        dict: Configruation dictionary for the device.
    """
    device_directory = bc.DEVICES_DIRECTORY / device_type_holder.value
    file = await gui_utils.load_file(device_directory)
    config = bc.utils.load_config(file)
    return config


def open_device_gui(
    device_category: str,
    device_name_holder: gui_utils.Holder,
    meas_settings: bc.Measurement_Settings,
) -> None:
    """Opens device specific GUI in a seperate browser tab.

       Device specific GUI should be kept in the corresponding Device directory.

    Args:
        device_category (str): `Scan_Devices` or `Acquisition_Devices`.
        device_name_holder (gui_utils.Holder): Holder for chosen name.
        meas_settings (bc.Measurement_Settings): Settings that completely
            describe the measurement.
    """

    if device_category == "Scan Devices":
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
    """Finds path to the `last_config` file and loads its configuration

       If `last_file` is not found in the device's directory, `None` is passed
       to :py:meth:`device_load_config`.

    Args:
        device_load_last (gui_utils.Holder): Boolean; `True` indicates load `last_config`
            and `False` indicates to launch the file picker dialog.
        device_name_holder (gui_utils.Holder): Holder for chosen name.
        device_type_holder (gui_utils.Holder): Holder for type of
            device, e.g. SG380 or NIDAQ_Base.

    Returns:
        dict: Configruation dictionary for the device.
    """

    device_directory = bc.DEVICES_DIRECTORY / device_type_holder.value

    config_file = None
    for item in device_directory.iterdir():  ## items are absolute Paths
        if "last_config" in str(item):
            config_file = str(item)
            break

    device_config = device_load_config(config_file, device_name_holder, device_type_holder)

    return device_config


def device_load_config(
    file: str, device_name_holder: gui_utils.Holder, device_type_holder: gui_utils.Holder
) -> dict:
    """Loads device configuration from the file provided and returns it in a dictionary.

       If `None` is given as the file, then this method will look for the
       `default` configuration file. If that file isn't found, this method
       return a dictionary of the class defaults.

    Args:
        file (str): String of file path.
        device_name_holder (gui_utils.Holder): Holder for chosen name.
        device_type_holder (gui_utils.Holder): Holder for type of
            device, e.g. SG380 or NIDAQ_Base.

    Returns:
        dict: Configruation dictionary for the device.
    """
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
    """
    Generates dialog to select which device to remove and then removes it.

    Args:
        device_category (str): `Scan_Devices` or `Acquisition_Devices`.
        gui_fields (gui_utils.GUI_fields): All fields for the GUI.
        meas_settings (bc.Measurement_Settings): Settings that completely
            describe the measurement.
    """
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
    """Populates the device card with the measurement devices.

       These are the devices listed in `meas_settings`.

    Args:
        device_category (str): `Scan_Devices` or `Acquisition_Devices`.
        gui_fields (gui_utils.GUI_fields): All fields for the GUI.
        meas_settings (bc.Measurement_Settings): Settings that completely
            describe the measurement.
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
    """Buttons within the device drop-down expansion.

       These allow for opening the device specific GUI, reconnecting to the
       device, and toggling device output on and off.

    Args:
        device_name (str): Chosen working name.
        device_category (str): `Scan_Devices` or `Acquisition_Devices`.
        meas_settings (bc.Measurement_Settings): Settings that completely
            describe the measurement.
    """
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
    """Generates the tabs in the drop-down expansion of the device.

       The tabs are given by any dictionary term given in the configuration
       dictinary. For all device this includes `parameters` and `latent_parameters`.
       Some devices will have extra entries in configuration dictionary, which
       will also be given a tab.

       Each device also gets a tab for saving and loading its configuration to
       a configuration file.

    Args:
        device_name (str): Chosen working name.
        device_configuration (dict): Configuration dictionary for the device.
        device_category (str): `Scan_Devices` or `Acquisition_Devices`.
        gui_fields (gui_utils.GUI_fields): All fields for the GUI.
        meas_settings (bc.Measurement_Settings): Settings that completely
            describe the measurement.
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
    """Populates the device tab with saving and loading GUI elements.

       These elements are buttons for `load`, `save`, and `save as`, as well as
       an input box for the file name.

       :py:meth:`save_as_last_config` is specified in this function, since there
       is already saving happening. Upon the app disconnecting (equivalent to
       shutting down), the current configuration of the device will be save in
       the `last_config` file.

    Args:
        device_category (str): `Scan_Devices` or `Acquisition_Devices`.
        device_name (str): Chosen working name.
        gui_fields (gui_utils.GUI_fields): All fields for the GUI.
        meas_settings (bc.Measurement_Settings): Settings that completely
            describe the measurement.
    """
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
    button_event: events.ClickEventArguments,
    device_category: str,
    gui_fields: gui_utils.GUI_fields,
    meas_settings: bc.Measurement_Settings,
) -> None:
    """Saves current device configuration.

       The configuration is saved to the file currently specified in the GUI.
       The name of the device is taken from the click arguments of the button
       object.


    Args:
        button_event (events.ClickEventArguments): Event args from clicking
            save button.
        device_category (str): `Scan_Devices` or `Acquisition_Devices`.
        gui_fields (gui_utils.GUI_fields): All fields for the GUI.
        meas_settings (bc.Measurement_Settings): Settings that completely
            describe the measurement.
    """
    device, device_files, _ = determine_device(
        button_event, device_category, gui_fields, meas_settings
    )
    device.update_configuration()
    file = device_files.get(device.name)
    if file is not None:
        bc.utils.dump_config(device.configuration, file)
    return


async def save_as_button(
    button_event: events.ClickEventArguments,
    device_category: str,
    gui_fields: gui_utils.GUI_fields,
    meas_settings: bc.Measurement_Settings,
) -> None:
    """Opens dialog window to pick file to save the device as.

       The name of the device is taken from the click arguments of the button
       object.

    Args:
        button_event (events.ClickEventArguments): Event args from clicking
            save button.
        device_category (str): `Scan_Devices` or `Acquisition_Devices`.
        gui_fields (gui_utils.GUI_fields): All fields for the GUI.
        meas_settings (bc.Measurement_Settings): Settings that completely
            describe the measurement.
    """

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
    gui_event: events.EventArguments,
    devices_catagory: str,
    gui_fields: gui_utils.GUI_fields,
    meas_settings: bc.Measurement_Settings,
) -> tuple[bc.Device, dict, dict]:
    """Determines device from the GUI event arguments and device catagory.

       The property `sender` of `gui_event` is used a the start element for
       the :py:meth:`gui_utils.find_gui_element`.

       This method then returns the :py:class:`Device <baecon.device.Device>`
       of the device, a `dict` of device names and currently used config file,
       and `acquisition_devices or `scan_devices` property of
       `bc.Measurement_Settings`.

    Args:
        button_event (events.ClickEventArguments): Event args from clicking
            save button.
        device_category (str): `Scan_Devices` or `Acquisition_Devices`.
        gui_fields (gui_utils.GUI_fields): All fields for the GUI.
        meas_settings (bc.Measurement_Settings): Settings that completely
            describe the measurement.
    Returns:
        tuple[bc.Device, dict, dict]: Tuple where the first element is a
            :py:class:`Device <baecon.device.Device>` and the second a dictitonary
            with elements `{device_name: config file name}`, and either
            `acquisition_devices or `scan_devices`.
    """
    ## more  efficient way to get device name??
    element = gui_event.sender
    found_element = gui_utils.find_gui_element(element, "q-expansion-item")
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
    button_event: events.ClickEventArguments,
    device_catory: str,
    gui_fields: gui_utils.GUI_fields,
    meas_settings: bc.Measurement_Settings,
) -> None:
    """Opens a dialog with to pick and load a device configuration file.

       The name of the device is taken from the click arguments of the button
       object.

    Args:
        button_event (events.ClickEventArguments): Event args from clicking
            save button.
        device_category (str): `Scan_Devices` or `Acquisition_Devices`.
        gui_fields (gui_utils.GUI_fields): All fields for the GUI.
        meas_settings (bc.Measurement_Settings): Settings that completely
            describe the measurement.
    """
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
        meas_settings (bc.Measurement_Settings): Settings that completely
            describe the measurement.
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
        device_name (str): Device being controlled.
        meas_settings (bc.Measurement_Settings): Settings that completely
            describe the measurement.
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
        meas_settings (bc.Measurement_Settings): Settings that completely
            describe the measurement.
    """
    if device_name in meas_settings.scan_devices:
        device = meas_settings.scan_devices[device_name]
    elif device_name in meas_settings.acquisition_devices:
        device = meas_settings.acquisition_devices[device_name]
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
    contents = bc.DEVICES_DIRECTORY.iterdir()
    devices = [
        str(content.relative_to(bc.DEVICES_DIRECTORY))
        for content in contents
        if content.is_dir()
    ]
    return devices


## Not working, the column holding the expansion elements is empty when calling it on shutdown
## not sure when these elements are removed
async def save_as_last_config(
    button_element: events.ClickEventArguments,
    devices_catagory: str,
    gui_fields: gui_utils.GUI_fields,
    meas_settings: bc.Measurement_Settings,
) -> None:
    """Save current device configuration in `last_config` file.

       This method is called when the GUI is shutdown. Shutdown events don't
       send event arguments, so the save button element is used to create
       dummy `ClickEventArguments`.

       .. todo::
            This method is not working correctly.

    Args:
        button_event (events.ClickEventArguments): Event args from clicking
            save button.
        device_category (str): `Scan_Devices` or `Acquisition_Devices`.
        gui_fields (gui_utils.GUI_fields): All fields for the GUI.
        meas_settings (bc.Measurement_Settings): Settings that completely
            describe the measurement.
    """
    dummy_event = events.ClickEventArguments(
        sender=button_element, client=button_element.client
    )

    device, device_files, _ = determine_device(
        dummy_event, devices_catagory, gui_fields, meas_settings
    )
    device.update_configuration()
    device_directory = bc.DEVICES_DIRECTORY / f"{device.configuration.get('device')}"
    file = device_directory / "last_config.toml"
    if file is not None:
        bc.utils.dump_config(device.configuration, file)
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
