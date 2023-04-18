.. image:: https://github.com/olssonks/baecon/blob/main/baecon.svg

|docs|

----

+++++++++++++++++++++++++++++++++
Baecon - Basic Experiment Control
+++++++++++++++++++++++++++++++++

**Baecon** (/ˈbiːkən/), or **Ba**\ sic **E**\ xperiment **Con**\ trol, is a Python library 
for controlling laboratory deivce to perform experiments.

Measurement automation, in its most *basic* terms, consists of the computer 
sending a message to a device to change a parameter and/or get the value
of that parameter or other parameters. Baecon is structed around the this idea
by limiting the methods used to communicate with the devices. A device in 
Baecon can only a read command or a write command *during the measurement procedure*. 
Before or after the measurement procedure devices are free to communicate for
preparing and configuring the device.

The simplicity of Baecon is partially accomplished by shifting the heavy 
lifting to the user to build modules for devices that follow the Baecon 
communication standards. With users writing their own modules, Baecon isn't 
limited to any specific communication protocol. We have a few examples of 
device modules, and we hope to provide more modules we and others user 
contribute there own.

All the information for the measurement is stored in ``JSON`` parsible configuration
files. A full measurement can be stored as a single file, or as individual 
configurations for the scan settings and devices. The default configuration 
file type is ``.toml``, but ``.yml`` and ``.json`` files are also compatible.

Baecon operates with a command line interface or with the GUI made with
the `NiceGUI <https://nicegui.io/>`_ package. 


Still to do:
============

* Devices: PulseStreamer, Basler, TPI, Thorlabs stages, PulseBlaster 
* Data_Analysis modules
* Make unit tests

Overview
========

.. convert to table

.. Module, Purpose
.. `**baecon.base** <https://github.com/olssonks/baecon/blob/main/baecon/base.py>`_, Makes and organizes scans of instrument settings
.. `**baecon.device** <https://github.com/olssonks/baecon/blob/main/baecon/device/device.py>`_, Base class for experimental instruments
.. `**baecon.engine** <https://github.com/olssonks/baecon/blob/main/baecon/engine/engine.py>`_, Performs and controls the measurement
.. `**baecon.data** <https://github.com/olssonks/baecon/blob/main/baecon/data.py>`_, Data and analysis of measurements
.. `**baecon.utils** <https://github.com/olssonks/baecon/blob/main/baecon/utils.py>`_, File I/O and other utility functions

+---------------------------------------------------------------------------------------------+--------------------------------------------------+
| Module                                                                                      | Purpose                                          |
+=============================================================================================+==================================================+
| `**baecon.base** <https://github.com/olssonks/baecon/blob/main/baecon/base.py>`_            | Makes and organizes scans of instrument settings |
+---------------------------------------------------------------------------------------------+--------------------------------------------------+
| `**baecon.device** <https://github.com/olssonks/baecon/blob/main/baecon/device/device.py>`_ | Base class for experimental instruments          |
+---------------------------------------------------------------------------------------------+--------------------------------------------------+
| `**baecon.engine** <https://github.com/olssonks/baecon/blob/main/baecon/engine/engine.py>`_ | Performs and controls the measurement            |
+---------------------------------------------------------------------------------------------+--------------------------------------------------+
| `**baecon.data** <https://github.com/olssonks/baecon/blob/main/baecon/data.py>`_            | Data and analysis of measurements                |
+---------------------------------------------------------------------------------------------+--------------------------------------------------+
| `**baecon.utils** <https://github.com/olssonks/baecon/blob/main/baecon/utils.py>`_          | File I/O and other utility functions             |
+---------------------------------------------------------------------------------------------+--------------------------------------------------+


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


.. |docs| image:: https://readthedocs.org/projects/docs/badge/?version=latest
    :alt: Documentation Status
    :scale: 100%
    :target: https://baecon.readthedocs.io/en/latest/