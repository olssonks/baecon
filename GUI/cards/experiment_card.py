from nicegui import ui

from functools import partial

import sys
sys.path.insert(0,'C:\\Users\\walsworth1\\Documents\\Jupyter_Notebooks\\baecon')

import gui_utils
import GUI.cards.data_card as data_card
import baecon as bc

head_style = 'color: #37474f; font-size: 200%; font-weight: 300'

def main(gui_fields:gui_utils.GUI_fields, 
         meas_settings:bc.Measurement_Settings):
    with ui.row().classes('no-wrap items-center'):
        ui.label('Experiment:').style(head_style)
        ## needed lambda function here, or update_file_name would not run on change
        ui.input(placeholder='Experiment Name', 
                 on_change=lambda e: data_card.update_file_name(gui_fields))\
        .bind_value(gui_fields, "exp_name")
    with ui.row().classes('w-full no-wrap items-center'):
        ui.input('Experiment File').bind_value(gui_fields, "exp_file").classes('w-full')
        ui.button('Save', on_click=partial(save_exp_file, 
                                           *(gui_fields, meas_settings)))
        ui.button('Load', on_click=partial(load_exp_file, 
                                           *(gui_fields, meas_settings)))
    return

async def pick_file():
    result = await gui_utils.load_file('.')
    return result

async def load_exp_file(gui_fields:gui_utils.GUI_fields, 
                        meas_settings:bc.Measurement_Settings):
    exp_file = await pick_file()
    gui_fields.exp_file = exp_file
    gui_config = bc.utils.load_config(exp_file)
    meas_settings = bc.make_measurement_settings(gui_config)
    return
    
async def save_exp_file(gui_fields:gui_utils.GUI_fields, 
                        meas_settings:bc.Measurement_Settings):
    config = bc.generate_measurement_config(meas_settings)
    bc.utils.dump_config(config, gui_fields.exp_file)
    return

if __name__ in {"__main__", "__mp_main__"}:
    gui_config = gui_utils.load_gui_config("C:\\Users\\walsworth1\\Documents\\Jupyter_Notebooks\\baecon\\tests\\test_measurement_settings.toml")

    main(gui_config)
    ui.run(port=8082)