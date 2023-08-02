from pathlib import Path

import pytest

#import baecon.Devices.Pulse_Sequence as pseq
from baecon.Devices.Pulse_Sequence import Pulse, Pulse_Sequence

## Test values
channels = ["PS-0", "PS-3"]
pulse_patterns = [[Pulse("none", 1, 1)], [Pulse("pi/2", 1.5, 1), Pulse("pi/2", 10.5, 1)]]
seq_dict = {
    "PS-0": {"pulse_0": {"type": "none", "duration": 1, "start_time": 1}},
    "PS-3": {
        "pulse_0": {"type": "pi/2", "duration": 1, "start_time": 1.5},
        "pulse_1": {"type": "pi/2", "duration": 1, "start_time": 10.5},
    },
}


def test_Pulse():
    t_pulse = Pulse("read", 10.5, 1)

    assert t_pulse.type == "read"
    assert t_pulse.start_time == 10.5
    assert t_pulse.duration == 1
    assert t_pulse.end_time == 11.5

    return


def test_Pulse_Sequence():
    t_seq = Pulse_Sequence(channels, pulse_patterns)

    assert t_seq.channels == channels
    assert t_seq.total_duration == 11.5
    assert t_seq.pulse_patterns == pulse_patterns

    return


def test_to_dict():
    t_seq = Pulse_Sequence(channels, pulse_patterns)
    test_dict = t_seq.to_dict()

    assert test_dict == seq_dict

    return


def test_from_dict():
    t_seq:Pulse_Sequence = Pulse_Sequence.from_dict(seq_dict)

    assert t_seq.channels == channels
    assert t_seq.pulse_patterns == pulse_patterns

    return


def test_save_load_sequence():
    test_file = Path(__file__).with_name("test_seq.toml")

    t_seq:Pulse_Sequence = Pulse_Sequence(channels, pulse_patterns)
    t_seq.save_sequence(test_file)
    load_seq:Pulse_Sequence = Pulse_Sequence.load_sequence(test_file)

    assert load_seq.channels == t_seq.channels
    assert load_seq.pulse_patterns == t_seq.pulse_patterns
    assert load_seq.total_duration == t_seq.total_duration

    return


def test_sort_sequence():
    unsorted_patterns = [[Pulse("none", 1, 1)], [Pulse("pi/2", 10.5, 1), Pulse("pi/2", 1.5, 1)]]

    t_seq = Pulse_Sequence(channels, unsorted_patterns)
    t_seq.sort_sequence()

    assert t_seq.pulse_patterns == pulse_patterns

    return


def test_get_types():
    t_seq = Pulse_Sequence(channels, pulse_patterns)

    test_types = t_seq.get_types()
    assert test_types == [["none"], ["pi/2", "pi/2"]]

    return


def test_calc_duration():
    t_seq = Pulse_Sequence(channels, pulse_patterns)

    dur = t_seq.calc_duration()
    assert dur == 11.5

    return


if __name__ == "__main__":
    pytest.main()
