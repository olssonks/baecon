import copy
from dataclasses import dataclass
from functools import partial

from nicegui import ui

import baecon as bc
from baecon.GUI import gui_utils


@dataclass
class abort:
    """Used to stop all threads with keyboard input ``'abort'``."""

    flag = False


engine_holder = gui_utils.Holder()

nicegui_element_holder = gui_utils.Holder()


def main(
    gui_fields: gui_utils.GUI_fields,
    meas_settings: bc.Measurement_Settings,
    meas_data: bc.Measurement_Data,
):
    def trigger_abort():
        gui_fields.abort_measurement = True
        print("Measurement aborted.")

    with ui.column().classes("justify-start items-stretch h-full w-full no-wrap") as cols:
        nicegui_element_holder.update(cols)
        with ui.row().classes("no-wrap items-end h-full"):
            ui.button("Load", on_click=partial(load_engine_button, gui_fields)).classes(
                "w-1/4"
            )
            ui.input(label="engine", placeholder="select engine").classes(
                "w-3/4 h-full"
            ).bind_value(gui_fields, "engine_name").props(
                'type=textarea autogrow rounded outlined'
            )
        with ui.row().classes("no-wrap items-end h-full"):

            def turn_on_plot():
                gui_fields.plot_active = True

            run_button = ui.button(
                "Run",
                on_click=partial(run_measurement, *(gui_fields, meas_settings, meas_data)),
            ).classes("w-3/4")
            run_button.on("click", turn_on_plot)
            ui.button("Abort", on_click=trigger_abort).classes("1/4")

    return


async def load_engine_button(gui_fields: gui_utils.GUI_fields):
    file = await gui_utils.pick_file(gui_utils.ENGINE_DIRECTORY)
    load_engine(file, gui_fields)
    return


def load_engine(file: str, gui_fields: gui_utils.GUI_fields):
    engine_module = bc.utils.load_module_from_path(file)
    engine_holder.update(engine_module)
    gui_fields.engine_file = file
    gui_fields.engine_name = gui_utils.name_from_path(file)
    return


def abort_measurement(gui_fields: gui_utils.GUI_fields) -> None:
    gui_fields.__setattr__("abort_measurement", True)
    return


async def run_measurement(
    gui_fields: gui_utils.GUI_fields,
    meas_settings: bc.Measurement_Settings,
    meas_data: bc.Measurement_Data,
):
    ## need to update any measurement settings from the GUI_fields
    meas_data.data_template = bc.create_data_template(meas_settings)
    meas_data.assign_measurement_settings(meas_settings)
    meas_data.data_current_scan = copy.deepcopy(meas_data.data_template)

    task = await engine_holder.value.main(meas_settings, meas_data, gui_fields)

    # gui_fields.plot_active = True

    # baecon_cards = gui_utils.get_card_elements(nicegui_element_holder)
    # plot_card = [el for el in baecon_cards if el.name == 'card_plot'][0]

    # plot_card.update()

    while not task.done():
        gui_fields.plot_active = True
    else:
        gui_fields.plot_active = False
    # ui.update(plot_card)
    return


if __name__ in {"__main__", "__mp_main__"}:
    gui_fields = gui_utils.GUI_fields()

    main(gui_fields, [], [])

    ui.run(port=8082)
