.. Baecon documentation master file, created by
   sphinx-quickstart on Sun Apr  2 16:14:48 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Baecon Documentation
====================

**Baecon** (/ˈbiːkən/), or **Ba**\ sic **E**\ xperiment **Con**\ trol, is a Python library 
for controlling laboratory instruments to perform experiments. 

Measurement automation, in its most *basic* terms, consists of the computer 
sending a message to the instrument to change a parameter and/or get the value
of that parameter or other parameters. Baecon is structed around the this idea
by limiting the methods used to communicate with the instruments. 

The simplicity of Baecon is partially accomplished by shifting the heavy 
lifting to the user to build modules for instruments that follow the limited 
communication methods. With users writing their own modules, Baecon isn't 
limited to any specific communication protocol. We have a few examples of 
instrument modules, and we hope to provide more modules we and others user 
contribute there own.

Baecon operates with a command line interface or with the GUI made with
the `NiceGUI <https://nicegui.io/>`_ package. 

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   base
   device
   engine
   data
   utils


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

