from dataclasses import dataclass
from functools import partial

import numpy as np
import plotly.graph_objects as go
import xarray as xr
from nicegui import ui

import baecon as bc
from baecon.GUI import gui_utils

head_style = "color: #37474f; font-size: 200%; font-weight: 300"


analyzer_holder = gui_utils.Holder()
analyzer_name_holder = gui_utils.Holder('default_analyzer')


def main(
    gui_fields: gui_utils.GUI_fields,
    meas_settings: bc.Measurement_Settings,
    meas_data: bc.Measurement_Data,
):
    def toggle_active():
        if gui_fields.plot_active:
            plot_updates.activate()
        else:
            plot_updates.deactivate()

    with ui.column().classes("w-full items-center q-gutter-lg"):
        fig = go.Figure()
        main_plot = ui.plotly(fig).classes("w-full h-full")
        with ui.row().classes("w-full justify-start"):
            ui.label("Plots").style(head_style)
            ui.button("Plot Properties")
            plot_updates = ui.timer(
                0.1, partial(plot_data, *(main_plot, meas_data, gui_fields)), active=False
            )
            ui.checkbox("Plot Active", on_change=toggle_active).bind_value(
                gui_fields, "plot_active"
            )
            ui.button(
                "Load Analysis",
                on_click=partial(load_analyzer_button, gui_fields),
            ).classes("w-1/9")
            ui.label().bind_text(analyzer_name_holder, "value")
    return


## don't really need ui vals for plot properties, plotly plots are inveractive
## this should be a tab
def props_dialog():
    with ui.dialog(), ui.card():
        with ui.column():
            with ui.row():
                ui.label("x:")
                ui.input(placeholder="min")
                ui.input(placeholder="max")
    return


async def load_analyzer_button(gui_fields: gui_utils.GUI_fields):
    analyzer_file = await gui_utils.pick_file(gui_utils.DATA_DIRECTORY / "Analysis")
    load_analyzer(analyzer_file, gui_fields)
    return


def load_analyzer(file: str, gui_fields: gui_utils.GUI_fields):
    analyzer_module = bc.utils.load_module_from_path(file)
    analyzer_holder.update(analyzer_module)
    analyzer_name_holder.update(analyzer_module.__name__)
    ##gui_fields.engine_file = file
    ##gui_fields.engine_name = gui_utils.name_from_path(file)
    return


# how to add custom color names
# test = '''<style>
# .text-brand {
#   color: #a2aa33 !important;
# }
# .bg-brand {
#   background: #a2aa33 !important;
# } </style>'''
# ui.add_head_html(test)


## engine provides plot data function for ui.timer to use
## ui.timer needs to be in the plot card or engine card
def plot_data(
    the_plot: ui.plotly, meas_data: bc.Measurement_Data, gui_fields: gui_utils.GUI_fields
) -> None:
    analyzer = analyzer_holder.value
    if analyzer is None:
        analyzer = default_analyzer
    scan_parameters: list = meas_data.raw_data_set.attrs.get("scan_parameters")
    acquisition_methods: list = meas_data.raw_data_set.attrs.get("acquire_methods")
    if (scan_parameters or acquisition_methods) is None:
        return  ## No plotting if measurement settings not defined

    fig = {
        "data": [],
        "layout": {
            "margin": {"l": 50, "r": 50, "t": 50, "b": 50},
            "plot_bgcolor": "#E5ECF6",
            "xaxis": {"title": scan_parameters[0], "gridcolor": "white"},
            "yaxis": {"gridcolor": "white"},
        },
        "config": {
            "showLink": "true",
            "plotlyServerURL": "https://chart-studio.plotly.com",
        },
    }

    (
        current_data,
        completed_data,
        average_data,
    ) = analyzer.process_data(meas_data, acquisition_methods, scan_parameters)
    if current_data is not None:
        try:
            fig = main_trace_style(fig, {**current_data, **average_data})
        except TypeError:
            pass
    if completed_data is not None:
        fig = secondary_trace_style(fig, completed_data)
    the_plot.update_figure(fig)
    if not any(thread.is_alive() for thread in gui_fields.measurement_threads):
        gui_fields.plot_active = False

    return


def process_data(
    meas_data: bc.Measurement_Data, acquire_methods: list, scan_parameters: list
) -> tuple[dict, dict, dict]:
    current_data = process_current_data(
        meas_data.data_current_scan[acquire_methods[0]], scan_parameters
    )
    completed_data = completed_processed_data(
        meas_data.raw_data_set, scan_parameters
    )  ## returns dict {name: (x,y)} for completed data
    average_data = average_processed_data(meas_data.raw_data_set, scan_parameters)

    return current_data, completed_data, average_data


def process_current_data(data_array: xr.DataArray, scan_parameters: list) -> dict:
    ## data_array should be measurement_data_holder in Measurement_Data object
    ## need to update for handling 2-d and N-d scans

    parameter = scan_parameters[0]
    trimmed = data_array.dropna(parameter)

    ## checks if all values are nan
    if trimmed.nbytes == 0:
        return
    else:
        x = trimmed.coords.get(parameter).values
        y = np.mean(trimmed.values, axis=0)
    return {"current": (x, y)}


def completed_processed_data(processed_data_set: xr.Dataset, scan_parameters: list) -> dict:
    ## need to update for handling 2-d and N-d scans
    complete_data = {}
    parameter = scan_parameters[0]
    if processed_data_set.nbytes == 0:
        return
    else:
        for scan_key in list(processed_data_set.keys()):
            vals = processed_data_set.get(scan_key).values
            x = processed_data_set.get(scan_key).coords.get(parameter).values
            y = np.mean(vals, axis=vals.ndim - 1)
            complete_data.update({scan_key: (x, y)})
    return complete_data


def average_processed_data(processed_data_set: xr.Dataset, scan_parameters: list) -> dict:
    ## need to update for handling multi dimensional scans
    if processed_data_set.nbytes == 0:
        return {}
    else:
        parameter = scan_parameters[0]
        data_array = processed_data_set.to_array()
        x = data_array.coords.get(parameter).values
        vals = data_array.values
        mean_samps = np.mean(vals, axis=vals.ndim - 1)
        mean_scans = np.mean(mean_samps, axis=0)
        y = mean_scans
    return {"Average": (x, y)}


def main_trace_style(fig, trace_data: dict):
    ## use for current data and average data
    for trace_name in list(trace_data.keys()):
        (x, y) = trace_data.get(trace_name)
        new_trace = {
            "type": "scatter",
            "name": trace_name,
            "x": x,
            "y": y,
            "line": {"width": 4},
        }
        fig.get("data").insert(0, new_trace)
        ## use insert to add to front of list to order traces in plot properly
    return fig


def secondary_trace_style(fig, trace_data: dict):
    ## use for completed data
    for idx, trace_name in enumerate(list(trace_data.keys())):
        (x, y) = trace_data.get(trace_name)
        new_trace = {
            "type": "scatter",
            "name": trace_name,
            "x": x,
            "y": y,
            "line": {"width": 2},
            "opacity": max(0.25, 1 - 0.1 * idx),
        }
        fig.get("data").insert(0, new_trace)
    return fig


def clear_plot(fig):
    ## Need method and button for clearing plot
    return


@dataclass
class default_analyzer:
    process_data = process_data


analyzer_holder = gui_utils.Holder(default_analyzer)


if __name__ in {"__main__", "__mp_main__"}:
    gui_fields = gui_utils.GUI_fields()
    meas_settings = bc.Measurement_Settings()
    meas_data = bc.Measurement_Data()

    main(gui_fields, meas_settings, meas_data)

    ui.run(port=8082)
