from nicegui import ui
import plotly.graph_objects as go

from dataclasses import dataclass, field
import sys
sys.path.insert(0,'C:\\Users\\walsworth1\\Documents\\Jupyter_Notebooks\\baecon')

#import gui_utils
import baecon as bc

    
@ui.page('/Pulse_Streamer')
def Pulse_Streamer():
    with ui.card():
        with ui.column():
            with ui.card():
                fig = go.Figure(go.Scatter(x=[1, 2, 3, 4], y=[1, 2, 3, 2.5]))
                fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
                ui.plotly(fig).classes('w-full h-full')
            with ui.row().classes('w-full h-full no-wrap'):
                with ui.card():
                    ui.label('Edit Channel')
                with ui.card():
                    ui.label('Edit Pulse')
                    
                    
    return
                    

with ui.card():
        ui.button('Open', on_click=lambda: ui.open(Pulse_Streamer))
                    
ui.run(port=8082)
                
