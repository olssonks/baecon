from nicegui import ui

import sys, os
sys.path.insert(0,'C:\\Users\\walsworth1\\Documents\\Jupyter_Notebooks\\baecon')
from typing import Any

import gui_utils
import baecon as bc

import nicegui

gui_configs_holder = gui_utils.holder()

devices_catagory_holder = gui_utils.holder()

devices_card_holder = gui_utils.holder({})

""":todo:
    Devices currenlty can only apear in the cards. Adding custom pages for devices
    would be good, so for things like pulse generators can display the pulse
    pattern, or for cameras show an image for aligning etc.
"""

def main(gui_config:gui_utils.GUI_Measurement_Configuration,
         meas_settings:bc.Measurement_Settings,
         devices_catagory:str):
    """Main function for the Devices GUI card. Both scan_devices and
        acquisition_devices use this card.
        
        Note:
            Pseudo args are used with async functions, as arguments are difficult
            to handle with the 
        
        Flow:
        * Device card is constructed and populated based on gui_config
            and devices_catagory
        * On pressing add or remove device buttons, the device_catagory_holder will
            be updated based on the button text, and the device will be added
            to gui_config
        * After device is added/removed, the list of devices is updated by
            device_catagory_holder as the key for the correct card in
            devices_card_holder
        **This flow is a bit clumsy, but I do not know how to best pass or bind
            the values so work with the async functions.**

    Args:
        gui_config (gui_utils.GUI_Measurement_Configuration): The dictionary of
            Measurement_Settings determined from the GUI fields. At time of 
            measurement, this is passed to baecon.
        devices_catagory (str): "Scan Devices" or "Acquisition Devices" to 
        make the respective cards.
    """
        
    gui_configs_holder.update(gui_config)
    devices_catagory_holder.update(devices_catagory)
    
    add_label, remove_label = add_remove_button_labels(devices_catagory_holder)
        
    with ui.column().classes('w-full h-full place-content-around'):
        ui.label(devices_catagory_holder.value)
        devices_card_holder.value.update({devices_catagory: ui.card().classes('w-full')})
        with devices_card_holder.value[devices_catagory]:
            show_devices(meas_settings)
        with ui.column().classes('w-full'):
            ui.button(add_label, 
                      on_click=add_device_button).classes('w-full')
            ui.button(remove_label, 
                      on_click=remove_device_button).classes('w-full')
    return


def add_remove_button_labels(devices_catagory_holder:gui_utils.holder)->tuple:
    """Chooses the button labels for either "Scan Devices" or 
        "Acquisition Device"

    Args:
        devices_catagory_holder (gui_utils.holder): Holder object for which
            device catagory the card is.

    Returns:
        tuple: The labels for the buttons for add_device_button and 
            remove_device_button.
    """    
    if devices_catagory_holder.value == 'Scan Devices':
        add_label = 'Add Scan Device'
        remove_label = 'Remove Scan Device'
    elif devices_catagory_holder.value == "Acquisition Devices":
        add_label = 'Add Acqui Device'
        remove_label = 'Remove Acqui Device'
    else:
        print('Devices must be "Scan Devices" or "Acquisition Devices".')
        add_label = 'Try again'
        remove_label = 'Remove Acqui Device'
    return (add_label, remove_label)


def update_devices_card(meas_settings:bc.Measurement_Settings):
    """Updates the card listing devices when a device is added or removed.
    """
    card = devices_card_holder.value[devices_catagory_holder.value]
    card.clear()
    with card:
        show_devices(meas_settings)
    return

async def add_device_button(click_event):
    """Async function for calling the add_device_dialog window. Catagory
        of device is determined from the click_event_arg.
    
    Args:
        click_event (nicegui event): Click information passed to this function
            from the button element. The text of the button is used to determine
            which catagory of device to work with.
    """
    
    device_cat = click_event.sender.text
    
    if 'Scan' in device_cat:
        devices_catagory_holder.value = 'Scan Devices'
    else:
        devices_catagory_holder.value = 'Acquisition Devices'
    
    await add_device_dialog()
    return

async def add_device_dialog():
    """Dialog window for choosing a device to add. The list of devices is populated
        by the "Instruments" directory in baecon. When adding a device you choose
        the working name, or nickname for the device in the experiment, which is 
        different than the device class. 
        
        Once the working name and device type are selected, the device will 
        be loaded on into gui_config_holder with the 

    """
    device_name_holder = gui_utils.holder()
    device_type_holder = gui_utils.holder()
    
    with ui.dialog() as dialog, ui.card():
        use_device_gui = ui.checkbox('Launch in Device Gui')
        name_input = ui.input('Device Name',
                 placeholder='Choose Working Name (e.g., SG1)', 
                 on_change=lambda e: device_name_holder.update(e.value)).classes('w-full')
        rows = [{'name': device} for device in available_devices()]
        grid = ui.aggrid({
            'columnDefs': [{'field': 'name', 'headerName': 'File'}],
            'rowData':rows,
            'rowSelection': 'single',
            }).classes('w-96')
        
        async def choose_device():
            if name_input.value == '':
                ui.notify('Please Choose Working Name',
                          position = 'center',
                          type='negative',
                          timeout=1000)
            else:
                row = await grid.get_selected_row()
                device_type_holder.update(row['name'])
                add_device_configs(device_name_holder,
                                   device_type_holder)
                dialog.close()
            return
        
        ui.button('Choose Device', on_click=choose_device)
        ui.button('Cancel', on_click=(dialog.close)).props('outline')
    
    dialog.open()
    return

def add_device_configs(device_name_holder:gui_utils.holder, 
                       device_type_holder:gui_utils.holder, 
                       meas_settings:bc.Measurement_Settings):
    device_path = os.path.join(bc.Devices_directory, device_type_holder.value)
    found_default = False
    for item in os.listdir(device_path):
        if 'default' in item:
            default_file = os.path.join(device_path, item)
            found_default = True
    if not found_default:
        print(f'No default configuration file found for {device_type_holder.value} in {device_path}')
    default_config = bc.utils.load_config(default_file)
    default_config.update({'name':device_name_holder.value})
    default_config.update({'device':device_type_holder.value})
    if devices_catagory_holder.value == "Scan Devices":
        gui_configs_holder.value\
        .scan_devices.update({device_name_holder.value: default_config})
        bc.add_device(default_config, meas_settings.scan_devices)
    else: 
        gui_configs_holder.value\
        .acquisition_devices.update({device_name_holder.value: default_config})
        bc.add_device(default_config, meas_settings.scan_devices)
    
    ui.notify(f'{device_name_holder.value} has been added to the devices.',
            position = 'top',
            type='positive')
    
    update_devices_card()
    return

def remove_device_button(click_event):

    device_cat = click_event.sender.text
    
    if 'Scan' in device_cat:
        devices_catagory_holder.value = 'Scan Devices'
        device_list = gui_configs_holder.value.scan_devices
    else:
        devices_catagory_holder.value = 'Acquisition  Devices'
        device_list = gui_configs_holder.value.acquisition_devices
    
    def del_dev():
        del device_list[selected_device.value]
        update_devices_card()
    with ui.dialog() as dialog, ui.card():
        devices = list(device_list.keys())
        selected_device = ui.select(devices, 
                                    label='Choose Device to remove').classes('w-96')
        with ui.row():
            ui.button('Cancel', on_click=(dialog.close)).props('outline')
            ui.button('Remove Device', on_click=(del_dev, dialog.close))

    dialog.open()
    return

def show_devices(meas_settings:bc.Measurement_Settings):
    if devices_catagory_holder.value == 'Scan Devices':
        device_list = gui_configs_holder.value.scan_devices
    else: 
        device_list = gui_configs_holder.value.acquisition_devices
    with ui.column().classes('w-full'):
        for name, parameters in device_list.items():
            with ui.expansion(f'{name} ({parameters["device"]})').classes('w-full text-center'):
                device_tabs(name, parameters, meas_settings)
    return

def device_tabs(device_name:str,
                device_parameters:dict,
                meas_settings:bc.Measurement_Settings):
    ## device_parameters are: parameters, latent_parameters, etc.
    with ui.tabs() as tabs:
        for (param_name, entry) in list(device_parameters.items()):
            if isinstance(entry, dict):
                ui.tab(param_name)

    with ui.tab_panels(tabs, value='parameters'):
        for (param_name, entry) in list(device_parameters.items()):
            if isinstance(entry, dict):
                with ui.tab_panel(param_name):
                    list_parameters(device_name, 
                                    device_parameters[param_name], 
                                    meas_settings)
    return

def list_parameters(device_name:str,
                    parameters: dict,
                    meas_settings:bc.Measurement_Settings):
    with ui.column().classes('w-full'):
        with ui.row().classes('w-full no-wrap'):
            ui.button('Save Device').classes('w-full')
            ui.button('Reconnect').classes('w-full')
       
        with ui.row().classes('w-full no-wrap items-center bg-secondary'):
            ui.label('Output:')
            ui.radio({1:'On', 0:'Off'}, 
                     value=1, 
                     on_change = lambda e: device_output(
                            e.value, device_name, meas_settings
                            )).props('inline')
        
        for (param_name, value) in list(parameters.items()):
            with ui.row().classes('w-full no-wrap items-center bg-secondary'):
                p_label = ui.label(param_name).classes('w-full justify-right')
                ui.input(label = param_name,
                         value = value, 
                         on_change=lambda e: \
                            update_parameter(e.value, e.sender._props['label'], 
                                             device_name, meas_settings)
                         )
    return

def device_output(value:int, device_name:str,
                  meas_settings:bc.Measurement_Settings):

    if device_name in meas_settings.scan_devices:
        device = meas_settings.scan_devices[device_name]
    elif device_name in meas_settings.acquisition_devices:
        device = meas_settings.scan_devices[device_name]
    else:
        pass ## put logging here
    device.output(value)
    return

def update_parameter(value:Any,
                     parameter:str,
                     device_name:str,
                     meas_settings:bc.Measurement_Settings):
    if device_name in meas_settings.scan_devices:
        device = meas_settings.scan_devices[device_name]
    elif device_name in meas_settings.acquisition_devices:
        device = meas_settings.scan_devices[device_name]
    else:
        pass ## put logging here
        
    device.write(parameter, value)
    return

def available_devices()->list:
    device_path = bc.Devices_directory
    contents = os.listdir(device_path)
    devices = [content for content in contents if os.path.isdir(device_path+'\\'+content)]
    return devices

if __name__ in {"__main__", "__mp_main__"}:
    gui_config = gui_utils.load_gui_config("C:\\Users\\walsworth1\\Documents\\Jupyter_Notebooks\\baecon\\tests\\test_measurement_settings.toml")
    
    
    main(gui_config, "Scan Devices")
    ui.run(port=8082)