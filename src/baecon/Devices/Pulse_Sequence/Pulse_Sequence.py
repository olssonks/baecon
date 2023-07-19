from dataclasses import dataclass, field
from typing import TypeVar

import baecon as bc

Self = TypeVar("Self")


@dataclass
class Pulse:
    """Data structure for defining a pulse.

    The data structure is simple and can be easily shared between different
    devices.

    Time units are microseconds.
    .. todo::
         Might want to add another attr "time_units"?
    """

    type: str = "None"
    start_time: float = 1.0
    duration: float = 5.0
    end_time: float = field(
        init=False
    )  ## for clarity we may want to make this a required argument, and overwrite it in the post_init method

    def __post_init__(self):
        self.end_time = self.duration + self.start_time


## due to saving thing in a config file (e.g. toml), configurations shouls be simple.
## data structures used in parameters should be simple: list, tuple, and dictionary
## For a class to have a data structure as a parameter, need to have specific methods for unpacking
@dataclass
class Pulse_Sequence:
    """Data structure for generic pulse sequences.
    `Pulse` and `Pulse_Sequence` are meant to be "human readable", where
    a pulse is placed in a sequence based on the `start_time` and the
    `duration`.

    Pulse devices (PulseStreamer, AWG, etc.) have methods to convert this sequence
    into the proper format for the device to use.

    Attributes:
         channels (list[str]): The list of channels used in the sequence. The
             indices are paired with :attr:`pulse_patterns`, e.g., `channels[i] <-> pulse_pattern[i]`
         pulse_patterns (list[Pulse]): list of pulses for a specific channel.
             Each element is a :class:`Pulse`.
         total_duration (float): Total duration of the full sequence

    .. todo::
         Might want to make Pulse_sequence it's own class, seperate from the
         device so that it can be shared among the different devices more
         easily, e.g. Pulse Streamer, Keysight AWG, Zurich, etc.
         Specific pulse sequence child classes could then be defined for
         each different device.
    """

    channels: list = field(default_factory=list)
    pulse_patterns: list = field(
        default_factory=list
    )  ## make dict {channel: pulse_pattern} to preserve order?
    total_duration: float = field(init=False)

    def __post_init__(self) -> None:
        self.total_duration = self.calc_duration()
        return

    def update(self) -> None:
        self.sort_sequence()
        self.__post_init__()
        return

    def load_sequence(self, seq_file: str):
        """Loads `Sequence` from a file.
            Loaded pulse sequence is as `dict`, which is converted into a `Sequence`.

        Args:
            seq_file (str): Name of file to load.
        """
        seq_dict = bc.utils.load_config(seq_file)
        sequence = self.from_dict(seq_dict)
        return sequence

    def save_sequence(self, seq_file: str) -> None:
        """Saves `Sequence` to a file.
            The `Sequence` is first converted to a `dict` so it can be easily
            parsed into `toml`, `yaml`, or `json` format.

        Args:
            seq_file (str): File name to to save sequence.
        """
        seq_dict = self.to_dict()
        bc.utils.dump_config(seq_dict, seq_file)
        return

    def to_dict(self) -> dict:
        """Converts `Sequence` into dictionary format.

        Returns:
            dict: Dictionary version of `Sequence` object.
        """
        sequence_dict = {}
        for ch_idx, chan in enumerate(self.channels):
            pattern_dict = {}
            for p_idx, pulse in enumerate(self.pulse_patterns[ch_idx]):
                pulse_info = {
                    "type": pulse.type,
                    "duration": pulse.duration,
                    "start_time": pulse.start_time,
                }
                pattern_dict.update({f"pulse_{p_idx}": pulse_info})
            sequence_dict.update({f"{chan}": pattern_dict})
        return sequence_dict

    def from_dict(self: Self, sequence_dict: dict) -> Self:
        """Converts `dict` to `Sequence`.

        Returns:
            tuple (list[str], list[list[Pulse]]): Returns a `tuple` where the
            first element is a list of channels and the second element is a
            list of pulse_patterns.
        """
        try:
            channels = list(sequence_dict.keys())
            pulse_patterns = []
            for _ch_idx, chan in enumerate(channels):
                pattern = []
                for _p_idx, pulse in enumerate(list(sequence_dict[chan].values())):
                    ## imported object pulse is a dict not at Pulse
                    pattern.append(
                        Pulse(
                            type=pulse.get("type"),
                            start_time=pulse.get("start_time"),
                            duration=pulse.get("duration"),
                        )
                    )
                pulse_patterns.append(pattern)
            return Pulse_Sequence(channels, pulse_patterns)
        except AttributeError:
            print("Given sequence is empty")
            return Pulse_Sequence([], [])

    def sort_sequence(self):
        """Sorts the sequence for pulses to be in the proper time order."""
        for ch_idx, _chan in enumerate(self.channels):
            self.pulse_patterns[ch_idx] = self.sort_channel(ch_idx)
        return

    def sort_channel(self, channel_index: int) -> list[Pulse]:
        """Sorts the pulses for a single channel in :attr:pulse_pattern

        Args:
            channel_index (int): _description_
        """
        start_times = [pulse.start_time for pulse in self.pulse_patterns[channel_index]]
        start_times_copy = start_times.copy()
        start_times.sort()
        sorted_indeces = [start_times_copy.index(time) for time in start_times]
        sorted_pulses = [
            self.pulse_patterns[channel_index][index] for index in sorted_indeces
        ]
        return sorted_pulses

    def get_types(self) -> list[list[str]]:
        return [[pulse.type for pulse in pattern] for pattern in self.pulse_patterns]

    def calc_duration(self) -> float:
        ## sum function can flatten nested list
        flat_seq: list = sum(self.pulse_patterns, [])
        end_times = [pulse.end_time for pulse in flat_seq]
        if len(end_times) > 0:
            return max(end_times)
        else:
            return 0
