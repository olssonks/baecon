from functools import partial
from pathlib import Path

from nicegui import app, ui

import baecon as bc
from baecon.GUI import gui_utils
from baecon.GUI.cards import data_card

head_style = "color: #37474f; font-size: 200%; font-weight: 300"


def main(gui_fields: gui_utils.GUI_fields, meas_settings: bc.Measurement_Settings) -> None:
    """Section of the GUI that saves/loads the full experiment to/from a config file.
       All of the fields, except ``plot_data``, in :py:class:`GUI_Fields` are saved
       to a dictionary like format (``.toml``, ``.yml``, or ``.json``). The plot data
       is excluded to keep the config file readable, and the actual
       :py:class:`Measurement_Data` is saved elsewhere.

    Args:
        gui_fields (gui_utils.GUI_fields): GUI fields for the current measurement.
        meas_settings (bc.Measurement_Settings): Measurement settings for the current
            measurement.
    """
    with ui.row().classes("no-wrap items-center"):
        ui.label("Experiment:").style(head_style)
        ## needed lambda function here, or update_file_name would not run on change
        ui.input(
            placeholder="Experiment Name",
            on_change=lambda: data_card.update_file_name(gui_fields),
        ).bind_value(gui_fields, "exp_name")
    with ui.row().classes("w-full no-wrap items-end"):
        ui.input("Experiment File").bind_value(gui_fields, "exp_file").classes(
            "w-2/3 h-full"
        ).props("type=textarea autogrow rounded outlined")
        ui.button(
            "Save", on_click=partial(save_exp_file, *(gui_fields, meas_settings))
        ).classes("w-1/9")
        ui.button(
            "Save as", on_click=partial(save_as_exp_file, *(gui_fields, meas_settings))
        ).classes("w-1/9")
        ui.button(
            "Load", on_click=partial(load_exp_file, *(gui_fields, meas_settings))
        ).classes("w-1/9")

    app.on_shutdown(partial(save_as_last_experiment, *(gui_fields, meas_settings)))
    return


def make_experiment_config(
    gui_fields: gui_utils.GUI_fields, meas_settings: bc.Measurement_Settings
) -> dict:
    """Generates a configuration file for describing the entire experiment.

       The file is contains dictionary elements for
       :py:class:`Measurement Settings <baecon.Measurement_Settings>` and
       :py:class:`GUI Fields <gui_utils.GUI_fields>`.

    Args:
        gui_fields (gui_utils.GUI_fields): All fields for the GUI.
        meas_settings (bc.Measurement_Settings): Settings that completely
            describe the measurement.

    Returns:
        dict: Dictionary containing all information for defining an experiment in
            the GUI.
    """
    exp_config = {}
    exp_config.update(bc.generate_measurement_config(meas_settings))
    exp_config.update({"GUI_Fields": gui_utils.to_gui_fields_config(gui_fields)})
    return exp_config


async def load_exp_file(
    gui_fields: gui_utils.GUI_fields, meas_settings: bc.Measurement_Settings
) -> None:
    """Opens dialog window for picking and loading an experiment configuration.

    Args:
        gui_fields (gui_utils.GUI_fields): All fields for the GUI.
        meas_settings (bc.Measurement_Settings): Settings that completely
            describe the measurement.
    """
    exp_file = await gui_utils.pick_file(gui_utils.EXPERIMENT_DIRECTORY)
    exp_config = bc.utils.load_config(exp_file)
    gui_utils.from_gui_fields_config(exp_config, gui_fields)
    loaded_settings = bc.make_measurement_settings(exp_config)
    for attr, params in loaded_settings.__dict__.items():
        meas_settings.__setattr__(attr, params)
    gui_utils.update_everything(gui_fields, meas_settings)
    return


async def save_exp_file(
    gui_fields: gui_utils.GUI_fields, meas_settings: bc.Measurement_Settings
) -> None:
    """Saves experiment configuration with currently chosen configuration file name.

    Args:
        gui_fields (gui_utils.GUI_fields): All fields for the GUI.
        meas_settings (bc.Measurement_Settings): Settings that completely
            describe the measurement.
    """
    config = make_experiment_config(gui_fields, meas_settings)
    bc.utils.dump_config(config, gui_fields.exp_file)
    return


async def save_as_exp_file(
    gui_fields: gui_utils.GUI_fields, meas_settings: bc.Measurement_Settings
) -> None:
    """Opens dialog window for picking file to save experiment configuration as.

    Args:
        gui_fields (gui_utils.GUI_fields): All fields for the GUI.
        meas_settings (bc.Measurement_Settings): Settings that completely
            describe the measurement.
    """
    new_file = Path(await gui_utils.pick_file(gui_utils.EXPERIMENT_DIRECTORY))
    gui_fields.exp_file = str(new_file)
    gui_fields.exp_name = new_file.name.split(".")[0]
    config = make_experiment_config(gui_fields, meas_settings)
    bc.utils.dump_config(config, new_file)
    return


async def save_as_last_experiment(
    gui_fields: gui_utils.GUI_fields, meas_settings: bc.Measurement_Settings
):
    """Save current expierment configuration in `last_config` on GUI shutdown.

    Args:
        gui_fields (gui_utils.GUI_fields): All fields for the GUI.
        meas_settings (bc.Measurement_Settings): Settings that completely
            describe the measurement.
    """
    file = gui_utils.EXPERIMENT_DIRECTORY / "last_experiment.toml"
    config = make_experiment_config(gui_fields, meas_settings)
    bc.utils.dump_config(config, file)
    return


async def load_last_experiment():
    config = make_experiment_config(gui_fields, meas_settings)
    bc.utils.dump_config(config, gui_fields.exp_file)
    return


if __name__ in {"__main__", "__mp_main__"}:
    gui_fields = gui_utils.GUI_fields()
    meas_settings = bc.Measurement_Settings()

    main(gui_fields, meas_settings)
    ui.run(port=8082)
