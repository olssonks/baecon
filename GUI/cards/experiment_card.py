from nicegui import ui

import sys
sys.path.insert(0,'C:\\Users\\walsworth1\\Documents\\Jupyter_Notebooks\\baecon')

import gui_utils
import baecon as bc

exp_file_name = gui_utils.holder()

head_style = 'color: #37474f; font-size: 200%; font-weight: 300'

def main(gui_config:gui_utils.GUI_Measurement_Configuration):
    ui.label('Experiment').style(head_style)
    with ui.row().classes('w-full no-wrap items-center'):
        ui.input('Experiment File').bind_value(exp_file_name, 'value').classes('w-full')
        ui.button('Save', on_click=save_exp_file)
        ui.button('Load', on_click=load_exp_file)
    return

async def pick_file():
    result = await gui_utils.load_file('.')
    return result

async def load_exp_file():
    exp_file = await pick_file()
    exp_file_name.update(exp_file)
    gui_config = bc.utils.load_config(exp_file)
    return
    
async def save_exp_file():
    config = gui_config.__dict__
    bc.utils.dump_config(config, exp_file_name.value)
    return

if __name__ in {"__main__", "__mp_main__"}:
    gui_config = gui_utils.load_gui_config("C:\\Users\\walsworth1\\Documents\\Jupyter_Notebooks\\baecon\\tests\\test_measurement_settings.toml")

    main(gui_config)
    ui.run(port=8082)