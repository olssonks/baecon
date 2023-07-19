import sys

sys.path.insert(0, 'C:\\Users\\walsworth1\\Documents\\Jupyter_Notebooks\\baecon')
import time
import baecon as bc

import queue, threading, copy, asyncio
from dataclasses import dataclass, field
import numpy as np
import xarray as xr

from nicegui import ui, app
import plotly.graph_objects as go


def measure_thread():
    return


def data_thread():
    return


def perform_measurement():
    return


async def main():
    task = asyncio.create_task(perform_measurement(ms, md))
    await task
