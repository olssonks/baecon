import sys
sys.path.insert(0,'C:\\Users\\walsworth1\\Documents\\Jupyter_Notebooks\\baecon')
import baecon as bc

from baecon import Device

from dataclasses import dataclass, field
import numpy as np

@dataclass
class Pulse:
    """Data structure for defining a pulse. 
    
       The data structure is simple and can be easily shared between different
       devices. 
    """    
    type      : str
    duration  : float
    start_time: float
    end_time  : float = field(init=False) ## for clarity we may want to make this a required argument, and overwrite it in the post_init method
    def __post_init__(self):
        self.end_time = self.duration + self.start_time

## due to saving thing in a config file (e.g. toml), configurations shouls be simple
## data structures used in parameters should be simple: list, tuple, and dictionary
## For a class to have a data structure as a parameter, need to have specific methods for unpacking
@dataclass
class Pulse_Sequence: ## Maybe different name to not be confused with PulseStreamer sequencies
    """Data structure for a pulse sequence for the Pulse Streamer.
       
       The format that the Pulse Streamer uses a formatter that is not the most
       intuitive for humans to think about. So instead, pulses are definced by 
       a start time and a duration within in the sequence. The sequence is then
       converted into the Pulse Streamer format.
       
       .. todo::
            Might want to make Pulse_sequence it's own class, seperate from the
            device so that it can be shared among the different devices more
            easily, e.g. Pulse Streamer, Keysight AWG, Zurich, etc.
            Specific pulse sequence child classes could then be defined for 
            each different device.
    """
    total_duration : float
    channels       : list = field(default_factory=list)
    pulse_patterns : list = field(default_factory=list)
    #types          : list = field(default_factory=list) don't need for now??
    
    def load_sequence(self, seq_file:str)->None:
        with open(seq_file, 'r') as file:
            seq_dict = bc.utils.load_config(file)
        self.channels, self.pulse_patterns = self.dict_to_base(seq_dict)
        ## need total duration calculate method
        return
        
    def save_sequence(self, seq_file:str)->None:
        seq_dict = self.base_to_dict()
        bc.utils.dump_config(seq_dict)
        return
    
    def base_to_dict(self)->dict:
        sequence_dict = {}
        for ch_idx, chan in enumerate(self.channels):
            pattern_dict = {}
            for p_idx, pulse in enumerate(self.pulse_patterns[ch_idx]):
                pulse_info = {'type': pulse.type, 
                              'duration': pulse.duration,
                              'start_time': pulse.start_time}
                pattern_dict.update({f'pulse_{p_idx}':pulse_info})
            sequence_dict.update({f'{chan}': pattern_dict})
        return sequence_dict
        
    def dict_to_base(self, sequence_dict:dict)\
                ->tuple(list[str], list[list[Pulse]]):
        
        channels = list(sequence_dict.keys())
        pulse_patterns = []
        for ch_idx, chan in enumerate(self.channels):
            pattern = []
            for p_idx, pulse in enumerate(list(sequence_dict[chan].values())):
                pattern.append(Pulse(pulse['type'], 
                                     pulse['duration'], 
                                     pulse['start_time']))
            pulse_patterns.append(pattern)
        return channels, pulse_patterns
    
    def sort_sequence(self):
        for ch_idx, chan in enumerate(self.channels):
            self.sort_channel(ch_idx)
        return
    
    def sort_channel(self, channel_index):
        start_times = [pulse.start_time for pulse in self.pulses[channel_index]]
        start_times_copy = start_times.copy()
        start_times.sort()
        sorted_indeces = [start_times_copy.index(time) for time in start_times]
        sorted_pulses = [self.pulses[channel_index][index] 
                         for index in sorted_indeces]
        self.pulses[channel_index] = sorted_pulses
        return