.. Baecon documentation master file, created by
   sphinx-quickstart on Sun Apr  2 16:14:48 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. raw:: html

    <style> .red {color:#aa0060; font-weight:bold; font-size:16px} </style>

.. role:: red

++++++++++++++++++++
Baecon Documentation
++++++++++++++++++++

:red:`Baecon` (/ˈbiːkən/), or :red:`Ba`\ sic :red:`E`\ xperiment :red:`Con`\ trol, is a Python library 
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

.. .Module, Purpose
.. `baecon.base <https://github.com/olssonks/baecon/blob/main/baecon/base.py>`_, Makes and organizes scans of instrument settings
.. `baecon.device <https://github.com/olssonks/baecon/blob/main/baecon/device/device.py>`_, Base class for experimental instruments
.. `baecon.engine <https://github.com/olssonks/baecon/blob/main/baecon/engine/engine.py>`_, Performs and controls the measurement
.. `baecon.data <https://github.com/olssonks/baecon/blob/main/baecon/data.py>`_, Data and analysis of measurements
.. `baecon.utils <https://github.com/olssonks/baecon/blob/main/baecon/utils.py>`_, File I/O and other utility functions

+-----------------------------------------------------------------------------------------+--------------------------------------------------+
| Module                                                                                  | Purpose                                          |
+=========================================================================================+==================================================+
| `baecon.base <https://github.com/olssonks/baecon/blob/main/baecon/base.py>`_            | Makes and organizes scans of instrument settings |
+-----------------------------------------------------------------------------------------+--------------------------------------------------+
| `baecon.device <https://github.com/olssonks/baecon/blob/main/baecon/device/device.py>`_ | Base class for experimental instruments          |
+-----------------------------------------------------------------------------------------+--------------------------------------------------+
| `baecon.engine <https://github.com/olssonks/baecon/blob/main/baecon/engine/engine.py>`_ | Performs and controls the measurement            |
+-----------------------------------------------------------------------------------------+--------------------------------------------------+
| `baecon.data <https://github.com/olssonks/baecon/blob/main/baecon/data.py>`_            | Data and analysis of measurements                |
+-----------------------------------------------------------------------------------------+--------------------------------------------------+
| `baecon.utils <https://github.com/olssonks/baecon/blob/main/baecon/utils.py>`_          | File I/O and other utility functions             |
+-----------------------------------------------------------------------------------------+--------------------------------------------------+
|                                                                                         |                                                  |
+-----------------------------------------------------------------------------------------+--------------------------------------------------+
.. toctree::
   :maxdepth: 1
   :caption: Contents:

   base
   device
   engine
   data
   utils
   todo

Indices and tables
==================

* :py:mod:`base`
* :py:class:`base.Device`
* :py:mod:`engine`
* :py:mod:`data`
* :py:mod:`utils`


* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

