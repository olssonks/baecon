from nicegui import app, ui

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

head_style = "color: #37474f; font-size: 200%; font-weight: 300"

ui.colors(primary="#485696", secondary="#E7E7E7", accent="#FC7A1E", positive="#53B689")


## "Globals"
## gui_fields: All the main fields in the GUI for file names, plot
## meas_settings: actual measurement configuration with has instrument objects
##     in it for communication
## meas_data: measurement data

meas_settings = bc.Measurement_Settings()

gui_fields = gui_utils.GUI_fields()

meas_data = bc.Measurement_Data()

card_dict = {}


def main():
    """Main GUI for :py:mod:`baecon`.

    Includes sections (i.e., :py:mod:`nicegui.ui.cards`) for the following:

    * Data format and saving
    * Loading, configuring, and controlling acquisition and scan devices
    * Loading the measurement engine
    * Saving and loading the experiment
    * Plotting the data generated from the engine
    * Editable table of the scan settings/schedule

    """
    with ui.card().style("background-color: #E7E7E7").classes("h-full"):
        with ui.row().classes("no-wrap items-stretch w-full"):
            with ui.card().classes("w-2/3"):
                experiment_card.main(gui_fields, meas_settings)
            with ui.card().classes("w-1/3"):
                engine_card.main(gui_fields, meas_settings, meas_data)
        with ui.row().classes("flex items-stretch"):
            with ui.column().classes("grid justify-items-stretch"):
                ## Scan devices card
                with ui.card().classes("w-96  h-full"):
                    ## possible card props: .props('flat bordered')
                    refresh, extra_args = devices_card.main(
                        gui_fields, meas_settings, "Scan Devices"
                    )
                    card_dict.update(
                        {"card_scan_dev": {"function": refresh, "args": extra_args}}
                    )
                ## Acquisition devices card
                with ui.card().classes("w-96  h-full"):
                    refresh, extra_args = devices_card.main(
                        gui_fields, meas_settings, "Acquisition Devices"
                    )
                    card_dict.update(
                        {"card_acq_dev": {"function": refresh, "args": extra_args}}
                    )
                with ui.card().classes("w-full h-full place-content-evenly"):
                    data_card.main(gui_fields, meas_data)
            with ui.column().classes("h-full"):
                with ui.card().classes("w-full"):
                    plot_card.main(gui_fields, meas_settings, meas_data)
                with ui.card():
                    refresh, extra_args = scan_card.main(
                        gui_fields, meas_settings, meas_data
                    )
                    card_dict.update(
                        {"card_scan": {"function": refresh, "args": extra_args}}
                    )
    gui_utils.set_gui_cards(card_dict)
    gui_utils.update_everything(gui_fields, meas_settings)


async def run_main():
    main()
    app.on_disconnect(app.shutdown)
    # ui.run(port=gui_utils.GUI_PORT, reload=False)
    ui.run(port=8666, reload=False)
    return


if __name__ in {"__main__", "__mp_main__"}:
    ## Try different port if usual one is blocked
    ## This usually occurs if GUI page, other than main one, uses ui.run()
    # for _ in range(10):
    #     try:
    #         main()
    #         app.on_disconnect(app.shutdown)
    #         ui.run(port=gui_utils.GUI_PORT, reload=False)
    #     except PermissionError:
    #         gui_utils.GUI_PORT += 1
    #         time.sleep(0.1)
    #     else:
    #         break
    main()
    app.on_disconnect(app.shutdown)
    # ui.run(port=gui_utils.GUI_PORT, reload=False)
    ui.run(port=8666, reload=False)
