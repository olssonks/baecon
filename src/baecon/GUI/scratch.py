# -*- coding: utf-8 -*-
"""
Created on Wed Jan 18 15:21:13 2023

@author: walsworth1
"""

from nicegui import ui
from dataclasses import dataclass, asdict
import asyncio
import time

# import utils

import numpy as np

# @dataclass
# class holder:
#     value: any = ""
#     def update(self, new_value):
#         self.value = new_value

# rand = holder(str(np.random.random(1)))

# card_holder = holder()
# def update_card():
#     rand.update(str(np.random.random(1)))
#     card_holder.value.clear()
#     with card_holder.value:
#         make_card()
#     return

# def make_card():
#     ui.label(str(rand.value))
#     with ui.column().classes('w-full'):
#         with ui.row().classes('w-full no-wrap items-center'):
#             ui.label('Label').classes('w-full justify-right')
#             ui.input(placeholder='Put Label')
#         with ui.row().classes('w-full no-wrap items-center'):
#             ui.label('Longer Label').classes('w-full justify-right')
#             ui.input(placeholder='Put Label')
#     return

# def test():
#     print('hello')
#     return
# with ui.expansion('Expand').props('after-hide') as exp:
#     ui.label('Hello')
# exp.on('hide', test)

test = """<style>
.text-brand {
  color: #a2aa33 !important;
}
.bg-brand {
  background: #a2aa33 !important;
} </style>"""

ui.add_head_html(test)

with ui.card().classes("bg-brand"):
    with ui.row().classes("no-wrap items-stretch"):
        with ui.column().classes("grid justify-items-stretch"):
            with ui.card().classes("h-full justify-between"):
                ui.button("y")
                ui.button("y")
                ui.button("y")
            with ui.card().classes("place-content-center h-full"):
                ui.button("y")
        with ui.column():
            with ui.card():
                ui.button("y").classes("h-96")
            with ui.card():
                ui.button("y")


ui.run(port=8082)
