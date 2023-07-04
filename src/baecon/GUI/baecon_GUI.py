from nicegui import ui

import baecon as bc
from baecon.GUI import gui_utils
from baecon.GUI.cards import (
    data_card,
    devices_card,
    engine_card,
    experiment_card,
    plot_card,
    scan_card,
)

## should be working with this, but if baecon cannot be found uncomment this
# sys.path.insert(0,'C:\\Users\\walsworth1\\Documents\\Jupyter_Notebooks\\baecon')

head_style = "color: #37474f; font-size: 200%; font-weight: 300"

ui.colors(primary="#485696", secondary="#E7E7E7", accent="#FC7A1E", positive="#53B689")


## "Globals"
## gui_fields: All the main fields in the GUI for file names, plot
## meas_settings: actual measurement configuration with has instrument objects in it for communication
## meas_data: measurement data

meas_config = bc.utils.load_config(
    "C:\\Users\\walsworth1\\Documents\\Jupyter_Notebooks\\baecon\\tests\\generated_config.toml"
)

meas_settings = bc.make_measurement_settings(meas_config)

gui_fields = gui_utils.GUI_fields()

meas_data = bc.Measurement_Data()

with ui.card().style("background-color: #E7E7E7").classes("h-full"):
    with ui.row().classes("no-wrap items-stretch w-full"):
        with ui.card().classes("w-2/3") as exp_card:
            experiment_card.main(gui_fields, meas_settings)
        with ui.card().classes("w-1/3") as eng_card:
            engine_card.main(gui_fields, meas_settings, meas_data)
    with ui.row().classes("flex items-stretch"):
        with ui.column().classes("grid justify-items-stretch"):
            ## Scan devices card
            with ui.card().classes("w-96  h-full") as scan_dev_card:
                ## possible card props: .props('flat bordered')
                devices_card.main(gui_fields, meas_settings, "Scan Devices")
            ## Acquisition devices card
            with ui.card().classes("w-96  h-full") as acq_dev_card:
                devices_card.main(gui_fields, meas_settings, "Acquisition Devices")
                acq_dev_card.__setattr__("name", "card_acq_dev")
            with ui.card().classes("w-full h-full place-content-evenly") as card_for_data:
                data_card.main(gui_fields, meas_data)
        with ui.column().classes("h-full"):
            with ui.card().classes("w-full") as card_for_plot:
                plot_card.main(gui_fields, meas_settings, meas_data)
            with ui.card() as card_for_scan:
                scan_card.main(gui_fields, meas_settings, meas_data)

# app.on_disconnect(app.shutdown)
ui.run(port=8666)
