from nicegui import ui, app

import sys
sys.path.insert(0,'C:\\Users\\walsworth1\\Documents\\Jupyter_Notebooks\\baecon')
import baecon as bc


import gui_utils
from cards import *

head_style = 'color: #37474f; font-size: 200%; font-weight: 300'

ui.colors(primary='#485696', secondary='#E7E7E7', accent='#FC7A1E', positive='#53B689')

## "Globals"
## gui_config: GUI measurement configuration that is saved/loaded to define experiment, actually may not need this
## gui_fields: All the main fields in the GUI for file names, plot
## meas_settings: actual measurement configuration with has instrument objects in it for communication
## meas_data: measurement data

gui_config = gui_utils.load_gui_config("C:\\Users\\walsworth1\\Documents\\Jupyter_Notebooks\\baecon\\tests\\test_measurement_settings.toml")

meas_config = bc.utils.load_config('C:\\Users\\walsworth1\\Documents\\Jupyter_Notebooks\\baecon\\tests\\generated_config.toml')

meas_settings = bc.make_measurement_settings(meas_config)

gui_fields = gui_utils.GUI_fields()

meas_data = bc.Measurement_Data()

with ui.card().style('background-color: #E7E7E7'):
    with ui.row().classes('w-full h-full no-wrap items-end'):
        with ui.card().classes('w-2/3 h-full'):
            experiment_card.main(gui_config)
        with ui.card().classes('w-1/3 h-full'):
            engine_card.main()
    with ui.row().classes('flex items-stretch'):
        with ui.column().classes('grid justify-items-stretch'):
            ## Scan devices card
            with ui.card().classes('w-96  h-full'): ## possible card props: .props('flat bordered')
                devices_card.main(gui_config, meas_settings, 'Scan Devices')
            ## Acquisition devices card
            with ui.card().classes('w-96  h-full'):
                devices_card.main(gui_config, meas_settings, 'Acquisition Devices')
            ## Data Card
            with ui.card().classes('w-full h-full place-content-evenly'):
                data_card.main(gui_config, gui_fields, meas_data)
        
        with ui.column().classes('h-full'):
            ## plot card
            with ui.card().classes('w-full'):
                plot_card.main()
            with ui.card():
                scan_card.main(gui_config)
            

# app.on_disconnect(app.shutdown)
# ui.run(port=8082, reload=False)

ui.run(port=8082)

## pass gui_configs to make Measurement_Settings
## create Measurement_Data and initialize
## start measurement, data, and abort threads

## changes that need to be made to default_engine
## data need to get plotted
## either put plotting in data_thread
## or plot funtion in perform_measurement
## gui needs to use asyncio