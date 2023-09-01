import PyDAQmx


def PyDAQmx_lookup_value(value_key):
    return PyDAQmx_ref_value_dict[value_key]


PyDAQmx_ref_value_dict = {
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
