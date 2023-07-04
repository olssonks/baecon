from functools import partial
from pathlib import Path

from nicegui import ui

import baecon as bc
from baecon.GUI import gui_utils
from baecon.GUI.cards import data_card

## should be working with this, but if baecon cannot be found uncomment this
# sys.path.insert(0,"C:\\Users\\walsworth1\\Documents\\Jupyter_Notebooks\\baecon")

head_style = "color: #37474f; font-size: 200%; font-weight: 300"


def main(gui_fields: gui_utils.GUI_fields, meas_settings: bc.Measurement_Settings):
    with ui.row().classes("no-wrap items-center"):
        ui.label("Experiment:").style(head_style)
        ## needed lambda function here, or update_file_name would not run on change
        ui.input(
            placeholder="Experiment Name",
            on_change=lambda: data_card.update_file_name(gui_fields),
        ).bind_value(gui_fields, "exp_name")
    with ui.row().classes("w-full no-wrap items-end"):
        ui.input("Experiment File").bind_value(gui_fields, "exp_file").classes("w-2/3")
        ui.button("Save", on_click=partial(save_exp_file, *(gui_fields, meas_settings))).classes("w-1/9")
        ui.button(
            "Save as", on_click=partial(save_as_exp_file, *(gui_fields, meas_settings))
        ).classes("w-1/9")
        ui.button("Load", on_click=partial(load_exp_file, *(gui_fields, meas_settings))).classes("w-1/9")
    return

def make_experiment_config(gui_fields: gui_utils.GUI_fields, meas_settings: bc.Measurement_Settings):
    exp_config = {}
    exp_config.update(bc.generate_measurement_config(meas_settings))
    engine_config = {"engine":{"name":gui_fields.engine_name, "file":gui_fields.engine_file}}
    exp_config.update(engine_config)
    exp_config.update({"GUI_Fields": gui_utils.to_gui_fields_config(gui_fields)})
    ## data???
    return exp_config

async def load_exp_file(
    gui_fields: gui_utils.GUI_fields, meas_settings: bc.Measurement_Settings
):
    exp_file = await gui_utils.pick_file()
    exp_config = bc.utils.load_config(exp_file)
    gui_utils.from_gui_fields_config(exp_config, gui_fields)
    bc.make_measurement_settings(exp_config)
    return


async def save_exp_file(
    gui_fields: gui_utils.GUI_fields, meas_settings: bc.Measurement_Settings
):
    config = make_experiment_config(gui_fields, meas_settings)
    bc.utils.dump_config(config, gui_fields.exp_file)
    return


async def save_as_exp_file(
    gui_fields: gui_utils.GUI_fields, meas_settings: bc.Measurement_Settings
):
    new_file = Path(await gui_utils.pick_file())
    gui_fields.exp_file = str(new_file)
    gui_fields.exp_name = new_file.name.split(".")[0]
    config = make_experiment_config(gui_fields, meas_settings)
    bc.utils.dump_config(config, new_file)
    return


if __name__ in {"__main__", "__mp_main__"}:
    gui_config = gui_utils.load_gui_config(
        "C:\\Users\\walsworth1\\Documents\\Jupyter_Notebooks\\baecon\\tests\\test_measurement_settings.toml"
    )

    main(gui_config)
    ui.run(port=8082)
