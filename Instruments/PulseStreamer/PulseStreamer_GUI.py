from nicegui import ui
import plotly.graph_objects as go

import numpy as np
import matplotlib.pyplot as plt

from dataclasses import dataclass, field
import sys
sys.path.insert(0,'C:\\Users\\walsworth1\\Documents\\Jupyter_Notebooks\\baecon')

import GUI.gui_utils as gui_utils
import baecon as bc

@dataclass
class Pulse_Sequence: ## Maybe different name to not be confused with PulseStreamer sequencies
    """To make the scan of the sequence, we'll have a copy or holder of the original sequence
       so that when scanning we are adding/setting time with respect to the orignal sequence
       if start = 4us and scan is add 1,2,3, we want 5, 6, 7 to be out come
       not (4+1), (4+1+2), (4+1+2+3)
    """
    channels: list
    pulses: list
    name: list
 
@dataclass
class PulseStreamer_GUI_holder:
    channel
    ps_output
    shift_type
    pulse_number
    pulse_name
    pulse_start
    pulse_duration

@ui.page('/PulseStreamer')
def PulseStreamer():
    ps_gui_holder = PulseStreamer_GUI_holder()
    ps_sequence = Pulse_Sequence()
    with ui.card().classes('w-full h-full'):
        with ui.column().classes('w-full h-full'):
            with ui.card().classes('w-full h-full'):
                fig = go.FigureWidget()
                seq_plot = ui.plotly(fig).classes('w-full h-full')
                ui.button('Plot', on_click=plot_sequence(seq_plot, fig, pulses))
            with ui.row().classes('w-full h-full no-wrap'):
                with ui.card().classes('w-full h-full'):
                    edit_channel(ps_sequence, ps_gui_holder)
                with ui.card().classes('w-full h-full'):
                    edit_pulse(ps_gui_holder)
      
    return
    
def edit_channel(ps_gui_holder):
    ui.label('Edit Channel')
    with ui.column().classes('w-full h-full'):
        with ui.row().classes('w-full h-full no-wrap'):
            ui.select(['select'], label='Chan. Number').classes('w-2/6').bind_value(ps_gui_holder, 'channel')
            ui.select([0,1,2,3,4,5,6,7, "A0", "A1"], 
                      label = 'PS Number',
                      value=0).classes('w-2/6').bind_value(ps_gui_holder, 'ps_output')
            ui.button("Add Channel", 
                      on_click=add_channel(ps_gui_holder)).classes('w-1/6')
            ui.button("Remove Channel", 
                      on_click=remove_channel(ps_gui_holder)).classes('w-1/6')
        
        ui.radio({'no_shift': 'No Shift', 
                'shift_channel': 'Shift in Channel',
                'shift_all': 'Shift All Pulses'}, 
                 value='no_shift').bind_value(ps_gui_holder,'shift_type')
    return

    
def edit_pulse_card(ps:Pulse_Sequence, 
                    holder: PulseStreamer_GUI_holder):
    ui.label('Edit Pulse')
    with ui.column().classes('w-full h-full'):
        with ui.row().classes('w-full h-full no-wrap'):
            ui.select(['select'], label='Pulse').classes('w-1/3').bind_value(holder, 'pulse_number')
            ui.input('Name').classes('w-1/3').bind_value(ps_gui_holder, 'pulse_name')
            ui.button("Add Pulse", on_click=add_pulse_button(ps, holder)).classes('w-1/6')
            ui.button("Remove Pulse").classes('w-1/6')
        with ui.column().classes('w-full h-full'):
            with ui.row().classes('w-full h-full no-wrap items-center'):
                ui.label('Start Time:').classes('w-1/5')
                ui.input('time').classes('w-2/5').bind_value(holder, 'pulse_start')
                ui.label('Actual Time').classes('w-2/5')
            with ui.row().classes('w-full h-full no-wrap items-center'):
                ui.label('Pulse Duration:').classes('w-1/5')
                ui.input('duration').classes('w-2/5').bind_value(holder, 'pulse_duration')
                ui.label('Actual Time').classes('w-2/5')
    return
        
def add_pulse_button(ps:Pulse_Sequence, 
                     holder: PulseStreamer_GUI_holder):
    add_pulse(ps, ps_gui_holder.channel, holder.pulse_start, 
              holder.pulse_duration, holder.shift_type, holder.pulse_name)
    return
    
def remove_pulse_button(s:Pulse_Sequence, 
                        holder: PulseStreamer_GUI_holder):
    return

def add_pulse(ps:Pulse_Sequence, 
                channel:int, start:float, duration:float, 
                shift_type:str, name:str=None):
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
        name (str, optional): _description_. Defaults to None.

    Returns:
        _type_: _description_
    """    
    if channel in ps.channels:
        index = ps.channels.index(channel)
        ps = pulse_insert(ps, index, start, duration, name)
        shift_dict[shift_type](ps, index, start, duration)
    else:
        ps.channels.append(channel)
        index = len(ps.channels) - 1
        ps = pulse_insert(ps, index, start, duration, name)
        shift_dict[shift_type](ps, index, start, duration)
    return ps

def pulse_insert(self, ps:Pulse_Sequence, channel_index:int, 
                start:float, duration:float, name:str):
    pulses = ps.pulses[channel_index]
    new_pulse = (start,duration)
    pulses.append(new_pulse)
    pulses.sort()
    new_index = pulses.index(new_pulse)
    ps.names.insert(new_index, name)
    return ps
    

    
def shift_all(ps:Pulse_Sequence, channel_index:int, 
                start:float, duration:float):
    for chan_seq in ps.pulses:
        for chan_pulse in chan_seq:
            if chan_pulse[0]>start:
                chan_pulse[0] = chan_pulse[0]+duration
    return

def shift_current(ps:Pulse_Sequence, channel_index:int, 
                start:float, duration:float):
    for chan_pulse in ps.pulses[channel_index]:
        if chan_pulse[0]>start:
            chan_pulse[0] = chan_pulse[0]+duration
    return

shift_dict = {'shift_all': shift_all, 'shift_current': shift_current}


with ui.card():
        ui.button('Open').props('href="/PulseStreamer" target="_blank" ')
                    
ui.run(port=8666)

