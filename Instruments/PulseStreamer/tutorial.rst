+++++++++++++++++++++++++++
Device Construction Example
+++++++++++++++++++++++++++

This expample will explain the process of writing a new :py:class:`Device`, using
the PulseStreamer device as an example. Hopefully, it serves somewhat as a 
tutorial of the thought process behind building a new :py:class:`Device`.

Find Communication Protocol
+++++++++++++++++++++++++++
The first thing to do when writing a new instrument class is to determine
what the protocol or method is for talking to the device with the computer. Some
devices have their own Python packages for communication, like the NIDAQs which uses
`PyDAQmx <https://pythonhosted.org/PyDAQmx/>`_ 
and PulseStreamer which has it's own package `pulsestreamer <https://www.swabianinstruments.com/static/documentation/PulseStreamer/>`_. 
Other devices have generic protocols, like the SRS SG380 signal generators, 
which uses the IEEE-488.2 communication standard. These units can 
use `PyVisa <https://pyvisa.readthedocs.io/en/latest/>`_ over GPIB 
or TCPIP connections. Finally, some devices have a very low level interface, 
like the TPI signal generatores, which use binary commands sent over USB with 
the `serial` package.

The ``pulsestreamer`` API has methods for communicating with the device, so these
will be used when defining our ``read`` and ``write`` methods.

Determine Device Parameters
+++++++++++++++++++++++++++
Next is to determine which ``parameters`` of the device are **required** for it to
operate. 

For the PulseStreamer, the required parameters are:
    * IP address: need to communicate with the instrument
    * pulse sequence: defines the output of the device

This list of required parameters is quite small, and though the we could 
just use these parameters with the device, our options will be limited. Looking 
through the ``pulsestreamer`` documentation we can identify some other useful
paraeters:
    * n_runs: number of times the sequence is repeated
    * final state: output configuration once sequence ends

These provide a base for the :py:class:`Device` parameters will be, though 
we will likely add additionaly ``parameters`` needed for the methods we define in 
the next section.


Determine Measurement Methods
+++++++++++++++++++++++++++++
We now want to define what we want the device to be able to do during a 
measurement, while keeping in mind that all communciation to the device is
through the ``read`` and ``write`` methods. We'll likely need to add additional
parameters to the class to faciliate the limited communication (which is by
design).

The ``pulsestreamer`` outputs a pulse sequence to trigger other devices during
the measurement. The main things we want to change would be the start times
of various pulses, as well as the duration of these pulses. There is no 
built in function of the ``pulsestreamer`` that allows for automatically changing
these values in a pulse sequence, so we will need to implement these ourselves.

For example, we want the following command: ::
    write('tau', 500)
    
where some spacing ``tau`` between pulses is changed to 500. 

For this to happen, we need to know which pulses to change the spacing between. 
In addition, we want to know how to change the other pulses in the sequence 
should change with respect to the change ``tau``. Should the other pulse stay in
place, shift with ``tau``, etc.? So we will need some additional parameters in the
:py:class:`Device`. These parameters will be configured before the scan, so that
a scan through ``tau`` only writes the method: ``write('tau', xxx)``. 

Additional Parameters
---------------------
First, we need a method to know which pulse(s) to change. To do this, we need to
know the channel the pulse is on, and which pulse on that channel to change. So,
additional parameters to add are:
    * channel number: which channel the pulse is on
    * name of pulse: to distinguish it from other pulses with in the channel
    * name to scan: picking specific pulse

We also want a parameter to specify how other channels should change with
respect to scanning pulse.
    * shift_method: how to change channels with respect to scanning channel

Defining Methods
----------------

