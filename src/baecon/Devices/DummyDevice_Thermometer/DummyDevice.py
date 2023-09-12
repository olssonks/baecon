from typing import Optional
from datetime import datetime

from baecon import Device

class dummy_connection:
    def connect(self, address):
        print(f"Connect to address {address}.")
        return self.make_measurement 
    def make_measurement(self, command):
        commands = {"measure temperature celcius": "100 C",
                    "measure temperature kelvin": "373 K",
                    "measure volume cubic cm": "0.1 cm^3",
                    "measure volume cubic mm": "100 mm^3"}
        return 

class DummyDevice(Device):

    def __init__(self, configuration: Optional[dict] = None):
        self.parameters = {
            "temperature": 100, ## C
            "volume": 0.1, ## cm^3
        }

        self.latent_parameters{
            "temperature_scale": "celcius",
            "volume_units": "cubic_cm",
            "address": "0.0.0.0"
        }

        super.__init__(configuration)

        self.thermometer_device = self.make_connection(configuration)
        
        return
    def make_connection(self, configuration:dict):
        address = configuration['address']
        return dummy_connection.connect(address)
    
    def write(self, parameter, value):
        ## this device cannot write
        return

    def read(self, parameter, value):
        msg = self.measure_dict["parameter"]() 

        return
    
    def measure_temp(self, scale):
        command_msg= "measure temperature " + scale
        temperature = dummy_connection.make_measurement(command_msg)
        return temperature
    
    def measure_vol(self, units)