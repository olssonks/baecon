from nicegui import ui
import plotly.graph_objects as go

import numpy as np
import matplotlib.pyplot as plt

from dataclasses import dataclass, field
import sys
sys.path.insert(0,'C:\\Users\\walsworth1\\Documents\\Jupyter_Notebooks\\baecon')

#import gui_utils
import baecon as bc

    
@ui.page('/PulseStreamer')
def PulseStreamer():
    with ui.card().classes('w-full h-full'):
        with ui.column().classes('w-full h-full'):
            with ui.card().classes('w-full h-full'):
                fig = go.Figure(go.Scatter(x=[1, 2, 3, 4], y=[1, 2, 3, 2.5]))
                fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
                ui.plotly(fig).classes('w-full h-full')
            with ui.row().classes('w-full h-full no-wrap'):
                with ui.card().classes('w-full h-full'):
                    edit_channel()
                with ui.card().classes('w-full h-full'):
                    edit_pulse()
      
    return
    
def edit_channel():
    ui.label('Edit Channel')
    with ui.column().classes('w-full h-full'):
        with ui.row().classes('w-full h-full no-wrap'):
            ui.select(['select'], label='Chan. Number').classes('w-2/6')
            ui.select(['N'], label = 'PS Number').classes('w-2/6')
            ui.button("Add Channel").classes('w-1/6')
            ui.button("Remove Channel").classes('w-1/6')
        
        ui.radio({'no_shift': 'No Shift', 
                'shift_channel': 'Shift in Channel',
                'shift_all': 'Shift All Pulses'}, value='no_shift')
    return
    
def edit_pulse():
    ui.label('Edit Pulse')
    with ui.column().classes('w-full h-full'):
        with ui.row().classes('w-full h-full no-wrap'):
            ui.select(['select'], label='Pulse').classes('w-1/3')
            ui.input('Name').classes('w-1/3')
            ui.button("Add Pulse").classes('w-1/6')
            ui.button("Remove Pulse").classes('w-1/6')
        with ui.column().classes('w-full h-full'):
            with ui.row().classes('w-full h-full no-wrap items-center'):
                ui.label('Start Time:').classes('w-1/5')
                ui.input('time').classes('w-2/5')
                ui.label('Actual Time').classes('w-2/5')
            with ui.row().classes('w-full h-full no-wrap items-center'):
                ui.label('Pulse Duration:').classes('w-1/5')
                ui.input('duration').classes('w-2/5')
                ui.label('Actual Time').classes('w-2/5')
    return
                    

with ui.card():
        ui.button('Open').props('href="/PulseStreamer" target="_blank" ')
                    
ui.run(port=8666)

# import itertools
              
# seq = [
#     [(10, 1), (50,1), (70, 20)],
#     [(20, 20)],
#     [(5,5), ]
#     ]

# seq_duration = max([pulse[0]+pulse[1] for channel in seq for pulse in channel])

# plot_seq = np.zeros((len(seq), seq_duration*1000))
# seq_points = np.arange(0, seq_duration, 0.001)

# for c_idx, chan in enumerate(seq):
#     for p_idx, pulse in enumerate(chan):
#         plot_seq[c_idx, 
#                  pulse[0]*1000:(pulse[0]+pulse[1])*1000] = 1
#         plot_seq[c_idx] = plot_seq[c_idx] + c_idx*1.1
        
# print(plot_seq)

# for seq in plot_seq:
#     plt.plot(seq)