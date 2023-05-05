from nicegui import ui

import sys
sys.path.insert(0,'C:\\Users\\walsworth1\\Documents\\Jupyter_Notebooks\\baecon')

import gui_utils
import baecon as bc

def main():
    with ui.column().classes('w-full h-full items-end'):
        with ui.row().classes('w-full h-full items-end'):
            ui.button('Load')
            ui.input(label='engine')
        with ui.row().classes('w-full h-full items-end'):
            ui.button('Run')
            ui.button('Stop')

    return
    
if __name__ in {"__main__", "__mp_main__"}:
    main()
    
    ui.run(port=8082)