from typing import Optional

import numpy as np
import PyDAQmx

from baecon import Device
from baecon.Devices.NIDAQ_Base import PyDAQmx_lookup_value


class NIDAQ_Base(Device):
    """
    Base Device class for National Instrument DAQ devices.

    DAQmx is the API for communicating with the NIDAQS, and we use the third
    party PyDAQmx package. This package follows the syntaxt of the C/.NET API
    which has decent documentation provided by NI. PyDAQmx is essentially
    a wrapper for the C code. The Python API that NI
    itself provides is underdeveloped as this point (June 2023).

    NI DAQ communication is handled by tasks. You create a task of a certain
    type, e.g. analog volage input, and then configure its properties, like
    sample rate and voltage range. This base class can only have one read task
    and one write task. These tasks can contain multiple channels, but all
    channels will have the same properties. For more advanced task configuration
    a new child Device class will be needed.

    There are many different types of measurements the NI DAQs can do, but
    currently we only use analog voltage input and output tasks. Extending to
    digital input and output should be straight forward, but something like
    an analog strain gauge input may need its own child Device class.
    .. todo::
        Are read and write the only kinds of tasks we want for NI DAQs?
        Would couting tasks be any different? Other examples?
    """

    def __init__(self, configuration: Optional[dict] = None) -> None:
        self.parameters = {
            "input_sample_rate": 50e3,
            "input_samples_per_chan": 10e3,
            "inputs_per_sample": 1,
            "input_samples_total": 10e3,
            "input_channels": [],
            "output_sample_rate": 5e3,
            "output_samples_per_chan": 1e3,
            "outputs_per_sample": 1,
            "output_samples_total": 1e3,
            "output_channels": [],
        }
        self.latent_parameters = {
            "device_name": "",
            "units": "volts",
            "voltage_limits": 2,
            "terminal_type": "RSE",
            "input_clock_source": "OnboardClock",
            "input_active_edge": "rising_edge",
            "input_sample_mode": "finite_samples",
            "input_fill_mode": "by_channel",
            "input_timeout": "infinite_timeout",
            "input_trigger_channel": "",
            "output_units": "volts",
            "output_voltage_limits": "10",
            "output_sample_mode": "finite_samples",
            "output_clock_source": "OnBoardClock",
            "output_trigger_edge": "rising_edge",
            "output_fill_mode": "by_scan",
        }

        self.acquire_methods = [
            "analog_input",
            "digital_counts",
        ]

        super().__init__(configuration)

        self.preparations = ""

        self.prepared_input_task = None
        self.prepared_input_method = None
        self.input_data = []

        self.prepared_output_task = None
        self.prepared_output_method = None
        self.output_data = []

        self.prepare_device(configuration)

        self.set_acquisition_data_size()

        return

    def __del__(self) -> None:
        """Resets DAQ completely when object is closed
        Note:
            This may cause issues when use the same DAQ as multiple
            devices, e.g., reading analog inputs (acquisition)
            and writing analog outputs (scan).
        """
        PyDAQmx.ResetDevice(self.parameters["device_name"])
        return

    def enable_output(self, value: bool):
        ## this methods is required to be defined here by the Device class
        ## NIDAQ Base doesn't have any outputs
        return

    ## Writing and Reading will be device specfic as connect types and command are all different
    def write(self, parameter=None, value=None):
        pass
        return

    def read(self, parameter=None, value=None) -> np.ndarray:
        # self.start_task(self.prepared_input_task)
        self.prepared_input_method()
        return self.input_data

    def set_acquisition_data_size(self):
        self.acquisition_data_size = self.parameters["input_samples_total"]
        return

    def update_device(self):
        self.stop_task(self.prepared_input_task)
        self.clear_task(self.prepared_input_task)

        self.stop_task(self.prepared_output_task)
        self.clear_task(self.prepared_output_task)

        self.prepare_device(self.configuration)
        return

    def start_task(self, task):
        a = PyDAQmx.bool32()
        task.IsTaskDone(a)
        if a.value:
            task.StartTask()
        return

    def stop_task(self, task):
        if not None:
            task.StopTask()
        return

    def clear_task(self, task):
        if not None:
            task.ClearTask()
        return

    def prepare_analog_input(self):
        number_of_channels = len(self.parameters["input_channels"])
        if number_of_channels == 0:
            msg = "No analog channels defined in device parameters."
            raise LookupError(msg)

        task = PyDAQmx.Task()  # 'ai_task-'+f'{(time.time() % 1):.8f}'[2:]

        channels = ""
        for ch in self.parameters["input_channels"]:
            channels = channels + "/" + self.parameters["device_name"] + "/" + ch + ","

        task.CreateAIVoltageChan(
            channels,
            "",
            PyDAQmx_lookup_value(self.latent_parameters["terminal_type"]),
            -self.latent_parameters["voltage_limits"],
            self.latent_parameters["voltage_limits"],
            PyDAQmx_lookup_value(self.latent_parameters["units"]),
            None,
        )

        time_source = str(self.latent_parameters["input_clock_source"])

        if time_source.upper()[0:3].find("PFI") >= 0:
            time_source = ("/" + self.parameters["device_name"] + "/" + time_source.upper(),)

        total_samples = int(
            number_of_channels
            * self.parameters["input_samples_per_chan"]
            * self.parameters["inputs_per_sample"]
        )

        task.CfgSampClkTiming(
            time_source,
            self.parameters["input_sample_rate"],
            PyDAQmx_lookup_value(self.latent_parameters["input_active_edge"]),
            PyDAQmx_lookup_value(self.latent_parameters["input_sample_mode"]),
            total_samples,
        )

        self.prepared_input_task = task
        self.input_data = np.zeros(total_samples)
        self.parameters["input_samples_total"] = total_samples
        return

    def prepare_input_digital_trigger(self):
        trigger_edge = PyDAQmx_lookup_value(self.latent_parameters["input_active_edge"])
        chan_name = (
            "/"
            + self.parameters["device_name"]
            + "/"
            + self.latent_parameters["input_trigger_channel"]
        )
        self.prepared_input_task.CfgDigEdgeStartTrig(chan_name, trigger_edge)
        return

    def read_analog_input(self):
        samps_per_chan = int(
            self.parameters["input_samples_total"] / len(self.parameters["input_channels"])
        )

        self.prepared_input_task.ReadAnalogF64(
            samps_per_chan,
            PyDAQmx_lookup_value(self.latent_parameters["input_timeout"]),
            PyDAQmx_lookup_value(self.latent_parameters["input_fill_mode"]),
            self.input_data,
            int(self.parameters["input_samples_total"]),
            PyDAQmx.byref(PyDAQmx.int32()),
            None,
        )

        return

    def prepare_analog_output(self):
        number_of_channels = len(self.parameters["output_channels"])
        if number_of_channels == 0:
            msg = "No analog channels defined in device parameters."
            raise LookupError(msg)

        task = PyDAQmx.Task()  # 'ai_task-'+f'{(time.time() % 1):.8f}'[2:]

        channels = ""
        for ch in self.parameters["output_channels"]:
            channels = channels + "/" + self.parameters["device_name"] + "/" + ch + ","

        task.CreateAOVoltageChan(
            channels,
            "",
            PyDAQmx_lookup_value(self.latent_parameters["terminal_type"]),
            -self.latent_parameters["voltage_limits"],
            self.latent_parameters["voltage_limits"],
            PyDAQmx_lookup_value(self.latent_parameters["units"]),
            None,
        )

        time_source = str(self.latent_parameters["output_clock_source"])

        if time_source.upper()[0:3].find("PFI") >= 0:
            time_source = ("/" + self.parameters["device_name"] + "/" + time_source.upper(),)

        total_samples = int(
            number_of_channels
            * self.parameters["output_samples_per_chan"]
            * self.parameters["outputs_per_sample"]
        )

        task.CfgSampClkTiming(
            time_source,
            self.parameters["output_sample_rate"],
            PyDAQmx_lookup_value(self.latent_parameters["output_active_edge"]),
            PyDAQmx_lookup_value(self.latent_parameters["output_sample_mode"]),
            total_samples,
        )

        self.prepared_output_task = task
        self.output_data = np.zeros(total_samples)
        self.parameters["output_samples_total"] = total_samples
        self.ouput_data_size = total_samples
        return

    def prepare_output_digital_trigger(self):
        trigger_edge = PyDAQmx_lookup_value(self.latent_parameters["output_active_edge"])
        chan_name = (
            "/"
            + self.parameters["device_name"]
            + "/"
            + self.latent_parameters["output_trigger_channel"]
        )
        self.prepared_output_task.CfgDigEdgeStartTrig(chan_name, trigger_edge)
        return

    def write_analog_output(self):
        samps_per_chan = int(
            self.parameters["write_samples_total"] / len(self.parameters["write_channels"])
        )

        self.prepared_output_task.WriteAnalogF64(
            samps_per_chan,
            PyDAQmx_lookup_value(self.latent_parameters["output_timeout"]),
            PyDAQmx_lookup_value(self.latent_parameters["output_fill_mode"]),
            self.input_data,
            int(self.parameters["output_samples_total"]),
            PyDAQmx.byref(PyDAQmx.int32()),
            None,
        )

        return

    def show_preparation_options(self) -> None:
        """
        Prints available options for preparing DAQ tasks.
        """
        print(self.preparation_options())
        return

    def preparation_options(self) -> tuple[dict, dict, dict]:
        preparation_types = {
            "analog_input": self.prepare_analog_input,
            "input_digital_trigger": self.prepare_input_digital_trigger,
            "output_digital_trigger": self.prepare_output_digital_trigger,
        }
        input_methods = {"analog_input": self.read_analog_input}
        output_methods = {"analog_output": self.write_analog_output}
        return preparation_types, input_methods, output_methods

    def prepare_device(self, configuration: dict) -> None:
        preparation_types, input_methods, output_methods = self.preparation_options()

        try:
            self.preparations = configuration.get("preparations")
        except KeyError:
            print("prepations not listed in configuration")
        try:
            for prep in self.preparations.get("input"):
                preparation_types[prep]()
            input_method = self.preparations.get("input_method")
            self.prepared_input_method = input_methods.get(input_method)

            for prep in self.preparations.get("output"):
                preparation_types[prep]()
            output_method = self.preparations.get("output_method")
            self.prepared_output_method = output_methods.get(output_method)

        except TypeError:
            return  ## happends when preparations is empty
        except KeyError as e:
            print(
                f"{e} not found in input preparations or method listed, check preparations"
            )
        return


##############################################################

# PyDAQmx_lookup = {
#     "Differential": PyDAQmx.DAQmx_Val_Diff,
#     "RSE": PyDAQmx.DAQmx_Val_RSE,
#     "NRSE": PyDAQmx.DAQmx_Val_NRSE,
#     "by_channel": PyDAQmx.DAQmx_Val_GroupByChannel,
#     "by_scan": PyDAQmx.DAQmx_Val_GroupByScanNumber,
#     "finite_samples": PyDAQmx.DAQmx_Val_FiniteSamps,
#     "continuous_samples": PyDAQmx.DAQmx_Val_ContSamps,
#     "timed_single_poined": PyDAQmx.DAQmx_Val_HWTimedSinglePoint,
#     "infinite_timeout": PyDAQmx.DAQmx_Val_WaitInfinitely,
#     "rising_edge": PyDAQmx.DAQmx_Val_Rising,
#     "falling_edge": PyDAQmx.DAQmx_Val_Falling,
#     "volts": PyDAQmx.DAQmx_Val_Volts,
# }

parameter_options = {
    "terminal_type": ["Differential", "RSE", "NRSE"],
    "fill_mode": ["by_channel", "by_scan"],
    "sample_mode": ["finite_samples", "continuous_samples", "timed_single_point"],
    "active_edge": ["rising_edge", "falling_edge"],
    "units": ["volts"],
    "voltage_limits": [0.1, 0.2, 0.5, 1, 2, 5, 10],
}


## End NI_DAQ
