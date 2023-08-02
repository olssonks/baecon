import itertools
import pathlib
from dataclasses import dataclass, field

import numpy as np
import plotly.graph_objects as go
from nicegui import APIRouter, app, ui

import baecon as bc
from baecon.Devices.Pulse_Sequence import Pulse, Pulse_Sequence
from baecon.GUI import gui_utils

gui_colors = ui.colors(
    primary="#485696", secondary="#E7E7E7", accent="#FC7A1E", positive="#53B689"
)

## Reference pages in other modules, see nicegui pull request #897
device_gui_router = APIRouter()
device_gui_name = pathlib.Path(__file__).name.split(".")[0]

## Sequence directory
SEQUENCE_DIRECTORY = pathlib.Path(__file__).parent.parent.resolve() / "sequences"


@dataclass
class PulseSequence_GUI_holder:
    file_path = ""
    file_name = ""
    channel_choice = 0
    output_number = "PS-0"
    shift_type = "no_shift"
    pulse_number = 0
    pulse_type = None
    pulse_start = 0
    pulse_duration = 0
    chan_select_ui = ""
    pulse_num_ui = ""  ## gui object bound to pulse_number
    show_types = False
    show_times = False
    seq_plot = ""
    chan_select_options: list = field(default_factory=list)
    pulse_num_options: list = field(default_factory=list)


ps_gui_holder: PulseSequence_GUI_holder = PulseSequence_GUI_holder()
ps_sequence: Pulse_Sequence = Pulse_Sequence([], [])


@device_gui_router.page(f"/{device_gui_name}")
def main():
    with ui.card():
        with ui.column():
            with ui.row().classes("w-full no-wrap"):
                with ui.column().classes("w-1/2"):
                    with ui.row().classes("no-wrap w-full"):
                        ui.button("Load", on_click=load_sequence).classes("w-full")
                        ui.button("Save", on_click=save_sequence).classes("w-full")
                        ui.button("Save As", on_click=save_as_sequence).classes("w-full")
                    ui.button("Update Pulse Device", on_click=update_pulse_device).classes(
                        "w-full"
                    )
                ui.input("Sequence File").bind_value(ps_gui_holder, "file_name").classes(
                    "w-full"
                )
            with ui.card().classes("w-full h-full"):
                fig = go.Figure()
                ps_gui_holder.seq_plot = ui.plotly(fig).classes("w-full h-full")
            with ui.row().classes("w-full no-wrap items-stretch"):
                with ui.card():
                    edit_channel_card()
                with ui.card().classes("flex"):
                    edit_pulse_card()


def edit_channel_card():
    ui.label("Edit Channel")
    with ui.column().classes("item-stretch"):
        with ui.row().classes("no-wrap w-full"):
            ps_gui_holder.chan_select_ui = (
                ui.select([0], label="Sequence Chan. Number")
                .classes("w-full")
                .bind_value(ps_gui_holder, "channel_choice")
            )
            ## "on_change" wasn't working but this way does
            ps_gui_holder.chan_select_ui.on("update:model-value", update_from_chan_change)

            ui.select(
                [
                    "PS-0",
                    "PS-1",
                    "PS-2",
                    "PS-3",
                    "PS-4",
                    "PS-5",
                    "PS-6",
                    "PS-7",
                    "PS-A0",
                    "PS-A1",
                ],
                label="Output",
                value="PS-0",
            ).classes("w-full").bind_value(ps_gui_holder, "output_number")

        with ui.row().classes("no-wrap"):
            ui.radio(
                {
                    "no_shift": "No Shift",
                    "shift_channel": "Shift in Channel",
                    "shift_all": "Shift All Pulses",
                },
                value="no_shift",
            ).bind_value(ps_gui_holder, "shift_type").classes("w-1/2")

            with ui.column().classes(""):
                ui.checkbox("Show Pulse Names", on_change=plot_sequence).bind_value(
                    ps_gui_holder, "show_types"
                )
                ui.checkbox("Show Pulse Times", on_change=plot_sequence).bind_value(
                    ps_gui_holder, "show_times"
                )
            with ui.column().classes("item-stretch"):
                ui.button("Add Channel", on_click=add_channel_button).classes("")
                ui.button("Remove Channel", on_click=remove_channel_button).classes("")
                ui.button("Update Channel", on_click=update_channel_button).classes("")

    return


def edit_pulse_card():
    with ui.column().classes(""):
        with ui.row().classes("w-full no-wrap grid-rows-2 justify-between"):
            ui.label("Edit Pulse").classes("")
            ui.label("Times rounded to nearest nanosecond").classes("font-bold opacity-25")

        with ui.row().classes("w-full no-wrap"):
            ps_gui_holder.pulse_num_ui = (
                ui.select(options=[0], label="Pulse", value=0)
                .classes("w-full")
                .bind_value(ps_gui_holder, "pulse_number")
            )
            ## "on_change" wasn't working but this does
            ps_gui_holder.pulse_num_ui.on("update:model-value", update_pulse_information)

            ui.input("Type", value="None").classes("w-full").bind_value(
                ps_gui_holder, "pulse_type"
            ).classes("text-uppercase")

        with ui.row().classes("no-wrap"):
            with ui.column().classes("w-2/3"):
                with ui.row().classes("w-full no-wrap"):
                    ui.label("Start Time:").classes("w-2/5 grid justify-end self-end")
                    ui.number("time (us)", value=0, step=0.001, format="%.3f").classes(
                        "w-3/5"
                    ).bind_value(ps_gui_holder, "pulse_start")
                with ui.row().classes("w-full no-wrap"):
                    ui.label("Pulse Duration:").classes("w-2/5 grid justify-end self-end")
                    ui.number("duration (us)", value=0, step=0.001, format="%.3f").classes(
                        "w-3/5"
                    ).bind_value(ps_gui_holder, "pulse_duration")

            with ui.column().classes("w-1/3"):
                ui.button("Add Pulse", on_click=add_pulse_button).classes("w-full")
                ui.button("Remove Pulse", on_click=remove_pulse_button).classes("w-full")
                ui.button("Update Pulse", on_click=update_pulse_button).classes("w-full")

    return


async def pick_file():
    """Opens pop-up window for selecting a file.
    Returns path to this file.

    Returns:
        path (str): Path to file
    """
    path = await gui_utils.load_file(SEQUENCE_DIRECTORY)
    return path


async def load_sequence():
    """Loads a :class:`Pulse_Sequence` from a file.

    The file is loaded as a dictionary which is used to create a
    :class:`Pulse_Sequence`. The attributes of the global pulse sequence
    `ps_sequence` are then set to the attributes of the the loaded sequence.
    This global pulse sequence stays the same Python object, just updated.

    The GUI fields are updated to reflect the loaded sequence, and then
    the sequence plot is updated.
    """
    file = await gui_utils.pick_file(SEQUENCE_DIRECTORY)
    if file:
        seq_dict = bc.utils.load_config(file)
        loaded_seq = Pulse_Sequence().from_dict(seq_dict)
        ## using ps_sequence = Pulse_Sequence(chans, pulses) doesn't update
        ## the pulse sequence
        ps_sequence.channels = loaded_seq.channels
        ps_sequence.pulse_patterns = loaded_seq.pulse_patterns
        ps_sequence.total_duration = loaded_seq.total_duration
        ps_gui_holder.file_path = file
        ps_gui_holder.file_name = gui_utils.name_from_path(file)
        update_from_load()
        plot_sequence()
    return


def update_from_load():
    """Updates GUI fields based on the loaded :class:`Pulse_Sequence`.

    The "loaded sequence" is actually the global sequence with the
    attributes of the loaded sequence in :func:`load_sequence`.

    The GUI fields updated the the ones in the channel and pulse cards.
    """
    ps_gui_holder.chan_select_options = list(range(len(ps_sequence.channels)))
    ps_gui_holder.chan_select_ui.options = ps_gui_holder.chan_select_options
    ps_gui_holder.chan_select_ui.update()

    for chan_idx, chan in enumerate(ps_sequence.channels):
        ps_gui_holder.output_number = chan
        ps_gui_holder.channel_choice = chan_idx
        update_pulse_options()
        for pulse_idx, _pulse in enumerate(ps_sequence.pulse_patterns[chan_idx]):
            ps_gui_holder.pulse_number = pulse_idx
            update_pulse_information()
    return


async def save_as_sequence():
    """Creates pop-up window to choose a file name and saves the sequence to a
    dictionary like configuration format.

    A pop-up window allows one to choose which file to save as. After saving
    the GUI fields for the file name and path are updated.
    """
    file = await gui_utils.pick_file(SEQUENCE_DIRECTORY)
    if file:
        seq_dict = ps_sequence.to_dict()
        bc.utils.dump_config(seq_dict, file)
        ps_gui_holder.file_path = file
        ps_gui_holder.file_name = gui_utils.name_from_path(file)
    return


def save_sequence():
    """Saves the sequence to a dictionary like file using file currently defined
    in the GUI.
    """
    seq_dict = ps_sequence.to_dict()
    bc.utils.dump_config(seq_dict, ps_gui_holder.file_path)
    return


def add_channel_button():
    """Adds channel to sequence.
    Channels have two identifiers the the channel number and output number.
    This allows outputs to be in any order.
    """
    add_channel()
    ps_gui_holder.chan_select_ui.options = ps_gui_holder.chan_select_options
    ps_gui_holder.chan_select_ui.update()
    update_pulse_information()
    return


def add_channel():
    """Addes channel to the pulse sequence.

    First, the `output_number` in the GUI is confirmed to not already be in
    the sequence. The channel is added to the pulse sequence using its
    `output_number`. (Channels are defined by their output name in
    :class:`Pulse_Sequence`).
    An empty pulse pattern (i.e. `list`) is added to the sequence as well.
    GUI fields are updated to reflect the new channel, and the empty channel
    is plotted.
    """
    ## Adding the first channel doesn't update the plot???
    ## functions get run by gui at start up, if statements avoid errors
    if ps_gui_holder.output_number in ps_sequence.channels:
        ui.notify(
            f"{ps_gui_holder.output_number} is already being used.",
            position="top",
            type="negative",
            timeout=3100,  ## weird units, not exactly milliseconds
        )
    else:
        ps_sequence.channels.append(ps_gui_holder.output_number)
        ps_sequence.pulse_patterns.append([])
        update_channel_options()
        clear_pulse_ui()
        plot_sequence()
    return


def update_channel_options():
    """Updates the GUI list of channels in a sequence."""
    ps_gui_holder.chan_select_options = list(range(len(ps_sequence.channels)))
    ps_gui_holder.channel_choice = ps_gui_holder.chan_select_options[-1]
    return


def clear_pulse_ui():
    """Clears the GUI fields with the pulse information.

    Used when adding a channel to clear all the pulse fields.
    """
    ps_gui_holder.pulse_number = 0
    ps_gui_holder.pulse_type = None
    ps_gui_holder.pulse_start = 0
    ps_gui_holder.pulse_duration = 0
    return


def remove_channel_button():
    """Removes a channel and plots the updated sequence."""
    remove_channel()
    plot_sequence()
    return


def remove_channel():
    """Removes a channel from the pulse sequence and updates GUI.

    First, it checks that the selected output_number exists in the :attr:channels
    of the pulse sequence. The respective channel is then removed from the sequence,
    along with its corresponding `pulses_patter`. The GUI is then updated with
    the altered pulse sequence.
    """
    if ps_gui_holder.output_number in ps_sequence.channels:
        chan_index = ps_gui_holder.channel_choice
        ps_sequence.channels.pop(chan_index)
        ps_sequence.pulse_patterns.pop(chan_index)
        ps_sequence.update()
        ps_gui_holder.chan_select_options = list(range(len(ps_sequence.channels)))
        if ps_gui_holder.chan_select_options == []:
            ps_gui_holder.channel_choice = 0
        else:
            ps_gui_holder.channel_choice = ps_gui_holder.chan_select_options[-1]
    return


def update_channel_button():
    ps_sequence.channels[ps_gui_holder.channel_choice] = ps_gui_holder.output_number
    ps_sequence.update()
    plot_sequence()
    return


def update_from_chan_change():
    """Updates GUI fields based on selecting different channel numbers.

    When switching channel number, the other fields fresh with the proper values.
    """
    if not ps_sequence.channels == []:
        ps_gui_holder.output_number = ps_sequence.channels[ps_gui_holder.channel_choice]
        ps_gui_holder.chan_select_ui.update()
        # if not ps_sequence.pulse_patterns[ps_gui_holder.channel_choice] == []:
        ps_gui_holder.pulse_number = 0  ## reset pulse to index 0 on switching channels
        update_pulse_options()
        update_pulse_information()
    ui.update()
    return


def add_pulse_button():
    """Adds pulse to the pulse pattern on the selected channel number and
    updates the GUI.
    """
    add_pulse(
        ps_sequence,
        ps_gui_holder.channel_choice,
        ps_gui_holder.pulse_start,
        ps_gui_holder.pulse_duration,
        ps_gui_holder.shift_type,
        ps_gui_holder.pulse_type,
    )
    update_pulse_options()
    update_pulse_information()
    ps_sequence.update()
    plot_sequence()
    return


def remove_pulse_button():
    """Remove selected pulse from the pattern of the selected channel and updates
    the GUI.

    Currently doesn't do any shifting of the sequence based on removing the pusle.
    """
    if not ps_sequence.channels == []:
        chan_index = ps_gui_holder.channel_choice
        pulse_index = ps_gui_holder.pulse_number
        if len(ps_sequence.pulse_patterns[chan_index]) == 1:
            ps_sequence.pulse_patterns.pop(chan_index)
        else:
            ps_sequence.pulse_patterns[chan_index].pop(pulse_index)
        update_pulse_options()
        update_pulse_information()
        ps_sequence.update()
        plot_sequence()
    return


def update_pulse_button():
    channel_pulses = ps_sequence.pulse_patterns[ps_gui_holder.channel_choice]
    channel_pulses[ps_gui_holder.pulse_number] = Pulse(
        ps_gui_holder.pulse_type,
        float(ps_gui_holder.pulse_start),
        ps_gui_holder.pulse_duration,
    )
    ps_sequence.update()
    plot_sequence()
    return


def update_pulse_options():
    """Updates the pulse number field in the GUI to reflect the number of pulses
    on the selected channel.
    """
    if not ps_sequence.pulse_patterns[ps_gui_holder.channel_choice] == []:
        num_of_pulses = len(ps_sequence.pulse_patterns[ps_gui_holder.channel_choice])
        ps_gui_holder.pulse_num_options = list(range(num_of_pulses))
        ps_gui_holder.pulse_num_ui.options = ps_gui_holder.pulse_num_options
        # ps_gui_holder.pulse_num_ui.bind_value(ps_gui_holder, 'pulse_number')
        ps_gui_holder.pulse_num_ui.update()
    return


def update_pulse_information():
    """Updates the GUI fields for a selected pulse in the pulse pattern of the
    selected channel.
    """
    if not ps_sequence.pulse_patterns[ps_gui_holder.channel_choice] == []:
        pulse_index = ps_gui_holder.pulse_number
        start = ps_sequence.pulse_patterns[ps_gui_holder.channel_choice][
            pulse_index
        ].start_time
        duration = ps_sequence.pulse_patterns[ps_gui_holder.channel_choice][
            pulse_index
        ].duration
        ps_gui_holder.pulse_start = start
        ps_gui_holder.pulse_duration = duration
        ps_gui_holder.pulse_type = ps_sequence.pulse_patterns[ps_gui_holder.channel_choice][
            pulse_index
        ].type
        ps_gui_holder.pulse_num_ui.update()
        plot_sequence()
    return


def add_pulse(
    ps: Pulse_Sequence,
    channel_choice: int,
    start: str,
    duration: str,
    shift_type: str,
    p_type: str,
) -> None:
    """Adds new pulse to the pulse sequence.
    The pulse is specified as a tuple of form ``(start, duration)``, and
    added to the specified ``channel``. The channle corresponds to the
    physical PulseStreamer channel, and not the placement in the
    sequence, e.g., sequence can have a channel list of [1,3,2,7] where
    the channels in the list do not correspond to their respective index.

    Depending on which is selected in the GUI, `no_shift`, `shift_in_channel`,
    and `shift_all_pulses`, the pulses in the sequence will be updated with
    shifts due to the added pulse.

    Args:
        ps (Pulse_Sequence): Pulse sequence to add channel to.
        channel (int): Physical PulseStreamer channel to at the pulse to.
        start (str): Pulse start time.
        duration (str): Pulse duration.
        p_type (str): Type of pulse, used for determining if pulse should be scanned.
    """
    pulse_insert(ps, channel_choice, start, duration, p_type)
    shift_dict[shift_type](ps, channel_choice, start, duration, p_type)
    return


def pulse_insert(
    ps: Pulse_Sequence, channel_choice: int, start: str, duration: str, p_type: str
):
    """Inserts pulse into a pulse pattern.

    First the new pulse is defined and then it is checked that it does not overlap
    with any other pulse in the pattern. If it does overlap, the pulse is not added.

    Args:
        ps (Pulse_Sequence): Pulse sequence to add channel to.
        channel (int): Physical PulseStreamer channel to at the pulse to.
        start (str): Pulse start time.
        duration (str): Pulse duration.
        p_type (str): Type of pulse, used for determining if pulse should be scanned.
    """

    pulses = ps.pulse_patterns[channel_choice]
    new_pulse = Pulse(p_type, float(start), float(duration))
    check_overlap = False

    for pulse in pulses:
        if pulse == new_pulse:
            check_overlap = True
        start = pulse.start_time
        end = pulse.end_time
        new_start = new_pulse.start_time
        new_end = new_pulse.end_time

        if (new_start < start < new_end) or (new_start < end < new_end):
            check_overlap = True

    if not check_overlap:
        pulses.append(new_pulse)
        ps.sort_channel(channel_choice)
        new_index = pulses.index(new_pulse)
        ps.pulse_patterns[channel_choice] = pulses
        ps_gui_holder.pulse_number = new_index
    return


def shift_all(
    ps: Pulse_Sequence, channel_index: int, start: str, duration: str, p_type: str
):
    """Shifts all pulses in the pulse sequence based on the start and duration
    of the added pulse. Only pulses after the new pulse are shifted.

    :func:`shift_all`, :shift:`shift_channel`, and :func:`no_shift` all use
    the same arguments because they are called by a dictionary of functions
    in :func:`add_pulse`. Not all arguments are used in each function.

    Args:
        ps (Pulse_Sequence): Pulse sequence to add channel to.
        channel (int): Physical PulseStreamer channel to at the pulse to.
        start (str): Pulse start time.
        duration (str): Pulse duration.
        p_type (str): Type of pulse, used for determining if pulse should be scanned.
    """
    start_time, p_duration = float(start), float(duration)
    for ch_idx, chan in enumerate(ps.pulse_patterns):
        for p_idx, pulse in enumerate(chan):
            if pulse.start_time > start:
                ps.pulse_patterns[ch_idx][p_idx] = Pulse(p_type, start_time, p_duration)
    ps.total_duration = ps.calc_duration()
    return


def shift_channel(
    ps: Pulse_Sequence, channel_index: int, start: str, duration: str, p_type: str
):
    """Shifts all pusles in a channel after the inserted pulse.

    Args:
        ps (Pulse_Sequence): Pulse sequence to add channel to.
        channel (int): Physical PulseStreamer channel to at the pulse to.
        start (str): Pulse start time.
        duration (str): Pulse duration.
        p_type (str): Type of pulse, used for determining if pulse should be scanned.
    """
    start, duration = float(start), float(duration)
    for p_idx, pulse in enumerate(ps.pulse_patterns[channel_index]):
        if pulse.start_time > start:
            ps.pulse_patterns[channel_index][p_idx] = Pulse(p_type, start, duration)
    ps.total_duration = ps.calc_duration()
    return


def no_shift(ps: Pulse_Sequence, channel_index: int, start: str, duration: str, p_type: str):
    """Nothing needed to add a pulse with no shift in the natural pulse
    notation.

    Sequence duration is updated with the addition of the new pulse.

    Args:
        ps (Pulse_Sequence): Pulse sequence to add channel to.
        channel (int): Physical PulseStreamer channel to at the pulse to.
        start (str): Pulse start time.
        duration (str): Pulse duration.
        p_type (str): Type of pulse, used for determining if pulse should be scanned.
    """
    ps.total_duration = ps.calc_duration()
    return


shift_dict = {
    "no_shift": no_shift,
    "shift_all": shift_all,
    "shift_channel": shift_channel,
}


def update_pulse_device():
    """Updates device to sequence shown in the GUI.

    The device object is stored in `app.storage` as an attribute
    indexed by its GUI name.
    """
    device = app.storage.__getattribute__(device_gui_name)
    device.update_sequence_from_gui(ps_sequence)
    return


def plot_sequence():
    """Plots pulse sequence."""
    if ps_sequence.pulse_patterns is not None:
        fig_data = prepare_plot_data(ps_sequence)
        ps_gui_holder.seq_plot.figure = fig_data
        ui.update(ps_gui_holder.seq_plot)
    # else:
    #     ps_gui_holder.seq_plot.figure["data"] = []
    #     ui.update(ps_gui_holder.seq_plot)
    return


def prepare_plot_data(ps_sequence: Pulse_Sequence) -> dict:
    """Prepares data from the pulse sequence for plotting.

    First the patterns are turned into numpy arrarys with time steps
    of 1 nanosecond. These arrays are sued to make the `fit_data` and
    annotations of the pulse times and types are added based on GUI
    selection fields.

    .. todo::
        Propbably good to add a way to specify units of time.
    Args:
        ps_sequence (Pulse_Sequence): Pulse sequence to plot

    Returns:
        fig (dict): Dictionary defining parameters of the plot, including data.
    """
    seq_to_plot, seq_steps = make_plot_data(ps_sequence)

    fig_data = make_plot_traces(seq_to_plot, seq_steps)

    annotations = []
    if ps_gui_holder.show_types:
        annotations.extend(plot_pulse_types(ps_sequence, seq_to_plot, seq_steps))
    if ps_gui_holder.show_times:
        annotations.extend(plot_pulse_times(ps_sequence, seq_to_plot, seq_steps))
    fig = {
        "data": fig_data,
        "layout": {
            "margin": {"l": 30, "r": 0, "t": 0, "b": 30},
            "plot_bgcolor": "#E5ECF6",
            "showlegend": True,
            "legend": {"traceorder": "reversed"},
            "xaxis": {"gridcolor": "white", "title": {"text": "Time (us)"}},
            "yaxis": {"visible": False, "gridcolor": "white"},
            "annotations": annotations,
        },
    }
    return fig


def make_plot_traces(
    sequence_to_plot: np.ndarray[float], sequence_time_steps: np.ndarray[float]
) -> list[dict]:
    """Generates traces to plot.

    Loops through the pulse patterns defined in `sequence_to_plot`, generating a
    dictionary in format used by plotly.

    Args:
        sequence_to_plot (nd.aarray): Numpy array with dimensions (channels, time steps)
        sequence_time_steps (nd.array): Time steps.

    Returns:
        list[dict]: Dictionarys of data for each pulse pattern.
    """
    trace_color = itertools.cycle(
        ["#e0003c", "#66A37A", "#357ded", "#f8d53a", "#f06f05", "#54457F"]
    )
    traces = []
    for idx, seq in enumerate(sequence_to_plot):
        traces.append(
            {
                "x": sequence_time_steps,
                "y": seq,
                "type": "scatter",
                "name": f"Chan{idx}:{ps_sequence.channels[idx]}",
                "line": {"color": trace_color.__next__()},
            }
        )
    return traces


def make_plot_data(
    ps_sequence: Pulse_Sequence,
) -> tuple[np.ndarray[float], np.ndarray[float]]:
    """Uses numpy to turn the :class:`Pulse_Sequence` in to plottable data.

    Args:
        ps_sequence (Pulse_Sequence): Pulse sequence to plot.

    Returns:
        tuple[np.ndarray[float], np.ndarray[float]]: A tuple with elements:
            Numpy array with dimentions (channels, time steps) and Numpy array
            with dimenions (time steps).
    """
    seq_duration = ps_sequence.total_duration
    if seq_duration == 0:
        ## still plots channels if no channels have any pulses
        seq_duration = 10
    all_pulses = ps_sequence.pulse_patterns
    ## times defined in us, 1000 and 0.001 factors give nanosecond resolution
    sequence_to_plot = np.zeros((len(all_pulses), int(seq_duration * 1000)))
    sequence_time_steps = np.arange(0, seq_duration, 0.001)

    for c_idx, chan in enumerate(all_pulses):
        for _p_idx, pulse in enumerate(chan):
            start = int(pulse.start_time * 1000)
            dur = int(pulse.duration * 1000)
            sequence_to_plot[c_idx, start : start + dur] = 1 * 0.75
        sequence_to_plot[c_idx] += 1.15 * c_idx

    return (sequence_to_plot, sequence_time_steps)


def plot_pulse_types(
    ps_sequence: Pulse_Sequence,
    sequence_to_plot: np.ndarray[float],
    sequence_time_steps: np.ndarray[float],
) -> list[dict]:
    """Creates list of annotation dictionaries specifying the type of pulses.

    Uses the data `sequence_to_plot` and `sequence_time_steps`  to determine
    the location to set the annotation on the plot.
    Args:
        ps_sequence (Pulse_Sequence): Pulse sequence to plot types of.
        sequence_to_plot (np.ndarray[float]): Numpy array of sequence data.
        sequence_time_steps (np.ndarray[float]): Numpy array of time steps.

    Returns:
        list[dict]: List of annotation dictionaries for pulse types.
    """
    type_annotations = []
    for ch_idx, _chan in enumerate(ps_sequence.channels):
        for p_idx, pulse in enumerate(ps_sequence.pulse_patterns[ch_idx]):
            ## x and y here are used as coordinates to place the text on the plot
            time_idx = int(ps_sequence.pulse_patterns[ch_idx][p_idx].start_time) * 1000
            x = sequence_time_steps[time_idx - 1]
            y = sequence_to_plot[ch_idx][time_idx - 1]

            type_annotations.append(
                {
                    "x": x,
                    "y": y,
                    "xref": "x",
                    "yref": "x",
                    "text": f"Type: {pulse.type!s}",
                    "showarrow": False,
                    "ax": 0,
                    "ay": 0,
                    "font": {"size": 14, "color": "#000000"},
                    "bgcolor": "#ffffff90",
                    "xanchor": "right",
                    "yanchor": "bottom",
                }
            )
    return type_annotations


def plot_pulse_times(
    ps_sequence: Pulse_Sequence,
    sequence_to_plot: np.ndarray[float],
    sequence_time_steps: np.ndarray[float],
) -> list[dict]:
    """Creates a list of annotation dictionarys to display the start time and duration of each pulse.

    Uses the data `sequence_to_plot` and `sequence_time_steps`  to determine
    the location to set the annotation on the plot.

    Args:
        ps_sequence (Pulse_Sequence): Pulse sequence to plot types of.
        sequence_to_plot (np.ndarray[float]): Numpy array of sequence data.
        sequence_time_steps (np.ndarray[float]): Numpy array of time steps.

    Returns:
        list[dict]: List of annotations dictionaries for pulse times.
    """
    time_annotations = []
    for pat_idx, pattern in enumerate(ps_sequence.pulse_patterns):
        for p_idx, pulse in enumerate(pattern):
            ## x and y here are used as coordinates to place the text on the plot
            time_idx = int(ps_sequence.pulse_patterns[pat_idx][p_idx].start_time) * 1000
            x = sequence_time_steps[time_idx]
            y = sequence_to_plot[pat_idx][time_idx]
            label = f"Start: {pulse.start_time:.3f}<br>Duration: {pulse.duration:.3f}"  ## <br> is new line in plotly

            time_annotations.append(
                {
                    "x": x,
                    "y": y,
                    "xref": "x",
                    "yref": "x",
                    "text": label,
                    "showarrow": False,
                    "ax": 0,
                    "ay": 0,
                    "font": {"size": 14, "color": "#000000"},
                    "align": "left",
                    "bgcolor": "#ffffff90",
                    "xanchor": "left",
                    "yanchor": "top",
                }
            )
    return time_annotations


if __name__ in {"__main__", "__mp_main__"}:
    with ui.card():
        # ui.button('Open').props('href="/PulseStreamer" target="_blank" ')
        main()

    ui.run(port=8666)
