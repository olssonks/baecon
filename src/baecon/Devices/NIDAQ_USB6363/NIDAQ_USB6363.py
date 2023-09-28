"""
.. todo::
   Needs to be tested. 
"""
## need to import class not the full .py module
from baecon.Devices.NIDAQ_Base.NIDAQ_Base import NIDAQ_Base
from baecon.Devices.NIDAQ_Base.PyDAQmx_ref_values import PyDAQmx_lookup_value


class NIDAQ_USB6363(NIDAQ_Base):
    """
    Device class for NI DAQ model USB 6363.

    Only extra feature used over the base class is analog start trigger.
    Other functionality can be implemented if usedful.

    Args:
        NIDAQ_Base (class): Parent class and base class for NI DAQ Devices.
    """

    def __init__(self, configuration: dict) -> None:
        ## additional 6363 parameters
        self.latent_parameters = {
            "input_start_trigger_channel": "",
            "input_start_trigger_active_edge": "rising_edge",
            "output_start_trigger_channel": "",
            "output_start_trigger_active_edge": "rising_edge",
            "analog_trigger_level": 0.5,
        }
        super().__init__(
            ## ** on dicts appends them together
            ## want configuration last, so that it overwrites default values.
            {**self.latent_parameters, **configuration},
        )

        return

    def prepare_input_start_trigger(self) -> None:
        """Prepares task to start based on a trigger from the specified channel.

        Configures both analog or digital start triggers, depending on
        the name of the channel: PFI or APFI.
        """
        try:
            trigger_edge = PyDAQmx_lookup_value(
                self.latent_parameters["output_start_trigger_active_edge"]
            )
            chan_name = (
                "/"
                + self.parameters["device_name"]
                + "/"
                + self.latent_parameters["output_trigger_channel"]
            )

            if "A" in self.parameters["output_trigger_channel"]:
                self.prepared_input_task.CfgAnlgEdgeStartTrig(
                    chan_name, trigger_edge, self.latent_parameters["analog_trigger_level"]
                )
            else:
                self.prepared_input_task.CfgDigEdgeStartTrig(chan_name, trigger_edge)

        except KeyError as e:
            print(
                f"{e} not found in read preparations or \
                  method listed, check preparations"
            )

    def prepare_output_start_trigger(self) -> None:
        """Prepares task to start based on a trigger from the specified channel.

        Configures both analog or digital start triggers, depending on
        the name of the channel: PFI or APFI.

        """
        try:
            trigger_edge = PyDAQmx_lookup_value(
                self.latent_parameters["input_start_trigger_active_edge"]
            )
            chan_name = (
                "/"
                + self.parameters["device_name"]
                + "/"
                + self.latent_parameters["input_trigger_channel"]
            )

            if "A" in self.parameters["input_trigger_channel"]:
                self.prepared_output_task.CfgAnlgEdgeStartTrig(
                    chan_name, trigger_edge, self.latent_parameters["analog_trigger_level"]
                )
            else:
                self.prepared_output_task.CfgDigEdgeStartTrig(chan_name, trigger_edge)

        except KeyError as e:
            print(
                f"{e} not found in read preparations or \
                  method listed, check preparations"
            )

        return

    def preparation_options(self) -> tuple[dict, dict, dict]:
        """
        Defines available preparation options.

        Overrides the method found in the child class, but copies all available
        Base options and methods, and adds those specific to the USB 6363.

        Returns:
            tuple[dict, dict, dict]: Tuple of dictionarys corresponding to the
                available options for preparing a input or ouput methd,
                available input methods, and available output methods.
        """
        preparation_types = {
            "analog_input": self.prepare_analog_input,
            "input_digital_trigger": self.prepare_input_digital_trigger,
            "output_digital_trigger": self.prepare_output_digital_trigger,
            "input_start_triger": self.prepare_input_start_trigger,
            "output_start_triger": self.prepare_output_start_trigger,
        }
        input_methods = {"analog_input": self.read_analog_input}
        output_methods = {"analog_output": self.write_analog_output}

        return preparation_types, input_methods, output_methods
