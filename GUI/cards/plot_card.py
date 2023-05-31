from nicegui import ui
import plotly.graph_objects as go

from dataclasses import dataclass, field
import sys
sys.path.insert(0,'C:\\Users\\walsworth1\\Documents\\Jupyter_Notebooks\\baecon')

from GUI import gui_utils
import baecon as bc

head_style = 'color: #37474f; font-size: 200%; font-weight: 300'


def main():
    plot_settings = gui_utils.Plot_Settings()
    
    
    with ui.row():
        ui.label('Plots').style(head_style)
        #ui.select(['choose method'], label='Plot Method').bind_value(plot_settings, 'method')
        ui.button('Plot Properties')
    
    # fig = go.Figure()
    # plot = ui.plotly(fig).classes('w-full h-full')
    
    
    fig = go.Figure(go.Scatter(x=[1, 2, 3, 4], y=[1, 2, 3, 2.5]))
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
    ui.plotly(fig).classes('w-full h-full')
    
    return plot_settings
    
## don't really need ui vals for plot properties, plotly plots are inveractive
def props_dialog():
    with ui.dialog() as dialog, ui.card():
        with ui.column():
            with ui.row():
                ui.label('x:')
                ui.input(placeholder='min')
                ui.input(placeholder='max')
        
    return
    
    
def default():
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