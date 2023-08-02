import pathlib

import baecon as bc
import pulsestreamer
import pytest
from baecon.Devices import Pulse, Pulse_Sequence, Pulse_Streamer

sequence_dir = pathlib.Path(__file__).parent.resolve()

ps_config = bc.utils.load_config(sequence_dir / "ex_config.toml")

seq_dict = bc.utils.load_config(sequence_dir / "test_seq.toml")

ps = Pulse_Streamer(ps_config)

sequence = Pulse_Sequence().from_dict(seq_dict)


def test_Pulse_Streamer_init():
    """Tests :py:func:`__init__` with includes :py:func:`connect_to_device`."""
    assert isinstance(ps.device, pulsestreamer.jrpc.pulse_streamer_jrpc.PulseStreamer)
    assert isinstance(ps.device_sequence, pulsestreamer.sequence.Sequence)
    return


def test_convert_channel():
    """Tests :py:func:`convert_channel` looking to see that the channel number
    is correction, and that the communication function is correct, either
    digital or analog.
    """
    chan1 = ps.convert_channel("PS-5")
    chan2 = ps.convert_channel("PS-A0")

    assert chan1.number == 5
    assert chan1.channel_communication.__name__ == "setDigital"

    assert chan2.number == 0
    assert chan2.channel_communication.__name__ == "setAnalog"
    return


def test_convert_pattern():
    """Tests :py:func:`convert_pattern` which converts a pulse pattern from
    :py:class:`Pulse_Sequence` into the correct format for the Pulse Streamer.
    """
    swab_pat, swab_types = ps.convert_pattern(
        sequence.pulse_patterns[1], sequence.get_types()[1]
    )

    assert swab_pat == [(1500.0, 0), (1000, 1), (8000.0, 0), (1000, 1), (0, 0)]
    assert swab_types == ["Zero", "pi/2", "Zero", "pi/2", "Zero"]
    return


def test_convert_to_swabian():
    """Tests :py:func:`convert_to_swabian` which converts a :py:class:`Pulse_Sequence`
    into the correct format for the Pulse Streamer, which include the channels
    pulse patterns, and pulse types.
    """
    swab_pat, swab_chan, swab_types = ps.convert_to_swabian(
        sequence, sequence.get_types()[1]
    )

    assert swab_pat == [
        [(1000, 0), (1000, 1), (0, 0)],
        [(1500.0, 0), (1000, 1), (8000.0, 0), (1000, 1), (0, 0)],
    ]
    assert swab_types == [["Zero", "none", "Zero"], ["Zero", "pi/2", "Zero", "pi/2", "Zero"]]

    assert swab_chan[0].number == 0
    assert swab_chan[0].communication_channel.__name__ == "setDigital"

    assert swab_chan[1].number == 3
    assert swab_chan[1].communication_channel.__name__ == "setDigital"

    return


def test_set_sequence():
    ps.set_sequence(seq_dict)

    assert ps.swabian_channels[0].number == 0
    assert ps.swabian_channels[0].channel_communication == "setDigital"

    assert ps.swabian_channels[1].number == 3
    assert ps.swabian_channels[1].channel_communication == "setDigital"

    assert ps.swabian_patterns == [
        [(1000, 0), (1000, 1), (0, 0)],
        [(1500.0, 0), (1000, 1), (8000.0, 0), (1000, 1), (0, 0)],
    ]

    assert ps.swabian_types == [
        ["Zero", "none", "Zero"],
        ["Zero", "pi/2", "Zero", "pi/2", "Zero"],
    ]

    return


def test_update_device():
    """Testing that swabian parameters get updated to `device_sequence`.

    :py:func:`getData` outputs the pusle sequence in the form:
         (duration, active digital channels, analog 1, analog 2)
         The digital channels are represented by an 8 bits in the form of an
         integeget indicating,whether the channel is on. In the third element,
         channels 0 and 3 are on, leading the bits to be 10010000. The
         integer representation of these bits is 9. Analog values a just
         the voltage level rounded to the nearest 16 bit value.
    """
    ps.set_sequence(seq_dict)
    ps.update_device()
    assert ps.device_sequence.getData() == [
        (1000, 0, 0, 0),
        (500, 1, 0, 0),
        (500, 9, 0, 0),
        (500, 8, 0, 0),
        (8000, 0, 0, 0),
        (1000, 8, 0, 0),
    ]
    return


def test_scan_shift_all_start_time():
    ps.set_sequence(seq_dict)
    ps.parameters["add_time"] = True
    ps.scan_shift_all(
        "start", [], ps.swabian_patterns, channel_idx=0, pulse_idx=1, shift_value=1500
    )
    ps.parameters["add_time"] = True
    ps.scan_shift_all(
        "start", [], ps.swabian_patterns, channel_idx=1, pulse_idx=1, shift_value=500
    )
    assert ps.swabian_patterns == [
        [(1000, 0), (2500, 1), (500, 0)],
        [(1500.0, 0), (1500, 1), (9500.0, 0), (1000, 1), (0, 0)],
    ]

    ps.set_sequence(seq_dict)
    ps.parameters["add_time"] = False
    ps.scan_shift_all(
        "start", [], ps.swabian_patterns, channel_idx=0, pulse_idx=1, shift_value=1500
    )
    ps.parameters["add_time"] = False
    ps.scan_shift_all(
        "start", [], ps.swabian_patterns, channel_idx=1, pulse_idx=1, shift_value=500
    )
    assert ps.swabian_patterns == [
        [(1000, 0), (1500, 1), (0, 0)],
        [(1500.0, 0), (500, 1), (7500.0, 0), (1000, 1), (0, 0)],
    ]
    return


def test_no_shift_duration():
    ps.set_sequence(seq_dict)
    ps.parameters["add_time"] = True
    ps.no_shift_duration(ps.swabian_patterns, channel_idx=0, pulse_idx=1, shift_value=1500)
    ps.no_shift_duration(ps.swabian_patterns, channel_idx=1, pulse_idx=1, shift_value=-500)
    assert ps.swabian_patterns == [
        [(1000, 0), (2500, 1), (0, 0)],
        [(1500.0, 0), (500, 1), (8500.0, 0), (1000, 1), (0, 0)],
    ]

    ps.set_sequence(seq_dict)
    ps.parameters["add_time"] = False
    ps.no_shift_duration(ps.swabian_patterns, channel_idx=0, pulse_idx=1, shift_value=1500)
    ps.no_shift_duration(ps.swabian_patterns, channel_idx=1, pulse_idx=1, shift_value=750)
    assert ps.swabian_patterns == [
        [(1000, 0), (1500, 1), (0, 0)],
        [(1500.0, 0), (750, 1), (8250.0, 0), (1000, 1), (0, 0)],
    ]
    return


def test_no_shift_start_time():
    ps.set_sequence(seq_dict)
    ps.parameters["add_time"] = False
    ps.no_shift_start_time(ps.swabian_patterns, channel_idx=0, pulse_idx=1, shift_value=1500)
    ps.no_shift_start_time(ps.swabian_patterns, channel_idx=1, pulse_idx=3, shift_value=7500)

    assert ps.swabian_patterns == [
        [(1500, 0), (1000, 1), (0, 0)],
        [(1500.0, 0), (1000, 1), (7500, 0), (1000, 1), (0, 0)],
    ]

    ps.set_sequence(seq_dict)
    ps.parameters["add_time"] = True
    ps.no_shift_start_time(ps.swabian_patterns, channel_idx=0, pulse_idx=1, shift_value=500)
    ps.no_shift_start_time(ps.swabian_patterns, channel_idx=1, pulse_idx=3, shift_value=75)

    assert ps.swabian_channels == [
        [(1500, 0), (1000, 1), (0, 0)],
        [(1500.0, 0), (1000, 1), (8075.0, 0), (1000, 1), (0, 0)],
    ]
    return


def test_write():
    return


def test_read():
    return


def test_enable_output():
    """Test :py:func:`enable_output` by streaming sequence (on) and streaming
    OutputState.Zero (off).
    """
    ps.enable_output()
    return


# ps.update_device()
# if __name__ == "__main__":
#     pytest.main()

ps.set_sequence(seq_dict)
ps.parameters["add_time"] = True
ps.scan_shift_all(
    "start", [], ps.swabian_patterns, channel_idx=0, pulse_idx=1, shift_value=1500
)
ps.swabian_patterns
