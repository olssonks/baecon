import os
from abc import ABC, abstractmethod
from pathlib import Path

DEVICES_DIRECTORY = Path(__file__).parent.parent.resolve() / "Devices"


## abstractmethods must be redefined in child class
class Device(ABC):
    """Class for handling control and communication with experimental devices.

    Experimental devices are designated into two catagories: **scanning devices**
    and **acquisition devices**, with this class serving as
    the base class for both. Scanning devices are the devices whose
    properties are changed from reading to reading. Acquisition devices
    perform the reading after a property has changed. Devices can be
    both scanning and aquisistion instruments, like a sourcemeter. The
    distinction between the two happens when the :py:class:`Measurement_Settings<baecon.base.Measurement_Settings>`
    are defined.

     Note:
         In the user defined child classes (e.g, SG380),
         users will need to override the :py:attr:`Device.parameters` and
         :py:attr:`.Device.latent_paramenters` atrributes, and the :py:func:`Device.read`
         and :py:func:`Device.write` methods. Additional methods in the child class
         will needed to be defined to support these required attributes
         and methods.
     Attributes:
         name (str): Alias for the device to distringuish it from the
             same device class. Example: SG1 for a signal generator.
         parameters(dict): Properties of the device that would be scanned through
             in an measurement sequence. Examples: voltage, frequency,
             power, ...
         latent_parameters(dict): Properties of the device that would be the same
             from measurement to measurement. Exampls: connection settings
             (e.g., IP address), output port, ...
         configuration (dict): Full configuration of the device: name,
             parameters, and latent_parameters. Passing this dictionary
             when creating the device object fully defines the
             device. Used to save/load device into the measurement.
         acq_data_size (int or tupel): Size of the data taken during a
             reading by an acquisition device. For example, a single
             reading of voltage would be size 1, size for an image would be
             the pixel dimensions. Child classes for devices intended
             for acquisition should override this based on a parameter.
    """

    def __init__(self, configuration: dict) -> None:
        """Initializes device object with supplied configuration dictionary.
           The supplied dictionary is then stored in the configuration attribue.
           The configuration dictionary has the form::

                {'name': name string,
                'parameters': parameter dictionary,
                'latent_parameters': latent_parameter dictionary}

        Args:
            configuration (dict): Full configuration of the device: name,
                parameters, and latent_parameters. Passing this dictionary
                when creating the device object fully defines the device.
        """

        if configuration is None:
            configuration = self.check_default_file()

        if not hasattr(self, "name"):
            self.name = "No_name"
        if not hasattr(self, "parameters"):
            self.parameters: dict = {}
        if not hasattr(self, "latent_parameters"):
            self.latent_parameters: dict = {}
        self.acq_data_size = 1
        self.intitalize_parameters(configuration)
        self.configuration = configuration
        self.gui_router = None
        return

    def __del__(self) -> None:
        """Specialized deletion procedure for device. For example, reset
        the physical device when the object is deleted.
        """

        return

    def check_default_file(self):
        files = os.listdir(f"{DEVICES_DIRECTORY}/{self.__module__}")
        default = [file for file in files if "default" in file]
        if len(default) == 1:
            from baecon.utils import utils

            config = utils.load_config(default[0])
        else:  ## should be logging
            print("No configuration supplied.")
            print(f"No default_config file found in Device/{self.__module__}")
            config = {}
        return config

    def intitalize_parameters(self, configuration: dict):
        """Populate the parameters and latent_parameters attributes from configuration dictionary.

        Args:
            configuration (dict): Full configuration of the instrument: name,
                parameters, and latent_parameters. Passing this dictionary
                when creating the device object fully defines the
                device.
        """

        if "name" in configuration:
            self.name = configuration["name"]
        else:  ## shhould be logging
            print(f"No device name found, using default: {self.name}")
            configuration.update({"name": self.name})
        if "parameters" in configuration:
            for key, value in list(configuration["parameters"].items()):
                self.parameters.update({key: value})
        else:  ## shhould be logging
            print("No parameters found, using defaults")
            print(self.parameters)
            configuration.update({"parameters": self.parameters})
        if "latent_parameters" in configuration:
            for key, value in list(configuration["latent_parameters"].items()):
                self.latent_parameters.update({key: value})
        else:  ## shhould be logging
            print("No parameters found, using defaults")
            print(self.latent_parameters)
            configuration.update({"latent_parameters": self.latent_parameters})
        return

    def update_configuration(self):
        attrs = dir(self)
        for key in list(self.configuration.keys()):
            if key in attrs:
                self.configuration[key] = self.__getattribute__(key)
        ##Put type of device in configuration, otherwise it puts the whole python object name
        self.configuration["device"] = self.__module__
        return

    def update_device(self):
        for param, value in list({**self.parameters, **self.latent_parameters}.items()):
            self.write(param, value)
        self.update_configuration()
        return

    def set_parameter(self, parameter, value) -> None:
        """
        .. todo::
            This method seems to not be used.

        """
        self.write(parameter, value)
        self.parameters[parameter] = value
        return

    def get_parameter(self, parameter, value):
        """
        .. todo::
            This method seems to not be used.

        """
        value = self.read(parameter)
        self.parameters[parameter] = value
        return value

    def get_device_gui(self) -> None:
        print("This device does not have a GUI.")  ## should be logging
        return

    ## abstarctmethods must be redefined in child class

    # Writing and Reading will be device specfic as connection types
    # and commands are different for all devices
    @abstractmethod
    def write(self, parameter, value):
        """Function used to write parameter to device during a measurement.
           The user decides how this write command is performed in the
           device child class. ``write`` only takes two inputs the parameter
           to write to, and the value to write. Values need not be numeric.

        Args:
            parameter (str): Device parameter to write to.
            value (str): Value to write to device.
        """
        return

    @abstractmethod
    def read(self, parameter, value):
        """Function used to read parameter from device during a measurement.
           The user decides how this write command is performed in the
           device child class. ``read`` only takes two inputs the parameter
           to read, and the value which can be used to format how the parameter
           is read, like units for example. If value is not required for the
           device type, set it to ``value=None`` in the overriding
           ``read function`` of in child class.

        Args:
            parameter (str): Device parameter to read.
            value (str): Value (i.e., arguement) if needed for specific device.

        Returns:
            Reading from device.
        """
        return

    @abstractmethod
    def enable_output(self, value: bool):
        """Enables or disables the device output based on value.
           Mostly used in the GUI to turn on/off output of constant devices.

        Args:
            value (bool): 0 or 1 for off or on
        """
        return

    def close_device(self) -> None:
        """
        .. todo::
            Need to figure out if we want devices to have this method.
            If so, need to be an abstract method.

        """
        return
