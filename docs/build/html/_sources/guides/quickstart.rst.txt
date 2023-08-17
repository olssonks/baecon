.. _quickstart:

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
    
    
Data
++++

The raw data is an ``xarray.Dataset`` saved as a ``zarr`` file. For example,
if we used the frequency scan above (1 to 2 in 10 points) and the DAQ measuring
5 samples per frequency (instead of 1000), the ``Dataset`` accessing the 
data would look like ::
    
    In [58]: data = xarray.open_zarr('measurement_data.zarr')
    In [59]: data
    Out[59]:
    <xarray.Dataset>
    Dimensions:    (frequency: 10, Daq: 5)
    Coordinates:
    * frequency  (frequency) float64 1.0 1.111 1.222 1.333 ... 1.778 1.889 2.0
    * Daq        (Daq) int32 0 1 2 3 4
    Data variables:
        Daq_0      (frequency, Daq) float64 0.3101 0.1398 0.8195 ... 0.2323 0.07908
        Coordinates:
        * frequency  (frequency) float64 1.0 1.111 1.222 1.333 ... 1.778 1.889 2.0
        Dimensions without coordinates: Daq
        
Here ``Daq`` refers to the coordinate, which is the sample index, and ``Daq_0``
is the first measurement made with ``Daq`` at each frequency. To access the data
array ``Daq_0``, we can index the ``Dataset`` like a dictionary ::
    
    In [40]: meas_0 = data['Daq_0']

    In [41]: meas_0
    Out[41]:
    <xarray.DataArray 'Daq_0' (frequency: 10, Daq: 5)>
    array([[0.31007643, 0.13983319, 0.81946348, 0.06386373, 0.84451861],
        [0.72068642, 0.16112617, 0.17229398, 0.23464845, 0.91359624],
        [0.50211397, 0.63015773, 0.87281202, 0.23805703, 0.16854426],
        [0.12987982, 0.28634581, 0.24274497, 0.98717013, 0.57904668],
        [0.18018263, 0.25442135, 0.62867808, 0.0741044 , 0.86772646],
        [0.61305147, 0.65637227, 0.3857262 , 0.68949025, 0.22860304],
        [0.97682538, 0.05933332, 0.00242159, 0.81892933, 0.10490373],
        [0.34668295, 0.83486479, 0.54124973, 0.69320961, 0.19347784],
        [0.8779518 , 0.24962297, 0.43079303, 0.90662706, 0.34527662],
        [0.50067085, 0.83609408, 0.51693081, 0.23233917, 0.07908146]])
Coordinates:
  * frequency  (frequency) float64 1.0 1.111 1.222 1.333 ... 1.778 1.889 2.0
  * Daq        (Daq) int32 0 1 2 3 4

Then in the ``DataArray``, the data can be indexed by the ``frequency`` 
coordinates ::

    In [43]: meas_0.sel({'frequency':1.1111}, method='nearest')
    Out[43]:
    <xarray.DataArray 'Daq_0' (Daq: 5)>
    array([0.72068642, 0.16112617, 0.17229398, 0.23464845, 0.91359624])
    Coordinates:
        frequency  float64 1.111
    * Daq        (Daq) int32 0 1 2 3 4
    
The ``method='nearest'`` is useful for indexing coordinates who's values may 
be complicated floats. The values of a coordinates can be accessed by ::

    In [44]: meas_0.coords['frequency'].values
    Out[44]:
    array([1.        , 1.11111111, 1.22222222, 1.33333333, 1.44444444,
        1.55555556, 1.66666667, 1.77777778, 1.88888889, 2.        ])
    
And the full data can be accessed simply by ::

    In [45]: meas_0.values
    Out[45]:
    array([[0.31007643, 0.13983319, 0.81946348, 0.06386373, 0.84451861],
        [0.72068642, 0.16112617, 0.17229398, 0.23464845, 0.91359624],
        [0.50211397, 0.63015773, 0.87281202, 0.23805703, 0.16854426],
        [0.12987982, 0.28634581, 0.24274497, 0.98717013, 0.57904668],
        [0.18018263, 0.25442135, 0.62867808, 0.0741044 , 0.86772646],
        [0.61305147, 0.65637227, 0.3857262 , 0.68949025, 0.22860304],
        [0.97682538, 0.05933332, 0.00242159, 0.81892933, 0.10490373],
        [0.34668295, 0.83486479, 0.54124973, 0.69320961, 0.19347784],
        [0.8779518 , 0.24962297, 0.43079303, 0.90662706, 0.34527662],
        [0.50067085, 0.83609408, 0.51693081, 0.23233917, 0.07908146]])