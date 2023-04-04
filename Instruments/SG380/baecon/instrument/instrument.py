"""
Notes:
   - configuration will be a dictionary, read from some file in engine (toml, yaml, json, etc.)
   
   - set_parameter calls write calls other function (and may one more function)
       - calling three functions slow??? Speed up?
"""
from .. import utils
import os, fnmatch
import numpy as np

Instruments_directory = "C:\\Users\\walsworth1\\Documents\\Jupyter_Notebooks\\baecon\\Instruments"

class Instrument:
    """Experimental Instruments are designated into two catagories: **scanning instruments** 
        and **acquisition instruments**, with this class serving as 
        the base class for both. Scanning instruments are the devices whose 
        properties are changed from reading to reading. Acquisition instruments 
        perform the reading after a property has changed. Instruments can be 
        both scanning and aquisistioninstruments, like a sourcemeter. The 
        distinction between the two happens when the :class: `Measurement_Settings`
        are defined.
        
        Note:
            In the user defined child classes (e.g, SG380),
            users will need to override the parameters and latent_paramenters 
            atrributes, and the read and write methods. Additional methods in the 
            child class will needed to be defined to support these required 
            attributes and methods.

        Attributes:
            name (str): Alias for the device to distringuish it from the 
                same instrument class. Example: SG1 for a signal generator.
            parameters(dict): Properties of the device that would be scanned through
                in an measurement sequence. Examples: voltage, frequency, 
                power, ...
            latent_parameters(dict): Properties of the device that would be the same
                from measurement to measurement. Exampls: connection settings 
                (e.g., IP address), output port, ...
            configuration (dict): Full configuration of the instrument: name, 
                parameters, and latent_parameters. Passing this dictionary 
                when creating the instrument object fully defines the 
                instrument.
            acq_data_size (int or tupel): Size of the data taken during a 
                reading by an acquisition instrument. For example, a single 
                reading of voltage would be size 1, size for an image would be
                the pixel dimensions. Child classes for instruments intended
                for acquisition should override this based on a parameter.
    """

    def __init__(self, configuration: dict = None) -> None:
        """Initializes instrument object with supplied configuration 
            dictionary. The supplied dictionary is then stored in the 
            configuration attribue.
            
            The configuration dictionary has the form::
                {'name': name string,
                 'parameters': parameter dictionary,
                 'latent_parameters': latent_parameter dictionary
                 }

        Args:
            configuration (dict): Full configuration of the instrument: name, 
                parameters, and latent_parameters. Passing this dictionary 
                when creating the instrument object fully defines the 
                instrument. 
        """
        if configuration == None:
            configuration = self.check_default_file()
        
        if not hasattr(self, "name"):
            self.name = 'No_name'
        if not hasattr(self, "parameters"):
            self.parameters = {}
        if not hasattr(self, "latent_parameters"):
            self.latent_parameters = {}
        self.acq_data_size = 1
        self.intitalize_parameters(configuration)
        self.configuration = configuration
        return
        
    def __del__(self)->None:
        """Specialized deletion procedure for instrument. For example, reset 
            the physica instrument when the object is deleted. 
        """        
        return

    def check_default_file(self):
        files = os.listdir(f'{Instruments_directory}/{self.__module__}')
        default = [file for file in files if 'default' in file]
        if len(default) == 1:
            config = utils.load_config(default[0])
        else:
            print('No configuration supplied.')
            print(f'No default_config file found in Instruments/{self.__module__}')
            config = {}
        return config
        
        
    def intitalize_parameters(self, configuration: dict):
        """Populate the parameters and latent_parameters attributes from 
            configuration dictionary.

        Args:
            configuration (dict): Full configuration of the instrument: name, 
                parameters, and latent_parameters. Passing this dictionary 
                when creating the instrument object fully defines the 
                instrument. 
        """    
        if "name" in configuration:
            self.name = configuration['name']
        else:
            print(f"No instrument name found, using default: {self.name}")
        if "parameters" in configuration:
            for key, value in list(configuration["parameters"].items()):
                self.parameters.update({key: value})
        else:
            print("No parameters found, using defaults")
            print(self.parameters)
        if "latent_parameters" in configuration:
            for key, value in list(configuration["latent_parameters"].items()):
                self.latent_parameters.update({key: value})
        else:
            print('No parameters found, using defaults')
            print(self.latent_parameters)
        return

    def update_configuration(self):
        attrs = dir(self)
        for key in list(self.configuration.keys()):
            if key in attrs:
                self.self.configuration[key] = self.__getattribute__(key)
        return

    # Writing and Reading will be device specfic as connect types and command are all different
    def write(self, parameter, value):
        """_summary_

        Args:
            parameter (_type_): _description_
            value (_type_): _description_
        """
        return

    def read(self, parameter, value):
        """_summary_

        Args:
            parameter (_type_): _description_
            value (_type_): _description_
        """
        return
        
    def update_instrument(self):
        for param, value in list(merge([self.parameters, 
                                 self.latent_parameters]).items()):
            self.write(param, value)
        return

    def set_parameter(self, parameter, value) -> None:
        self.write(parameter, value)
        self.parameters[parameter] = value
        return

    def get_parameter(self, parameter, value):
        value = self.read(parameter)
        self.parameters[parameter] = value
        return value


    def close_instrument(self) -> None:
        return


# end Instrument class
