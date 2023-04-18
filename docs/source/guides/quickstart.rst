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

