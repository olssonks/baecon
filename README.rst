.. image:: C:\Users\\walsworth1\Documents\\Jupyter_Notebooks\\baecon\\baecon_2.png

+++++++++++++++++++++++++++++++++
Baecon - Basic Experiment Control
+++++++++++++++++++++++++++++++++

**Baecon** (/ˈbiːkən/), or **Ba**\ sic **E**\ xperiment **Con**\ trol, is a Python library 
for controlling laboratory instruments to automate performing measurements. 

Measurement automation, in its most *basic* terms, consist of the computer 
sending a message to the instrument to change a parameter and/or get the value
of that parameter. Baecon is structed around the this by limiting the methods
used to communicate with the instrument. 

The simplicity of Baecon is partially accomplished by shifting the heavy 
lifting to the user to build the module for an instrument themselves to fit.
With users their own modules, Baecon isn't limited to any specific communication
protocol. We have a few examples of the instrument modules, and we hope to 
provide more modules user contribute there own.

Baecon operates with a command line interface or with the GUI made with
the `NiceGUI <https://nicegui.io/>`_ package. 


Still to do:
============

* Devices: PulseStreamer, Basler, TPI, Thorlabs stages, PulseBlaster 
* Data_Analysis modules
* Make unit tests

Overview
========

.. conver to table

Module, Purpose
`**baecon.base** <https://github.com/olssonks/baecon/blob/main/baecon/base.py>`_, Makes and organizes scans of instrument settings
`**baecon.device** <https://github.com/olssonks/baecon/blob/main/baecon/device/device.py>`_, Base class for experimental instruments
`**baecon.engine** <https://github.com/olssonks/baecon/blob/main/baecon/engine/engine.py>`_, Performs and controls the measurement
`**baecon.data** <https://github.com/olssonks/baecon/blob/main/baecon/data.py>`_, Data and analysis of measurements
`**baecon.utils** <https://github.com/olssonks/baecon/blob/main/baecon/utils.py>`_, File I/O and other utility functions



Installation
============
Blah blah blah

Getting Started
===============

A measurement in Baecon is defined by four properties:
* devices for acquiring data
* devices whos parameter is scanned through
* a list of the parameter scans to perform
* the repeats/averages of the whole measurement

These four properties are packaged in the Measurement_Settings class. 

License
=======
Baecon is open-source and available under the MIT License.

How to cite
===========
Arxiv then maybe Journal of Open Source Software