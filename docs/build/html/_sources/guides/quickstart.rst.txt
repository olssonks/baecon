+++++++++++
Quick start
+++++++++++

A brief summary of what is needed to run a measurement.

Acquisition
+++++++++++
Set up configuration file for the acquisition device in `/acq_dev_config.toml`.

Example configruation for NIDAQ: ::

    name = 'Daq1'

    device = 'NIDAQ_Base'

    [parameters]
    device_name = "Dev1"
    read_sample_rate = 50000.0
    read_sample_rate_out = 1000.0
    read_samples_per_chan = 10000.0
    reads_per_sample = 1
    read_samples_total = 10000.0
    read_channels = ['ai1']

    [latent_parameters]
    units = "volts"
    voltage_limits = 2
    terminal_type = "RSE"
    read_clock_source = "OnboardClock"
    read_active_edge = "rising_edge"
    read_sample_mode = "finite_samples"
    read_timeout = "infinite_timeout"
    read_trigger_channel = 'PFI0'
    read_fill_mode = 'by_channel'

    [preparations]
    read = ['analog_input']
    read_method = 'analog_input'


Scan Device
+++++++++++
Set up configuration file for the scan device in `/scan_dev_config.toml`.

Example configuration for SRS SG380: ::

    name = "SG1"

    device = "SG380"

    [parameters]
    frequency = 2.8e3
    phase = 0
    amplitude = 0.0
    modulation_enabled = false
    modulation_type = 'IQ'
    modulation_function = 'External'

    [latent_parameters]
    IPaddress = '10.229.42.86'
    port = '5025'

    ## Alternatively use GPIB
    ## GPIB = '27'


Scan Settings
+++++++++++++

Set up the configuration for the scan in `/scan_config.toml`. Make sure the 
parameter names match those in `/scan_dev_config.toml`.

Example scan settings for scanning the frequency of an SG380: ::

    name = 'SG1'
    device = 'SG380'
    parameter = 'frequency'
    min = 1
    max = 2
    points = 10
    repetitions = 1
    scale = 'linear'
    randomize = 'False'
    note = ''
    
Measurement Generation File
++++++++++++++++++++++++++++++++++

Collect the previous files in a file `/generate_config.toml`. For the 
`scan_collection`, the name must be {name}-{parameter}, with name being that of 
the scan device, and parameter is that to be scanned. 

The file should look like this: ::

    averages = 1

    [acquisition_devices]
    "Daq1" = ""

    [scan_devices]
    "SG1" = ""

    [scan_collection]
    "SG1-frequency" = "./scan_config.toml"

Then, the measurement configruation can be made through the 
`generate_measurement_configuration.py` script in `tools`. The command line 
arguments are `-g` for the generation file and `-o` for the file to save the
generated measuremene configruation.

The prompt looks like: ::
    
    >> python -m generate_measurement_configuration.py -g generate_config.toml -o measurement_config.toml

The full measurement configuration looks like: ::
    
    averages = 1

    [acquisition_devices.Daq1]
    name = "Daq1"
    device = "NIDAQ_Base"

    [scan_devices.SG1]
    name = "SG1"
    device = "SG380"

    [scan_collection.SG1-frequency]
    name = "SG1"
    device = "SG380"
    parameter = "frequency"
    min = 1
    max = 2
    points = 10
    repetitions = 1
    scale = "linear"
    randomize = "False"
    note = ""

    [acquisition_devices.Daq1.parameters]
    device_name = "Dev1"
    read_sample_rate = 50000.0
    read_sample_rate_out = 1000.0
    read_samples_per_chan = 10000.0
    reads_per_sample = 1
    read_samples_total = 10000.0
    read_channels = [ "ai1",]

    [acquisition_devices.Daq1.latent_parameters]
    units = "volts"
    voltage_limits = 2
    terminal_type = "RSE"
    read_clock_source = "OnboardClock"
    read_active_edge = "rising_edge"
    read_sample_mode = "finite_samples"
    read_timeout = "infinite_timeout"
    read_trigger_channel = "PFI0"
    read_fill_mode = "by_channel"

    [acquisition_devices.Daq1.preparations]
    read = [ "analog_input",]
    read_method = "analog_input"

    [scan_devices.SG1.parameters]
    frequency = 2800.0
    phase = 0
    amplitude = 0.0
    modulation_enabled = false
    modulation_type = "IQ"
    modulation_function = "External"

    [scan_devices.SG1.latent_parameters]
    IPaddress = "10.229.42.86"
    port = "5025"


Run Measurement
+++++++++++++++

With the generated measurement configuration file, the measurement can be run 
with the `run_baecon_measurement.py` script. The command line ar are `-c` for
the config file and `-o` for the file saving the data.

The prompt looks like: ::

    >> python -m run_baecon_measurement.py -c generate_config.toml -o measurement_data.zarr
<<<<<<< HEAD
    
    
Data
++++

The raw data is an ``xarray.Dataset`` saved as a ``zarr`` file. For example,
if we used the frequency scan above (1 to 2 in 10 points) and the DAQ measuring
5 samples per frequency (instead of 1000), the ``Dataset`` accessing the 
data would look like ::
    
    In [58]: data = xarray.open_zarr('measurement_data.zarr')
    In [59]: data
    Out[59]:
    <xarray.DataArray (frequency: 10, Daq: 5)>
    array([[0.06845721, 0.45418917, 0.02972986, 0.81162959, 0.84204303],
        [0.95977484, 0.38657898, 0.74791127, 0.18752947, 0.3381117 ],
        [0.85138632, 0.27183962, 0.21410397, 0.94043282, 0.85798746],
        [0.56255822, 0.88850187, 0.33879754, 0.32365884, 0.29647427],
        [0.75152129, 0.00900204, 0.94235881, 0.86847581, 0.63654923],
        [0.43740333, 0.49427344, 0.72159747, 0.94617294, 0.29943479],
        [0.95340883, 0.71562499, 0.94736602, 0.36457894, 0.69176947],
        [0.21102173, 0.32918041, 0.24226033, 0.64908989, 0.1524366 ],
        [0.80007326, 0.98316083, 0.35993896, 0.39380294, 0.51551403],
        [0.65309653, 0.48531812, 0.77776049, 0.73338655, 0.12133202]])
    Coordinates:
    * frequency  (frequency) float64 1.0 1.111 1.222 1.333 ... 1.778 1.889 2.0
    Dimensions without coordinates: Daq

The data can be indexed by the ``frequency`` coordinates ::

    In [60]: data.sel({'frequency':1.1111}, method='nearest')
    Out[60]: 
    <xarray.DataArray (Daq: 5)>
    array([0.95977484, 0.38657898, 0.74791127, 0.18752947, 0.3381117 ])
    Coordinates:
        frequency  float64 1.111
    Dimensions without coordinates: Daq
    
The ``method='nearest'`` is useful for indexing coordinates who's values may 
be complicated floats. The values of a coordinates can be accessed by ::

    In [61]: data.coords['frequency'].values
    Out[61]:
    array([1.        , 1.11111111, 1.22222222, 1.33333333, 1.44444444,
        1.55555556, 1.66666667, 1.77777778, 1.88888889, 2.        ])
    
And the full data can be accessed simply by ::

    In [62]: data.values
    Out[62]:
    array([[0.06845721, 0.45418917, 0.02972986, 0.81162959, 0.84204303],
        [0.95977484, 0.38657898, 0.74791127, 0.18752947, 0.3381117 ],
        [0.85138632, 0.27183962, 0.21410397, 0.94043282, 0.85798746],
        [0.56255822, 0.88850187, 0.33879754, 0.32365884, 0.29647427],
        [0.75152129, 0.00900204, 0.94235881, 0.86847581, 0.63654923],
        [0.43740333, 0.49427344, 0.72159747, 0.94617294, 0.29943479],
        [0.95340883, 0.71562499, 0.94736602, 0.36457894, 0.69176947],
        [0.21102173, 0.32918041, 0.24226033, 0.64908989, 0.1524366 ],
        [0.80007326, 0.98316083, 0.35993896, 0.39380294, 0.51551403],
        [0.65309653, 0.48531812, 0.77776049, 0.73338655, 0.12133202]])
=======

>>>>>>> dev
