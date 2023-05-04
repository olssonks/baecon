from nicegui import ui

import sys
sys.path.insert(0,'C:\\Users\\walsworth1\\Documents\\Jupyter_Notebooks\\baecon')

import gui_utils
import baecon as bc

#test_measurement = bc.make_measurement_settings(bc.utils.load_config("C:\\Users\\walsworth1\\Documents\\Jupyter_Notebooks\\baecon\\tests\\test_measurement_settings.toml"))

scan_settings = bc.define_scan_settings()

## name of the device is displayed intstead of device type
scan_headers = {
        'name':'Device', 'parameter': 'Parameter',
        'minimum': 'Min', 'maximum': 'Max', 'points': 'Points',
        'repetitions': 'Repetitions', 'scale': 'Scale', 'randomize': 'Randomize',
        'note': 'Note'
        }

header_widths = [300, 300, 150, 150, 150, 300, 300, 300, 300]
card_width = '1000px'

## the async functions do not work with args inside lambda functions
## these holder variables are to get around this and let async functions
## access different variables
gui_config_holder = gui_utils.holder()

file_holder = gui_utils.holder()
scan_name = gui_utils.holder('pick a file')

scan_table_holder = gui_utils.holder()
table_args_holder = gui_utils.holder()

head_style = 'color: #37474f; font-size: 200%; font-weight: 300'

def main(gui_config:gui_utils.GUI_Measurement_Configuration):
    gui_config_holder.update(gui_config)
    with ui.column().classes('w-full'):
        ui.label('Measurment Scans').style(head_style)
        save_load(gui_config.scan_collection)
        with ui.row().style(f'width: {card_width}').classes('no-wrap'):
            primary_buttons(gui_config_holder.value)
            table_args_holder.value = scan_table_args(gui_config_holder.value)
            scan_table_holder.value = ui.aggrid({'rowSelection': 'single'}).classes('w-full')
            update_table()
    return


def save_load(scan_collection:dict):
    with ui.row().style(f'width: {card_width}').classes('no-wrap items-center'):
        ui.input(label = 'Scan Collection Name',
                 placeholder='pick file').bind_value(scan_name, 'value').classes('w-full relative-right text-right')
        ui.button('Save', on_click=save_collection)
        ui.button('Load', on_click=load_collection)
    return
    
async def pick_file():
    result = await gui_utils.load_file('.')
    return result
async def save_collection():
    file = await pick_file()
    if file:
        file_holder.value = file
        scan_name.value = name_from_file(file)
    return 
async def load_collection():
    file = await pick_file()
    if file:
        file_holder.value = file
        scan_name.value = name_from_file(file)
    return
def name_from_file(file:str):
    name = file.split('\\')[-1]
    return name


def primary_buttons(gui_config:gui_utils.GUI_Measurement_Configuration):
    with ui.column():
        ui.number('Averages')
        ui.button('Add', on_click=lambda: add_scan_dialog(gui_config)).classes('w-full')
        ui.button('Remove', on_click=remove_device).classes('w-full')
    return

def update_table():
    scan_table_holder.value.options['columnDefs'] = table_args_holder.value['columnDefs']
    scan_table_holder.value.options['rowData'] = table_args_holder.value['rowData']
    scan_table_holder.value.update()
    return
    
def scan_table_args(gui_config:gui_utils.GUI_Measurement_Configuration):
    scans = gui_config.scan_collection
    columnDefs = []; rowData = []
    
    for idx, key in enumerate(scan_headers.keys()):
        columnDefs.append({'headerName': f'{scan_headers[key]}', 'field': f'{key}', 
                           'editable':True, 'resizable': True, 
                           'suppressSizeToFit': False,
                           'initialWidth': header_widths[idx]})
    for key in scans.keys():
        row = {}
        for setting in scan_headers.keys():
            row.update({f'{setting}': scans[key][setting]})
        rowData.append(row)

    return {'columnDefs': columnDefs, 'rowData': rowData}

def add_scan_dialog(gui_config:gui_utils.GUI_Measurement_Configuration):
    scan_settings_holder = gui_utils.holder()
    def update_scan_collection():
        new_settings = scan_settings_holder.value
        scan_key = f'{new_settings["name"]}-{new_settings["parameter"]}'
        gui_config_holder.value.scan_collection.update({scan_key: new_settings})
        table_args_holder.value = scan_table_args(gui_config_holder.value)
        return
    
    with ui.dialog() as dialog, ui.card():
        with ui.column().classes('w-full'):
            ui.label('Scan Settings').classes('text-h3')
            scan_settings_holder.value = choose_device_and_paramters(gui_config_holder.value)
            choose_settings(scan_settings_holder.value)
            make_button = ui.button("Make Scan", on_click=update_scan_collection)
            make_button.on('click', dialog.close)
            make_button.on('click', update_table)
    dialog.open()
    return
    
def choose_device_and_paramters(gui_config:gui_utils.GUI_Measurement_Configuration):
    selected_settings = scan_settings.copy()
    
    device_select = ui.select(list(gui_config.scan_devices.keys()), 
                            label='Device Name',
                            on_change = \
                            lambda e: (selected_settings.update({'name': e.value}), 
                                       param_update(e.value)) 
                            ).classes('w-full')
    param_select = ui.select(['choose device'], label='parameter',
                             on_change = \
                             lambda e: selected_settings.update({'parameter':e.value})).classes('w-full')
    
    def param_update(selected_device):
        param_select.options = list(gui_config.scan_devices\
                                    [selected_device]['parameters'].keys())
        param_select.update()
    return selected_settings
        
def choose_settings(selected_settings):
    remaining_keys = [key for key in list(scan_settings.keys()) 
                      if not (key=='name' or key=='parameter' or key=='device')]
    for scan_key in remaining_keys:
        with ui.row().classes('w-full'):
            if (isinstance(scan_settings[scan_key], str) 
                and not scan_key=='scale'
                and not scan_key =='randomize'):
                ui.input(scan_key, value=scan_settings[scan_key],
                        on_change = lambda e: selected_settings.update({scan_key:e.value})).classes('w-full')
            elif scan_key == 'points':
                get_points(selected_settings, scan_key)
            elif scan_key=='scale':
                ui.select(['linear', 'log', 'custom', 'constant'],
                          label='scale',
                          value='linear').classes('w-full')
            elif scan_key=='randomize':
                ui.select([True, False],
                          label='randomize',
                          value=False).classes('w-full')
            else:
                ui.number(scan_key, on_change = \
                          lambda e: selected_settings.update({scan_key:e.value})).classes('w-full')
                
    return selected_settings

def get_points(scan_settings, scan_key):
    def steps_to_points(scan_settings, input, stepsize_or_points):
        if stepsize_or_points.value == 'step size':
            span = scan_settings['maximum'] - scan_settings['minimum']
            points = round(span/input, 2)
            scan_settings.update({'points': points})
        else:
            scan_settings.update({'points': input})
        return
    
    ui.number(scan_key, value=scan_settings[scan_key],
            on_change = lambda e: steps_to_points(scan_settings, 
                                                    e.value,
                                                    stepsize_or_points))
    stepsize_or_points = ui.radio(['points', 'step size'], 
                                    value='points')
    return


async def remove_device():
    row = await scan_table_holder.value.get_selected_row()
    name = f'{row["name"]}-{row["parameter"]}'
    del gui_config_holder.value.scan_collection[name]
    table_args_holder.value = scan_table_args(gui_config_holder.value)
    update_table()
    return


if __name__ in {"__main__", "__mp_main__"}:
    gui_config = gui_utils.load_gui_config("C:\\Users\\walsworth1\\Documents\\Jupyter_Notebooks\\baecon\\tests\\test_measurement_settings.toml")

    with ui.card():
        main(gui_config)
    
    ui.run(port=8082)