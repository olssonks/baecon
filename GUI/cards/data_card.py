from nicegui import ui

from dataclasses import dataclass, field
from datetime import datetime
import sys
sys.path.insert(0,'C:\\Users\\walsworth1\\Documents\\Jupyter_Notebooks\\baecon')

from GUI import gui_utils
import baecon as bc

head_style = 'color: #37474f; font-size: 200%; font-weight: 300'

## GUI fields just for the data_card
## useful for debugging data_card.main()
@dataclass
class GUI_fields:
    """The GUI objects can be bound to these attributes, eliminating the need
       to pass values between differet cards.
    """
    #plot              : nicegui.elements.plotly.Plotly
    exp_name          : str
    #exp_file          : str
    #engine_file       : str
    #scan_file         : str
    #instrument_file   : dict
    data_auto_save    : bool
    data_folder       : str
    data_file         : str
    data_file_format  : str
    data_analysis     : str ### Probably a seperate Window
    #plot_active       : bool
    #abort_measurement : bool


def main(gui_config: gui_utils.GUI_Measurement_Configuration, 
         gui_fields: gui_utils.GUI_fields,
         meas_data):
    date_prefix = gui_utils.holder(datetime.today().strftime("%Y%m%d"))
    meas_number = gui_utils.holder('0')
    full_save_name = gui_utils.holder(('_'.join([date_prefix.value, meas_number.value, 
                                                gui_fields.exp_name])
                                      +gui_fields.data_file_format))
    with ui.column():
        with ui.row():
            ui.label('Data').style(head_style)
            ui.checkbox('Auto Save').bind_value(gui_fields, 'data_auto_save')
        with ui.row():
            ui.label('File: ')
            ui.label().bind_text(full_save_name, 'value')
            
    with ui.expansion('Save Info').classes('w-full'):
        with ui.row().classes('w-full no-wrap items-center'):
            ui.button('Pick:', on_click=pick_data_folder).classes('text-left')
            ui.input(placeholder='Data Location').bind_value(gui_fields, 'data_folder')
        
        with ui.column():
            with ui.row():
                ui.label('Date Prefix: ')
                ui.label().bind_text(date_prefix, 'value')
                ui.label('Meas. Number: ')
                ui.label().bind_text(meas_number, 'value')
            
            with ui.row().classes('w-full no-wrap items-center'):
                ui.input(placeholder='Data File Name', 
                        on_change= lambda e: update_file_name(e.value, full_save_name, date_prefix, meas_number, gui_fields))\
                        .classes('w-full').bind_value(gui_fields, "data_file")
        
        with ui.row().classes('w-full no-wrap items-center'):
            ui.label('Data Format:')
            ui.radio(['.zarr', '.nc', '.csv'], value='.zarr', 
                    on_change=lambda e: update_file_format(e.value, gui_fields))\
                    .props('inline').bind_value(gui_fields, "data_file_format")
        
        with ui.row():
            ui.button('Save')
            ui.button('Save as:', 
                    on_click=save_as_button(gui_fields, date_prefix, meas_number))\
                    .classes('text-left')
        
        with ui.row().classes('w-full no-wrap items-center'):
            ui.input('analysis method').classes('w-full')
            ui.button('Load')

        
#### end main ####    
    return

async def pick_file():
    result = await gui_utils.load_file('.')
    return result
    
async def pick_data_folder(gui_fields):
    result = await gui_utils.load_file('.')
    gui_fields.data_folder = result
    return

async def save_as_button(gui_fields, 
                         data_prefix, meas_number):
    if gui_fields.data_file in ['Data File Name', '']:
        file = await pick_file()
        if file:
            gui_fields.data_file = date_prefix.value + file
            gui_fields.data_file_format = '.' + file.split('.')[-1]

    # bc.utils.save_baecon_data(meas_data,
    #                             gui_fields.data_file, 
    #                             format=gui_fields.data_file_format) 
    return

def update_file_name(new_name, full_save_name, date_prefix, meas_number, gui_fields):
    full_save_name.update(
        '_'.join([date_prefix.value, 
                  meas_number.value, 
                  new_name])
        + gui_fields.data_file_format
        )
    return

def update_file_format(new_format, gui_fields):
    gui_fields.data_file_format = new_format
    if '.' in gui_fields.data_file:
        strip_format = '.'.join(gui_fields.data_file.split('.')[:-1])
        gui_fields.data_file = strip_format + new_format
    else:
        gui_fields.data_file = gui_fields.data_file + new_format
    return


if __name__ in {"__main__", "__mp_main__"}:
    gui_config = gui_utils.load_gui_config("C:\\Users\\walsworth1\\Documents\\Jupyter_Notebooks\\baecon\\tests\\test_measurement_settings.toml")
    gui_fields = GUI_fields()
    main(gui_config, gui_fields, {})
    ui.run(port=8082)

## automatic file name generator
## "101_exp-name_date-time.zarr"
## "date-time_exp-name.zarr"