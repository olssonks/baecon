from nicegui import ui

import sys
sys.path.insert(0,'C:\\Users\\walsworth1\\Documents\\Jupyter_Notebooks\\baecon')

import gui_utils
import baecon as bc

head_style = 'color: #37474f; font-size: 200%; font-weight: 300'

def main(gui_config:gui_utils.GUI_Measurement_Configuration):
    ui.label('Data').style(head_style)
    with ui.row().classes('w-full no-wrap items-center'):
        ui.input('analysis method').classes('w-full')
        ui.button('Load')
    with ui.row().classes('w-full no-wrap items-center'):
        ui.button('Save as:').classes('text-left')
        ui.input(placeholder='Data File Name').classes('w-full')
    with ui.row().classes('w-full no-wrap items-center'):
        ui.label('Data Format:')
        ui.radio(['.zarr', '.nc', '.csv'], value='.zarr').props('inline')
    return
    
if __name__ in {"__main__", "__mp_main__"}:
    gui_config = gui_utils.load_gui_config("C:\\Users\\walsworth1\\Documents\\Jupyter_Notebooks\\baecon\\tests\\test_measurement_settings.toml")

    main(gui_config)
    ui.run(port=8082)
