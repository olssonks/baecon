from typing import Optional

import numpy as np
import PyDAQmx

from baecon import Device


class NIDAQ_Base(Device):
    def __init__(self, configuration: Optional[dict] = None) -> None:
        self.parameters = {
            "device_name": "",
            "read_sample_rate": 50e3,
            "read_samples_per_chan": 10e3,
            "reads_per_sample": 1,
            "read_samples_total": 10e3,
            "read_channels": [],
        }
        self.latent_parameters = {
            "units": "volts",
            "voltage_limits": 2,
            "terminal_type": "RSE",
            "read_clock_source": "OnBoardClock",
            "read_active_edge": "rising_edge",
            "read_sample_mode": "finite_samples",
            "read_fill_mode": "by_channel",
            "read_timeout": "infinite_timeout",
            "read_trigger_channel": "",
        }

        super().__init__(configuration)

        self.preparations = ""
        self.prepared_read_task = None
        self.prepared_read_function = None
        self.read_data = []

        self.prepare_device(configuration)

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
    def write(self, parameter, value):
        pass
        return

    def read(self, parameter=None, value=None) -> np.ndarray:
        # self.start_task(self.prepared_read_task)
        self.prepared_read_function()
        return self.read_data

    def update_device(self):
        self.stop_task(self.prepared_read_task)
        self.clear_task(self.prepared_read_task)
        self.prepare_device(self.configuration)
        return

    def start_task(self, task):
        a = PyDAQmx.bool32()
        task.IsTaskDone(a)
        if a.value:
            task.StartTask()
        return

    def stop_task(self, task):
        task.StopTask()
        return

    def clear_task(self, task):
        task.ClearTask()
        return

    def prepare_analog_input(self):
        number_of_channels = len(self.parameters["read_channels"])
        if number_of_channels == 0:
            msg = "No analog channels defined in device parameters."
            raise LookupError(msg)

        task = PyDAQmx.Task()  # 'ai_task-'+f'{(time.time() % 1):.8f}'[2:]

        channels = ""
        for ch in self.parameters["read_channels"]:
            channels = channels + "/" + self.parameters["device_name"] + "/" + ch + ","

        task.CreateAIVoltageChan(
            channels,
            "",
            PyDAQmx_lookup[self.latent_parameters["terminal_type"]],
            -self.latent_parameters["voltage_limits"],
            self.latent_parameters["voltage_limits"],
            PyDAQmx_lookup[self.latent_parameters["units"]],
            None,
        )

        time_source = str(self.latent_parameters["read_clock_source"])

        if time_source.upper()[0:3].find("PFI") >= 0:
            time_source = ("/" + self.parameters["device_name"] + "/" + time_source.upper(),)

        total_samples = int(
            number_of_channels
            * self.parameters["read_samples_per_chan"]
            * self.parameters["reads_per_sample"]
        )

        task.CfgSampClkTiming(
            time_source,
            self.parameters["read_sample_rate"],
            PyDAQmx_lookup[self.latent_parameters["read_active_edge"]],
            PyDAQmx_lookup[self.latent_parameters["read_sample_mode"]],
            total_samples,
        )

        self.prepared_read_task = task
        self.read_data = np.zeros(total_samples)
        self.parameters["read_samples_total"] = total_samples
        self.acq_data_size = total_samples
        return

    def prepare_read_digital_trigger(self):
        trigger_edge = PyDAQmx_lookup[self.latent_parameters["read_active_edge"]]
        chan_name = (
            "/"
            + self.parameters["device_name"]
            + "/"
            + self.latent_parameters["read_trigger_channel"]
        )
        self.prepared_read_task.CfgDigEdgeStartTrig(chan_name, trigger_edge)
        return

    def read_analog_input(self):
        samps_per_chan = int(
            self.parameters["read_samples_total"] / len(self.parameters["read_channels"])
        )

        self.prepared_read_task.ReadAnalogF64(
            samps_per_chan,
            PyDAQmx_lookup[self.latent_parameters["read_timeout"]],
            PyDAQmx_lookup[self.latent_parameters["read_fill_mode"]],
            self.read_data,
            int(self.parameters["read_samples_total"]),
            PyDAQmx.byref(PyDAQmx.int32()),
            None,
        )

        return

    def prepare_device(self, configuration) -> None:
        preparation_methods = {
            "analog_input": self.prepare_analog_input,
            "digital_trigger": self.prepare_read_digital_trigger,
        }
        read_methods = {"analog_input": self.read_analog_input}
        try:
            self.preparations = configuration["preparations"]
        except KeyError:
            print("prepations not listed in configuration")
        try:
            for prep in self.preparations["read"]:
                preparation_methods[prep]()
            read_method = self.preparations["read_method"]
            self.prepared_read_function = read_methods[read_method]
        except TypeError as e:
            return  ## happends when preparations is empty
        except KeyError as e:
            print(f"{e} not found in read preparations or method listed, check preparations")
        return

    def show_parameter_optitions(self) -> None:
        print(parameter_options)
        return


##############################################################

PyDAQmx_lookup = {
    "Differential": PyDAQmx.DAQmx_Val_Diff,
    "RSE": PyDAQmx.DAQmx_Val_RSE,
    "NRSE": PyDAQmx.DAQmx_Val_NRSE,
    "by_channel": PyDAQmx.DAQmx_Val_GroupByChannel,
    "by_scan": PyDAQmx.DAQmx_Val_GroupByScanNumber,
    "finite_samples": PyDAQmx.DAQmx_Val_FiniteSamps,
    "continuous_samples": PyDAQmx.DAQmx_Val_ContSamps,
    "timed_single_poined": PyDAQmx.DAQmx_Val_HWTimedSinglePoint,
    "infinite_timeout": PyDAQmx.DAQmx_Val_WaitInfinitely,
    "rising_edge": PyDAQmx.DAQmx_Val_Rising,
    "falling_edge": PyDAQmx.DAQmx_Val_Falling,
    "volts": PyDAQmx.DAQmx_Val_Volts,
}

parameter_options = {
    "terminal_type": ["Differential", "RSE", "NRSE"],
    "fill_mode": ["by_channel", "by_scan"],
    "sample_mode": ["finite_samples", "continuous_samples", "timed_single_point"],
    "active_edge": ["rising_edge", "falling_edge"],
    "units": ["volts"],
    "voltage_limits": [0.1, 0.2, 0.5, 1, 2, 5, 10],
}


## End NI_DAQ
