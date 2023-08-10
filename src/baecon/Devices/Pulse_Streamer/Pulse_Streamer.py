from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Tuple

import pulsestreamer
from nicegui import APIRouter

from baecon import Device
from baecon.Devices.Pulse_Sequence import Pulse, Pulse_Sequence
from baecon.Devices.Pulse_Sequence.Pulse_Sequence_GUI import Pulse_Sequence_GUI


@dataclass
class Swabian_Channel:
    """Simple class holding the channel numner and the pulsesteamer.Sequence
    method to communicate with the channel. Analog and digital channels use
    different communication methods, `setAnalog` and `setDigital`,
    respectively.
    """

    number: int
    channel_communication: Callable[[int, List[Tuple[int, int]]], None]

    def set_pattern(self, pattern: List[Tuple[int, int]]) -> None:
        self.channel_communication(self.number, pattern)


## under score in the name to differentiate between pulsestreamer.PulseStreamer
class Pulse_Streamer(Device):
    """Class for the Swabian Instruments PulseStreamer device.
    This class handles communication to a PulseStreamer device using the
    `pulsestreamer` package.
    A :py:class:`Pulse_Sequence` should be provided as a `dict` and :py:meth:`convert_to_swabian`
    will convert it into the PulseStreamer format with :py:attr:`swabian_types`,
    :py:attr:`swabian_channels`, and :py:attr:`swabian_patterns`.

    .. todo::
         Currently sequences are shift/updated all in pure Python. If this is
         too slow, we can use Numpy array and generate the all the sequences
         before the measurement, then just index them during the measurement.
    """

    def __init__(self, configuration: Dict[str, Any]) -> None:
        """Set parameters for this `Device` class and connect to physical
        instrument

        Args:
            configuration (dict, optional): Dictionary of device parameters.
                Defaults defined here will be used if no `configuration` is
                provided.
        """
        self.parameters: dict = {
            "pulse_sequence": {},
            "type_to_scan": "pi/2",
            "scan_catagory": "start",
            "scan_shift": "no_shift",
            "add_time": True,
            "loop_number": -1,  ## infinite
        }
        self.latent_parameters: dict = {"IPaddress": "10.229.42.144"}

        (
            self.device,
            self.device_sequence,
        ) = self.connect_to_device(configuration)

        super().__init__(configuration)

        try:
            seq_dict = configuration.get("parameters").get("pulse_sequence")
        except AttributeError:
            seq_dict = {}

        if not len(seq_dict) == 0:
            ## if sequence defined in config use it
            self.set_sequence(seq_dict)
        else:
            self.swabian_types: List[List[str]] = []
            self.swabian_channels: List[Swabian_Channel] = []
            self.swabian_patterns: List[List[Tuple[int, int]]] = []
        return

    def set_sequence(self, seq_dict: Dict) -> None:
        """Sets the `Pulse_Streamer` attributes based on the given dictionary.

        Args:
            seq_dict (Dict): Dictionary of sequence
        """
        seq = Pulse_Sequence().from_dict(seq_dict)
        types = seq.get_types()

        (
            self.swabian_patterns,
            self.swabian_channels,
            self.swabian_types,
        ) = self.convert_to_swabian(seq, types)

        return

    def connect_to_device(
        self, configuration: dict
    ) -> Tuple[pulsestreamer.PulseStreamer, pulsestreamer.Sequence]:
        """Connect to Pulse Streamer device and create Pulse Streamer `sequence`
           object. This `sequence` object is ultimately what gets sent to the
           Pulse Streamer Device.

        Args:
            configuration (dict): Dictionary of configurations for the device.

        Returns:
            ps_device (PulseStreamer): Object to use to communication with physical device.
            sequence  (PulseStreamer.Sequence): Pulse sequence object to run on
                the Pulse Streamer device.
        """
        connection_settings = configuration.get("latent_parameters")
        if connection_settings is None:
            connection_settings = []
        if "IPaddress" in connection_settings:
            self.latent_parameters.update({"IPaddress": connection_settings["IPaddress"]})
            ps_device = pulsestreamer.PulseStreamer(self.latent_parameters["IPaddress"])
            sequence = ps_device.createSequence()
        else:
            print(
                f'No IPaddress specificed in "latent_parameters" using Class default value:{self.latent_parameters["IPaddress"]}.'
            )
            ps_device = pulsestreamer.PulseStreamer(self.latent_parameters["IPaddress"])
            sequence = ps_device.createSequence()

        return ps_device, sequence

    def write(self, parameter: str, value: float) -> None:
        """Communication to the PulseStreamer device. The main
           commands are pretty simple: for sending the pulse sequence object the
           device and telling the device how many times to run the sequence.

           The input `parameter` will be either `start_time` or `duration`, and
           then the `value` is the time unit to change by.

        Args:
            parameter (str): Either `start_time` or `duration` to inform how
                the sequence should be updated.
            value (float): Time values that the parameter will change by. Defined
                as a `float` in microseconds. Pulse Streamer uses nanoseconds,
                so this value is converted into a `int` in nanoseconds in the other
                methods.
        """
        value_nanoseconds = int(value * 1000)
        self.swabian_patterns = self.update_pulses(parameter, value_nanoseconds)
        self.update_device()
        self.device.stream(self.device_sequence, int(self.parameters["loop_number"]))

        return

    def read(self, parameter, value):
        """Add functionally to read the value of `parameter` from the instrument.

        Args:
            parameter (_type_): _description_
            value (_type_): _description_
        """
        return

    def enable_output(self, value: bool):
        """Enables or disables `Pulse_Streamer` output based on the provided
           boolean `value`. "Disabled" output for the pusle streamer is setting
           the channels to zero.

        Args:
            value (bool): Boolean to enable or disable output.
        """
        if value:
            self.update_device()
            if self.device_sequence.isEmpty():
                print("Device sequence is empty.")
            else:
                self.device.stream(
                    self.device_sequence, n_runs=self.parameters.get("loop_number")
                )
        else:
            self.device.constant(pulsestreamer.OutputState.ZERO())

        return

    def close_instrument(self) -> None:
        return

    def update_device(self) -> None:
        """Sends pulse sequence to the Pulse Streamer device.

        We need to individually update each channel on the Pulse Streamer.
        This methods loops through the channels defined in `Pulse_Streamer.swabian_channels`
        which Lists the Pulse Streamer output channels for the sequence. A full
        pulse pattern (single channel pulse sequence) is sent to a Pulse Streamer
        channel.

        Args:
            new_pulses (_type_): New pulse sequence to send to the device. These
                have been updated based on the `parameter` and `value` entries.

        .. todo::
                Currently updates all channels. May want to add some attribute
                that Lists the dynamic channels (i.e. channels that change during
                the measurement). `set.Digital` on 4 channels takes ~137us
        """
        for ch_idx, channel in enumerate(self.swabian_channels):
            ## check if channel is analog or digital
            ## ps_outputs in form 'PS-0',...,'PS-7', 'PS-A0', 'PS-A1'
            channel.set_pattern(self.swabian_patterns[ch_idx])
        return

    def update_pulses(self, scan_category: str, shift_value: int) -> List[List[Pulse]]:
        """Generates new pulse sequence to send to the Pulse Streamer device.

           This sequence is in the Pulse Streamer format, i.e., the `swabian_patterns`
           sequence is updated and returned.

        Args:
            scan_category (_type_):  Type of pulse to shift.
            shift_value (_type_): Amount to shift by.
        """
        for channel_idx, _chan in enumerate(self.swabian_channels):
            for type_idx, name in enumerate(self.swabian_types[channel_idx]):
                self.scan_by_type(scan_category, shift_value, channel_idx, type_idx, name)
        return

    def scan_by_type(
        self,
        scan_category: str,
        shift_value: int,
        channel_idx: int,
        type_idx: int,
        pulse_name: str,
    ) -> None:
        """Shifts pulses in a pattern based on the pulses' type.

        Args:
            scan_category (str): Type of pulse to shift.
            shift_value (int): Amount to shift by.
            channel_idx (int): Channel of the pattern
            type_idx (int): Index of the pulse to shift, i.e., pulse index in pattern
            pulse_name (str): Name of the type of pulses to shift.
        """
        if pulse_name == self.parameters["type_to_scan"]:
            self.shift_pulses(
                scan_category,
                self.swabian_types,
                self.swabian_patterns,
                channel_idx,
                type_idx,
                shift_value,
            )
        return

    def shift_pulses(
        self,
        scan_category: str,
        types: List[List[str]],
        pulse_patterns: List[List[Tuple[int, int]]],
        channel_idx: int,
        type_idx: int,
        shift_value: int,
    ) -> None:
        """Updates `pulses_swabian`, the Pulse Streamer format of the pulse
           sequence based on type of shift.

        Args:
            scan_category (str): _description_
            types (List): _description_
            pulses (List): _description_
            channel_idx (int): _description_
            type_idx (int): _description_
            shift_value (float): _description_

        Returns:
            _type_: _description_
        """
        if self.check_negative(shift_value):
            ## do nothing: shift value cannot be negative with `add_time`=False
            return
        if self.parameters["scan_shift"] == "no_shift":
            self.scan_no_shift(
                scan_category, types, pulse_patterns, channel_idx, type_idx, shift_value
            )
        elif self.parameters["scan_shift"] == "shift_channel":
            self.scan_shift_channel(
                scan_category, types, pulse_patterns, channel_idx, type_idx, shift_value
            )
        elif self.parameters["scan_shift"] == "shift_all":
            self.scan_shift_all(
                scan_category, types, pulse_patterns, channel_idx, type_idx, shift_value
            )
        else:
            print(f"Unrecognized shift type: {self.parameters['scan_shift']}")

        return

    def check_negative(self, shift_value: int) -> bool:
        """Checks if the `shift_value` is negative and the `add_time` is False.
           This two setting are not compatibale, i.e., the pulse duration cannot
           be set to a negative number

        Args:
            shift_value (int): _description_

        Returns:
            bool: _description_
        """
        check_val = self.parameters["add_time"] is False and shift_value < 0
        if check_val:
            print("Negative values only work with 'add_time' = True.")
        return check_val

    def scan_shift_all(
        self,
        scan_category: str,
        types: List[List[str]],
        pulse_patterns: List[List[Tuple[int, int]]],
        channel_idx: int,
        pulse_idx: int,
        shift_value: int,
    ):
        """Alters the pulse patterns such that all pulses that occur after the
           pulse of interest (at channel_idx and pulse_idx) are shifted.

           Either the start time or duration of pulses can be alterted. Additionally,
           the shift value can be added to the current pulse start/duration or
           the shift value sets the start/duration (:py:attr:`Pulse_streamer.parameters`['add_time'])

        Args:
            scan_category (str): Denotes whether start time or duration should be changed.
            types (List[List[str]]): List of the types for all pulses in all pulse patterns.
            pulse_patterns (List[List[Tuple[int, int]]]): Pulse patterns of the sequence
            channel_idx (int): Channel where pulse of interest is.
            pulse_idx (int): Index of pulse in the pattern.
            shift_value (int): Amount to alter the pulse by.
        """
        absolute_start = sum(
            [pulse[0] for pulse in pulse_patterns[channel_idx][: pulse_idx + 1]]
        )
        if scan_category == "duration":
            self.shift_all_duration(pulse_patterns, channel_idx, pulse_idx, shift_value)
        elif scan_category == "start":
            shift_for_other_pulses = self.shift_all_start_time(
                pulse_patterns, channel_idx, pulse_idx, shift_value
            )
        else:
            print(f'{scan_category} not recognized, us "start" or "duration"')

        for other_chan, pattern in enumerate(pulse_patterns):
            ## looking at the other channels to shift, then break since only
            ## one shift per channel is needed due to the Swabian format.
            if not other_chan == channel_idx:
                chan_start = 0
                for other_idx, other_pulse in enumerate(pattern):
                    if chan_start > absolute_start:
                        pulse_patterns[other_chan][other_idx] = (
                            other_pulse[0] + shift_for_other_pulses,
                            other_pulse[1],
                        )
                        break
                    else:
                        chan_start += other_pulse[0]
        return

    def shift_all_duration(
        self,
        pulse_patterns: List[List[Tuple[int, int]]],
        channel_idx: int,
        pulse_idx: int,
        shift_value: int,
    ) -> None:
        """Changes the duration of the pulse of interest.

        Args:
            pulse_patterns (List[List[Tuple[int, int]]]): Pulse patterns of the sequence
            channel_idx (int): Channel where pulse of interest is.
            pulse_idx (int): Index of pulse in the pattern.
            shift_value (int): Amount to alter the pulse by.
        """
        pulse = pulse_patterns[channel_idx][pulse_idx]
        if self.parameters["add_time"]:
            pulse_patterns[channel_idx][pulse_idx] = (pulse[0] + shift_value, pulse[1])
        else:
            pulse[0]
            pulse_patterns[channel_idx][pulse_idx - 1] = (pulse[0] + shift_value, pulse[1])

        ## if sweept pulse is the first in the sequence,
        ## shift the index 1 to use it to check other pulse start
        if pulse_patterns[channel_idx][pulse_idx - 1 : pulse_idx] == []:
            pulse_idx += 1

        return

    def shift_all_start_time(
        self,
        pulse_patterns: List[List[Tuple[int, int]]],
        channel_idx: int,
        pulse_idx: int,
        shift_value: int,
    ) -> int:
        """Shifts the start time of the pulse and returns a value by which the pulses
           after this one, on other channels, should be shifted by.

        Args:
            pulse_patterns (List[List[Tuple[int, int]]]): Pulse patterns of the sequence
            channel_idx (int): Channel where pulse of interest is.
            pulse_idx (int): Index of pulse in the pattern.
            shift_value (int): Amount to alter the pulse by.

        Returns:
            int: Value to by which to shift other pulses.
        """
        pulse = pulse_patterns[channel_idx][pulse_idx]
        if self.parameters["add_time"]:
            pulse_patterns[channel_idx][pulse_idx] = (pulse[0] + shift_value, pulse[1])
            shift_for_other_pulses = shift_value
        else:
            original_start = pulse[0]
            pulse_patterns[channel_idx][pulse_idx] = (shift_value, pulse[1])
            shift_for_other_pulses = original_start - shift_value
        return shift_for_other_pulses

    def scan_shift_channel(
        self,
        scan_category: str,
        types: List[List[Pulse]],
        pulse_patterns: List[List[Tuple[int, int]]],
        channel_idx: int,
        type_idx: int,
        shift_value: int,
    ) -> None:
        """Changes the pulse and shifts pulses after it only in the same channel.
           Due to the format of the Swabian sequences, this operation is very simple.

        Args:
            scan_category (str): Denotes whether start time or duration should be changed.
            types (List[List[str]]): List of the types for all pulses in all pulse patterns.
            pulse_patterns (List[List[Tuple[int, int]]]): Pulse patterns of the sequence
            channel_idx (int): Channel where pulse of interest is.
            pulse_idx (int): Index of pulse in the pattern.
            shift_value (int): Amount to alter the pulse by.
        """
        pulse = pulse_patterns[channel_idx][type_idx]
        if self.parameters["add_time"]:
            pulse_patterns[channel_idx][type_idx] = (pulse[0] + shift_value, pulse[1])
        else:
            pulse_patterns[channel_idx][type_idx] = (shift_value, pulse[1])
        return

    def scan_no_shift(
        self,
        scan_category: str,
        types: List[List[str]],
        pulse_patterns: List[List[Tuple[int, int]]],
        channel_idx: int,
        pulse_idx: int,
        shift_value: int,
    ) -> None:
        """Change the start time or duration of a pulse and keep all pulses after
           at their original posistions in the sequence.

        Args:
            scan_category (str): Denotes whether start time or duration should be changed.
            types (List[List[str]]): List of the types for all pulses in all pulse patterns.
            pulse_patterns (List[List[Tuple[int, int]]]): Pulse patterns of the sequence
            channel_idx (int): Channel where pulse of interest is.
            pulse_idx (int): Index of pulse in the pattern.
            shift_value (int): Amount to alter the pulse by.
        """
        if scan_category == "duration":
            self.no_shift_duration(pulse_patterns, channel_idx, pulse_idx, shift_value)
        elif scan_category == "start":
            self.no_shift_start_time(pulse_patterns, channel_idx, pulse_idx, shift_value)
        else:
            print(f'{scan_category} not recognized, us "start" or "duration"')
        return

    def no_shift_duration(
        self,
        pulse_patterns: List[List[Tuple[int, int]]],
        channel_idx: int,
        pulse_idx: int,
        shift_value: int,
    ) -> None:
        """Shifts duration of the pulse of interest and preserves the other pulses
           in their original places.

           There is the possibility that a pulse duration will collide with
           the next pulse in the pattern. This is handled by limiting the
           duration of the pulse of interest to end 5 ns before the next pulse.
           Any durations longer will be limited to thi same duration.

        Args:
            pulse_patterns (List[List[Tuple[int, int]]]): Pulse patterns of the sequence
            channel_idx (int): Channel where pulse of interest is.
            pulse_idx (int): Index of pulse in the pattern.
            shift_value (int): Amount to alter the pulse by.
        """
        pulse = pulse_patterns[channel_idx][pulse_idx]
        next_pulse = pulse_patterns[channel_idx][pulse_idx + 1]

        if self.parameters["add_time"]:
            pulse_patterns[channel_idx][pulse_idx] = (pulse[0] + shift_value, pulse[1])
        else:
            pulse_patterns[channel_idx][pulse_idx] = (shift_value, pulse[1])

        if not next_pulse == (0, 0):
            if (shift_value - 5) >= next_pulse[0]:
                print(
                    f"Pulse: [{self.swabian_types[channel_idx][pulse_idx]}, {pulse}]\
                        colliding with next pulse in the channel. Capping duration to\
                        5 ns before the next pulse."
                )
                shift_value -= 5
            pulse_patterns[channel_idx][pulse_idx + 1] = (
                next_pulse[0] + pulse[0] - shift_value,
                next_pulse[1],
            )

        return

    def no_shift_start_time(
        self,
        pulse_patterns: List[List[Tuple[int, int]]],
        channel_idx: int,
        pulse_idx: int,
        shift_value: int,
    ) -> None:
        """Shifts the start time of the pulse of interest and preserves the other pulses
           in their original places.

           This cannot be accomplished if the pulse of interest is the first in
           the pattern. When this is the case, this method does nothing.

        Args:
            pulse_patterns (List[List[Tuple[int, int]]]): Pulse patterns of the sequence
            channel_idx (int): Channel where pulse of interest is.
            pulse_idx (int): Index of pulse in the pattern.
            shift_value (int): Amount to alter the pulse by.
        """
        message = f"Pulse {pulse_patterns[channel_idx][pulse_idx]} in channel \
                    {channel_idx} cannot shift start time without a pulse before it."

        ## additional zero index here need for [(time, on)] -> (time, on)
        if pulse_patterns[channel_idx][pulse_idx - 1 : pulse_idx][0] in [[], (), (0, 0)]:
            print(message)
            ## if no prior pulse, do nothing
        else:
            pre_pulse = pulse_patterns[channel_idx][pulse_idx - 1]
            original_start = pre_pulse[0]
            if self.parameters["add_time"]:
                pulse_patterns[channel_idx][pulse_idx - 1] = (
                    original_start + shift_value,
                    pre_pulse[1],
                )
            else:
                pulse_patterns[channel_idx][pulse_idx - 1] = (shift_value, pre_pulse[1])
        return

    def convert_to_swabian(
        self, sequence: Pulse_Sequence, types: List[List[str]]
    ) -> Tuple[List[Any], List[Any], List[Any]]:
        """Take sequence in "human readable" sequence format and turns it into
           the proper format for the PulseStreamer device.

           "Human readable" means a pulses in a pulse sequence is defined by
           their absolute start time and their duration. The PulseStreamer takes
           pulses in the format of relative start time, i.e., how long after the
           end of the last pulst, and duration as well.

        Args:
            sequence (Pulse_Sequence): _description_
            types (List[List[any]]): _description_

        Returns:
            Tuple[List]: Tuple consisting of (pulse patterns, channels, types)
        """
        new_patterns = []
        new_types = []
        new_channels = []
        for ch_idx, chan in enumerate(sequence.channels):
            new_pattern: List[Any] = []
            types_holder: List[Any] = []

            new_chan = self.convert_channel(chan)
            (
                new_pattern,
                types_holder,
            ) = self.convert_pattern(sequence.pulse_patterns[ch_idx], types[ch_idx])

            new_patterns.append(new_pattern)
            new_channels.append(new_chan)
            new_types.append(types_holder)
        return (
            new_patterns,
            new_channels,
            new_types,
        )

    def convert_pattern(
        self, pulse_pattern: List[Pulse], type: List[str]
    ) -> Tuple[List[Tuple], List[str]]:
        """Converts a pulse_pattern from `Pulse_Sequence` form to the
           Swabian form. Converts the types of the pulses as well. Adds
           `Zero` type to portion of the pattern where the value is zero.

        Returns:
            Tuple[List[Tuple], List[str]]: Returns a Tuple of pulse_pattern and
                types in Swabian format.
        """
        new_pattern: List[tuple[float, int]] = []
        names_holder: List[str] = []
        duration_counter = 0
        for p_idx, pulse in enumerate(pulse_pattern):
            start = pulse.start_time * 1000 - duration_counter
            p1 = (start, 0)
            p2 = (pulse.duration * 1000, 1)
            duration_counter = start + pulse.duration * 1000
            ## use extend instead of append to put p1, p2 in pattern not [p1,p2]
            new_pattern.extend([p1, p2])
            ## 'Zero" is the type when the pulse is off / low
            names_holder.extend(("Zero", type[p_idx]))
        if not new_pattern[-1][1] == 0:
            ## capping all patterns with (0,0) will pad anything that is
            ## shorter than the longest pulse pattern with zeros in that
            ## channel until the end of the sequence
            new_pattern.append((0, 0))
            names_holder.append("Zero")
        return (
            new_pattern,
            names_holder,
        )

    def convert_channel(self, channel: str) -> Swabian_Channel:
        """Generates a :class:`Swabian_Channel` from a given string.
           Sets the proper communication funcation (`setDigital` or `setAnalog`)
           best on the given string.

        Args:
            channel (str): String specifying the channel to generate. Possible
            values: "PS-0", "PS-1", "PS-2", "PS-3", "PS-4", "PS-5", "PS-6",
            "PS-7", "PS-A0", "PS-A1".

        Returns:
            Swabian_Channel: Object hold the communication method for the
                channel and the channel number.
        """
        if "A" in channel:
            swabian_channel = Swabian_Channel(
                int(channel[-1]), self.device_sequence.setAnalog
            )
        else:
            swabian_channel = Swabian_Channel(
                int(channel[-1]), self.device_sequence.setDigital
            )
        return swabian_channel

    def get_device_gui(self) -> tuple[APIRouter, str]:
        """Calls the `Pulse_Streamer` device GUI which is `Pulse_Sequence_GUI`.

        Returns:
            tuple[APIRouter, str]: `nicegui` APIRouter object specifying the
                route to the GUI page, and name of GUI page
        """
        self.gui_router = Pulse_Sequence_GUI.device_gui_router
        return self.gui_router, Pulse_Sequence_GUI.device_gui_name

    def update_sequence_from_gui(self, sequence: Pulse_Sequence) -> None:
        """Updates sequence to the one in the currently shown in the GUI.

        Args:
            sequence (Pulse_Sequence): Sequence in the GUI.
        """
        types = sequence.get_types()
        (
            self.swabian_patterns,
            self.swabian_channels,
            self.swabian_types,
        ) = self.convert_to_swabian(sequence, types)
        return

    def generate_full_scan(self, scan_type, minimum, maximum):
        return


# if __name__ == "__main__":
#     ps_config = bc.utils.load_config(
#         'C:/Users/walsworth1/Documents/Jupyter_Notebooks/baecon/Instruments/Pulse_Streamer/ex_config.toml'
#     )
#     seq_config = bc.utils.load_config(
#         'C:/Users/walsworth1/Documents/Jupyter_Notebooks/baecon/Instruments/Pulse_Sequence/test_seq.toml'
#     )

#     ps = Pulse_Streamer(ps_config)

#     ps.set_sequence(seq_config)

#     ps.device_sequence.plot()
