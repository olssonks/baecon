from nicegui import ui

import sys
import copy
import asyncio
sys.path.insert(0,'C:\\Users\\walsworth1\\Documents\\Jupyter_Notebooks\\baecon')
from functools import partial
from dataclasses import dataclass, field


import gui_utils
import baecon as bc

@dataclass
class abort:
    """Used to stop all threads with keyboard input ``'abort'``.
    
    """   
    flag = False

engine_holder = gui_utils.holder()

def main(gui_fields:gui_utils.GUI_fields, 
         meas_settings:bc.Measurement_Settings,
         meas_data:bc.Measurement_Data):
    
    def trigger_abort():
        gui_fields.abort_measurement = True
        print('Measurement aborted.')
        
    with ui.column().classes('w-full h-full items-end'):
        with ui.row().classes('w-full h-full items-end no-wrap'):
            ui.button('Load', on_click=partial(load_engine, gui_fields))\
            .classes('w-1/4 h-full')
            ui.input(label='engine', placeholder='select engine')\
            .classes('w-3/4 h-full').bind_value(gui_fields, 'engine_file')
        with ui.row().classes('w-full h-full items-end no-wrap'):
            ui.button('Run', on_click=partial(run_measurement,
                                              *(gui_fields, 
                                               meas_settings, 
                                               meas_data))
                      ).classes('w-2/3 h-full')
            ui.button('Abort', on_click=trigger_abort)\
            .classes('w-1/3 h-full')

    return
    
    
async def pick_file():
    result = await gui_utils.load_file('.')
    return result

async def load_engine(gui_fields:gui_utils.GUI_fields):
    file = await pick_file()
    engine_module = bc.utils.load_module_from_path(file)
    engine_holder.update(engine_module)
    engine_file = gui_utils.name_from_path(file)
    gui_fields.engine_file = engine_file
    return

def abort_measurement(gui_fields:gui_utils.GUI_fields)->None:
    gui_fields.__setattr__('abort_measurement', True)
    return

async def run_measurement(gui_fields:gui_utils.GUI_fields,
                          meas_settings:bc.Measurement_Settings,
                          meas_data:bc.Measurement_Data):
    
    meas_data.data_template = bc.create_data_template(meas_settings)
    meas_data.assign_measurement_settings(meas_settings)
    meas_data.data_current_scan = copy.deepcopy(meas_data.data_template)
    
    task = await engine_holder.value.main(meas_settings, 
                                          meas_data,
                                          gui_fields)
    
    gui_fields.plot_active = True
    while not task.done():
        gui_fields.plot_active = True
    else:
        gui_fields.plot_active = False
    
    return

if __name__ in {"__main__", "__mp_main__"}:
    main()
    
    ui.run(port=8082)