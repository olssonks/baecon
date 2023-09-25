from typing import Callable, ClassVar

import pyvisa
from baecon import Device


class SG4400L(Device):
    def __init__(self, configuration: dict) -> None:
        self.parameters = {
            'output_status': "off",
            'frequency': 200,
            'amplitude': -30,
        }
        self.latent_parameters = {
            'address': None,
            "port": None,
        }
        super().__init__(configuration)

        self.SG4400L_connection = self.connect_to_SG4400L()

        return

    def connect_to_SG4400L(self):
        rm = pyvisa.ResourceManager("@py")

        if self.latent_parameters.get("address") is not None and not isinstance(
            self.latent_parameters.get('port'), str
        ):
            device_connection = rm.open_resource(
                "TCPIP0::"
                + self.latent_parameters.get('address')
                + "::"
                + self.latent_parameters.get('port')
                + "::SOCKET"
            )
            return device_connection

        if self.latent_parameters.get('address') is None and isinstance(
            self.latent_parameters.get('port'), str
        ):
            just_com_number = ''.join(
                char for char in self.latent_parameters.get('port') if char.isdigit()
            )

            device_connection = rm.open_resource(
                'ASRL' + just_com_number + '::INSTR',
                baud_rate=115200,
                data_bits=8,
            )
            return device_connection

        err_msg = "Double check connection parameters, only supply address and port \
        for TCPIP, or only port for USB/serial."
        print(err_msg)

        return

    def write(self, parameter, value):
        msg = some_function()  ## prepare a message to write to the device
        self.SG4400L_connection.write(msg)

        return

    def read(self, parameter, value=None):
        msg = some_other_function()  ## prepare a message to read a value from the device
        reading = self.SG4400L_connection.query(msg)

        return reading

    def freq(self, value, is_read):
        units = "MHZ"
        value = round(float(value), 6)  ## round to Hz

        if is_read is True:
            message = "FREQ:CW? " + str(value) + units
        else:
            message = "FREQ:CW " + str(value) + units

        return message

    def enable_output(self, value, is_read):
        return

    def amp(self, value, is_read):
        return

    commands = {'frequency': freq, 'amplitude': amp, 'output_status': enable_output}
