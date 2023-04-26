from nicegui import ui
import plotly.graph_objects as go

import numpy as np
import matplotlib.pyplot as plt

from dataclasses import dataclass, field
import sys
sys.path.insert(0,'C:\\Users\\walsworth1\\Documents\\Jupyter_Notebooks\\baecon')

gui_colors = ui.colors(primary='#485696', secondary='#E7E7E7', accent='#FC7A1E', positive='#53B689')

import GUI.gui_utils as gui_utils
import baecon as bc

@dataclass
class Pulse_Sequence: ## Maybe different name to not be confused with PulseStreamer sequencies
    """To make the scan of the sequence, we'll have a copy or holder of the original sequence
       so that when scanning we are adding/setting time with respect to the orignal sequence
       if start = 4us and scan is add 1,2,3, we want 5, 6, 7 to be out come
       not (4+1), (4+1+2), (4+1+2+3)
    """
    ps_output: list = field(default_factory=list)
    pulses: list = field(default_factory=list)
    pulses_swabian: list = field(default_factory=list)
    types: list = field(default_factory=list)
    types_swabian: list = field(default_factory=list)
 
@dataclass
class PulseStreamer_GUI_holder:
    channel_choice = 0
    ps_output = 'PS-0'
    shift_type = 'no_shift'
    pulse_number = ''
    pulse_type = None
    pulse_start = 0
    pulse_duration = 0
    chan_select_ui = ''
    chan_select_options: list = field(default_factory=list)
    pulse_num_ui = ''
    pulse_num_options: list = field(default_factory=list)
    show_types = False
    show_times = False
    seq_plot = ''



@ui.page('/PulseStreamer')
def PulseStreamer():
    ui.colors(primary='#485696', secondary='#E7E7E7', accent='#FC7A1E', positive='#53B689')
    with ui.card().classes('w-full h-full'):
        with ui.column().classes('w-full h-full'):
            with ui.card().classes('w-full h-full'):
                fig = go.Figure()
                ps_gui_holder.seq_plot = ui.plotly(fig).classes('w-full h-full')
            with ui.row().classes('w-full h-full no-wrap'):
                with ui.card().classes('w-full h-full'):
                    edit_channel_card()
                with ui.card().classes('w-full h-full'):
                    edit_pulse_card()
      
    return
    
def edit_channel_card():
    ui.label('Edit Channel')
    with ui.column().classes('w-full h-full'):
        
        with ui.row().classes('w-full h-full no-wrap'):
            ps_gui_holder.chan_select_ui = ui.select([0], 
                label='Chan. Number', on_change=update_from_chan_change)\
            .classes('w-2/6').bind_value(ps_gui_holder, 'channel_choice')
            
            ui.select(["PS-0", "PS-1", "PS-2", "PS-3", "PS-4", 
                       "PS-5", "PS-6", "PS-7", "PS-A0", "PS-A1"], 
                      label = 'PS Number',
                      value="PS-0").classes('w-2/6').bind_value(ps_gui_holder, 'ps_output')
            
            ui.button("Add Channel", 
                      on_click=add_channel_button).classes('w-1/6')
            ui.button("Remove Channel", 
                      on_click=remove_channel_button).classes('w-1/6')
       
        with ui.row().classes('w-full h-full no-wrap'):
            
            ui.radio({'no_shift': 'No Shift', 
                    'shift_channel': 'Shift in Channel',
                    'shift_all': 'Shift All Pulses'}, 
                        value='no_shift').bind_value(ps_gui_holder,'shift_type').classes('w-1/2')
            
            with ui.column().classes('w-full h-full'):
                ui.checkbox('Show Pulse Names', on_change=plot_sequence).bind_value(ps_gui_holder,'show_types')
                ui.checkbox('Show Pulse Times', on_change=plot_sequence).bind_value(ps_gui_holder,'show_times')
    return
    

def add_channel_button():
    add_channel()
    ps_gui_holder.chan_select_ui.options = ps_gui_holder.chan_select_options
    ps_gui_holder.chan_select_ui.update()
    print(ps_sequence)
    return
    
def add_channel():
    ## functions get run by gui at start up, if statements avoid errors
    if not ps_gui_holder.ps_output in ps_sequence.ps_output:
        ps_sequence.ps_output.append(ps_gui_holder.ps_output)
        ps_sequence.pulses.append([])
        ps_sequence.types.append([])
        ps_gui_holder.chan_select_options = [i for i in range(len(ps_sequence.ps_output))]
        ps_gui_holder.channel_choice = ps_gui_holder.chan_select_options[-1]
        plot_sequence()
    return
    
def remove_channel_button():
    remove_channel()
    plot_sequence()
    return
    
def remove_channel():
    if ps_gui_holder.ps_output in ps_sequence.ps_output:
        chan_index = ps_gui_holder.channel_choice
        ps_sequence.ps_output.pop(chan_index)
        ps_sequence.pulses.pop(chan_index)
        ps_sequence.types.pop(chan_index)
        ps_gui_holder.chan_select_options = [i for i in range(len(ps_sequence.ps_output))]
        if ps_gui_holder.chan_select_options == []:
            ps_gui_holder.channel_choice = 0
        else:
            ps_gui_holder.channel_choice = ps_gui_holder.chan_select_options[-1]
    return
    
def update_from_chan_change():
    if not ps_sequence.ps_output == []:
        ps_gui_holder.ps_output = ps_sequence.ps_output[ps_gui_holder.channel_choice]
        ps_gui_holder.chan_select_ui.update()
        if not ps_sequence.pulses[ps_gui_holder.channel_choice] == []:
            update_pulse_options()
            update_pulse_information()
    return
    
def edit_pulse_card():
    ui.label('Edit Pulse')
    with ui.column().classes('w-full h-full'):
        
        with ui.row().classes('w-full h-full no-wrap'):
            ps_gui_holder.pulse_num_ui = ui.select(
                ['select'], label='Pulse',on_change=update_pulse_information)\
                .classes('w-1/3').bind_value(ps_gui_holder, 'pulse_number')
            
            ui.input('Type', value="None").classes('w-1/3').bind_value(ps_gui_holder, 'pulse_type')
            ui.button("Add Pulse", on_click=add_pulse_button).classes('w-1/6')
            ui.button("Remove Pulse", on_click=remove_pulse_button).classes('w-1/6')
        
        with ui.column().classes('w-full h-full'):
            with ui.row().classes('w-full h-full no-wrap items-center'):
                ui.label('Start Time:').classes('w-1/5')
                ui.input('time (us)').classes('w-2/5').bind_value(ps_gui_holder, 'pulse_start')
                ui.label('Actual Time').classes('w-2/5')
            
            with ui.row().classes('w-full h-full no-wrap items-center'):
                ui.label('Pulse Duration:').classes('w-1/5')
                ui.input('duration (us)').classes('w-2/5').bind_value(ps_gui_holder, 'pulse_duration')
                ui.label('Actual Time').classes('w-2/5')
    return
      
def add_pulse_button():
    add_pulse(ps_sequence, ps_gui_holder.channel_choice, ps_gui_holder.pulse_start, 
              ps_gui_holder.pulse_duration, ps_gui_holder.shift_type, ps_gui_holder.pulse_type)
    print(ps_sequence)
    update_pulse_options()
    update_pulse_information()
    return
    
def remove_pulse_button():
    if not ps_sequence.ps_output == []:
        chan_index  = ps_gui_holder.channel_choice
        pulse_index = ps_gui_holder.pulse_number
        if len(ps_sequence.pulses[chan_index]) == 1:
            ps_sequence.pulses.pop(chan_index)
            ps_sequence.types.pop(chan_index)
        else:
            ps_sequence.pulses[chan_index].pop(pulse_index)
            ps_sequence.types[chan_index].pop(pulse_index)
        update_pulse_options()
        update_pulse_information()
        plot_sequence()
    return

def update_pulse_options():
    if not ps_sequence.pulses == []:
        num_of_pulses = len(ps_sequence.pulses[ps_gui_holder.channel_choice])
        ps_gui_holder.pulse_num_options    = [i for i in range(num_of_pulses)]
        ps_gui_holder.pulse_num_ui.options = ps_gui_holder.pulse_num_options
        ps_gui_holder.pulse_num_ui.update()
    return

def update_pulse_information():
    if not ps_sequence.pulses == []:
        pulse_index     = ps_gui_holder.pulse_number
        start, duration = ps_sequence.pulses[ps_gui_holder.channel_choice][pulse_index]
        ps_gui_holder.pulse_start    = start
        ps_gui_holder.pulse_duration = duration
        ps_gui_holder.pulse_type = ps_sequence.types[ps_gui_holder.channel_choice][pulse_index]
    return 

def add_pulse(ps:Pulse_Sequence, 
                channel_choice:int, start:float, duration:float, 
                shift_type:str, type:str=None):
    """Adds new pulse to the pulse sequence.
        The pulse is specified as a tuple of form ``(start, duration)``, and
        added to the specified ``channel``. The channle corresponds to the 
        physical PulseStreamer channel, and not the placement in the 
        sequence, e.g., sequence can have a channel list of [1,3,2,7] where
        the channels in the list do not correspond to their respective index.

    Args:
        ps (Pulse_Sequence): Pulse sequence to add channel to.
        channel (int): Physical PulseStreamer channel to at the pulse to.
        start (float): _description_
        duration (float): _description_
        type (str, optional): _description_. Defaults to None.

    Returns:
        _type_: _description_
    """    
    pulse_insert(ps, channel_choice, start, duration, type)
    shift_dict[shift_type](ps, channel_choice, start, duration)
    plot_sequence()
    return

def pulse_insert(ps:Pulse_Sequence, channel_choice:int, 
                start:str, duration:str, type:str):
    pulses        = ps.pulses[channel_choice]
    new_pulse     = (float(start), float(duration))
    check_overlap = False
    
    for pulse in pulses:
        if pulse == new_pulse:
            check_overlap = True
        start     = pulse[0]; end         = pulse[0] + pulse[1]
        new_start = new_pulse[0]; new_end = new_pulse[0] + new_pulse[1]
        
        if (new_start < start < new_end) or (new_start < end < new_end):
            check_overlap = True
    
    if not check_overlap:
        pulses.append(new_pulse)
        pulses.sort()
        new_index = pulses.index(new_pulse)
        ps.pulses[channel_choice] = pulses
        ps.types[channel_choice].insert(new_index, type)
        ps_gui_holder.pulse_number = new_index
    return
    
    
def shift_all(ps:Pulse_Sequence, channel_index:int, 
                start:str, duration:str):
    start, duration = (float(start), float(duration))
    for ch_idx, chan in enumerate(ps.pulses):
        for p_idx, pulse in enumerate(chan):
            if pulse[0]>start:
                ps.pulses[ch_idx][p_idx] = (pulse[0]+duration, pulse[1])
    return

def shift_channel(ps:Pulse_Sequence, channel_index:int, 
                start:float, duration:float):
    start, duration = (float(start), float(duration))
    for p_idx, pulse in enumerate(ps.pulses[channel_index]):
        if pulse[0]>start:
            ps.pulses[channel_index][p_idx] = (pulse[0]+duration, pulse[1])
    return

def no_shift(ps:Pulse_Sequence, channel_index:int, 
                start:float, duration:float):
    """Nothing needed to add a pulse with no shift in the natural pulse 
       notation.

    Args:
        ps (Pulse_Sequence): _description_
        channel_index (int): _description_
        start (float): _description_
        duration (float): _description_
    """    
    return

shift_dict = {'no_shift': no_shift, 'shift_all': shift_all, 'shift_channel': shift_channel}


def plot_sequence():
    if not ps_sequence.pulses == []:
        fig_data = plot_data(ps_sequence)
        ps_gui_holder.seq_plot.figure = fig_data
        ui.update(ps_gui_holder.seq_plot)
    else:
        ## how to remove annotations?? below doesn't work
        ps_gui_holder.seq_plot.figure['data'] = []
        # ps_gui_holder.seq_plot.figure['annotations'] = []
        ui.update(ps_gui_holder.seq_plot)
    return

def plot_data(ps_sequence:Pulse_Sequence):

    seq_to_plot, seq_steps = make_plot_data(ps_sequence.pulses)

    fig_data = make_plot_traces(seq_to_plot, seq_steps)
        
    annotations =[]
    if ps_gui_holder.show_types:
        annotations.extend(plot_pulse_types(ps_sequence, seq_to_plot, seq_steps))
    if ps_gui_holder.show_times:
        annotations.extend(plot_pulse_times(ps_sequence, seq_to_plot, seq_steps))
    fig = {
        'data': fig_data,
        'layout': {
            'margin': {'l': 30, 'r': 0, 't': 0, 'b': 30},
            'plot_bgcolor': '#E5ECF6',
            'showlegend': True,
            'xaxis': {'gridcolor': 'white', 'title': {'text': 'Time (us)'}},
            'yaxis': {'visible':False, 'gridcolor': 'white'},
            'annotations': annotations,
        },
    }
    return fig

def make_plot_traces(sequence_to_plot, sequence_time_steps):   
    traces =[]
    for idx, seq in enumerate(sequence_to_plot):
        traces.append({'type': 'scatter', 'name': f'Chan{idx}:{ps_sequence.ps_output[idx]}', 
                        'x': sequence_time_steps, 'y': seq})
    return traces

def make_plot_data(sequence:list):
    seq_duration = sequence_duration(sequence)

    sequence_to_plot = np.zeros((len(sequence), seq_duration*1000))
    sequence_time_steps = np.arange(0, seq_duration, 0.001)
    
    for c_idx, chan in enumerate(sequence):
        for p_idx, pulse in enumerate(chan):
            start = int(pulse[0])*1000
            dur   = int(pulse[1])*1000
            sequence_to_plot[c_idx, start:start+dur] = 1*0.75
        sequence_to_plot[c_idx] += 1.15*c_idx
    
    return [sequence_to_plot, sequence_time_steps]

def sequence_duration(sequence):
    durations = []
    for chan in sequence:
        ## default length is 10 us
        if chan == []:
            durations.append(10)
        for pulse in chan:
            t=pulse[0] + pulse[1]
            durations.append(t)
    return int(max(durations))
    
def plot_pulse_types(ps_sequence:Pulse_Sequence,
                     sequence_to_plot:list, sequence_time_steps:list):
    type_annotations = []
    for ch_idx, types in enumerate(ps_sequence.types):
        for p_idx, type in enumerate(types):
            time_idx = int(ps_sequence.pulses[ch_idx][p_idx][0])*1000
            x = sequence_time_steps[time_idx - 1]
            y = sequence_to_plot[ch_idx][time_idx - 1]
            type_annotations.append({
                'x':x, 'y':y, 'xref':'x', 'yref':'x', 'text':f'Type: {str(type)}', 
                'showarrow':False,'ax':0, 'ay':0,
                'font': {'size':14, 'color':'#000000'},
                'bgcolor': '#ffffff90', 'xanchor': 'right', 'yanchor':'bottom'
                })
    return type_annotations

def plot_pulse_times(ps_sequence:Pulse_Sequence,
                     sequence_to_plot:list, sequence_time_steps:list):
    time_annotations = []
    for ch_idx, chan in enumerate(ps_sequence.pulses):
        for p_idx, pulse in enumerate(chan):
            time_idx = int(ps_sequence.pulses[ch_idx][p_idx][0])*1000
            x = sequence_time_steps[time_idx]
            y = sequence_to_plot[ch_idx][time_idx]
            label = f"Start: {pulse[0]:.3f}<br>Duration: {pulse[1]:.3f}" ## <br> is new line in plotly
            time_annotations.append({
                'x':x, 'y':y, 'xref':'x', 'yref':'x', 'text':label, 
                'showarrow':False,'ax':0, 'ay':0,
                'font': {'size':14, 'color':'#000000'}, 'align':'left',
                'bgcolor': '#ffffff90', 'xanchor': 'left', 'yanchor':'top'
                })
    return time_annotations

with ui.card():
    ps_gui_holder = PulseStreamer_GUI_holder()
    ps_sequence = Pulse_Sequence()
    ui.button('Open').props('href="/PulseStreamer" target="_blank" ')

#PulseStreamer()
ui.run(port=8666)