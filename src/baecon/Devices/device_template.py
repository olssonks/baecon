from typing import Optional

from baecon import Device

## import any other packages needed for the device


class DeviceTemplate(Device):
    """Template for starting a new Device class.

    - First determine what properties of the device you would like to regularly change
      from measurement to measurement. Examples are output power, exposure time, voltage
      range, etc. These will be listed in the :py:attr:`self.parameters` dictionary of the device.

    - Next determine what properties of the device that will need to be specified, but do
      not change often. Examples are connection info (IPaddress, device name),
      communication formatting, input/output channel, etc. These will be in the
      :py:attr:`self.latent_parameters` dictionary.

    - **Note**: It may be good to look into what info is needed for the methods needed
      to :py:meth:`read` and :py:meth:`write` to the device in order to determine the above parameters.

    - Create a method for connecting to the device :py:meth:`connect_to_device` which uses
      the necessary parameters and latent parameters, either by the default values
      defined in the class or a configuration ditionary/file. This method should return
      an Python object used to communicate with the device, and be stored in a class
      atrribute like :py:attr:`self.connected_device`.

    - The :py:meth:`read` and :py:meth:`write` methods must take on the arguements
      `(self, parameter, value)`. This is crucial for the interchangability of devices.

    - The rest of the methods in the class will need to be used to allow the :py:meth:`read`
      and :py:meth:`write` methods to follow the restrictions mention above.
    """

    def __init__(self, configuration: Optional[dict] = None) -> None:
        """Initialize class with default or supplied info.
           Default values for the parameters are specific here and a connection
           to the device is made.

        Args:
            configuration (dict, optional): Dictionary of parameter configurations.
                If None, the parameter vallues specified in the class will be used.
        """
        super.__init__(configuration)

        return

    # Writing and Reading will be device specfic as connect types and command are all different
    def write(self, parameter, value):
        """Add functionally to change the `parameter` to `value` on the
            instrument.

        Args:
            parameter (_type_): _description_
            value (_type_): _description_
        """
        return

    def read(self, parameter, value):
        """Add functionally to read the value of `parameter` from the instrument.

        Args:
            parameter (_type_): _description_
            value (_type_): _description_
        """
        return
