from baecon import Device

from dataclasses import dataclass, field
import numpy as np

from pulsestreamer import PulseStreamer

@dataclass
class Pulse_Sequence: ## Maybe different name to not be confused with PulseStreamer sequencies
    """To make the scan of the sequence, we'll have a copy or holder of the original sequence
       so that when scanning we are adding/setting time with respect to the orignal sequence
       if start = 4us and scan is add 1,2,3, we want 5, 6, 7 to be out come
       not (4+1), (4+1+2), (4+1+2+3)
    """
    ps_output: list = field(default_factory=list)
    pulses: list = field(default_factory=list)
    pulses_swabian: list = field(default_factory=list)
    types: list = field(default_factory=list)
    types_swabian: list = field(default_factory=list)
    

class PulseStreamer(Device):
    def __init__(self, configuration: dict = None) -> None:
        """Add initionalization specifcs for the type of insturment.

        Args:
            configuration (dict, optional): _description_. Defaults to None.
        """
        self.parameters = {'sequence': {}, ##sequence dataclass???
                           'name_to_scan': 'pi/2',
                           'scan_catagory': 'start',
                           'scan_shift': 'no_shift',
                           'add_time': True
                           }
        
        self.latent_parameters = {'IPaddress': '127.0.0.1'} 
        
        self.device = self.connect_to_device()
        
        super.__init__(configuration)
        
        return

    def connect_to_device(self):
        ps = PulseStreamer(self.latent_parameters['IPaddress'])
        return ps

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

    def close_instrument(self) -> None:
        
        return
# end Instrument class


        
        write('start', val)
        scan_name
        for chan_idx, chan in enumerate(names):
            for name_idx, name in enumerate(chan):
                if name == scan_name:
                    pulse = pulses[channel_idx][name_idx]
                    start = pulse[0]
                    pulses[channel_idx][name_idx] = (pulse[0]+val, pulse[1])
                    for chan_pulse in ps.pulses[channel_index]:
                        if chan_pulse[0]>start:
                            chan_pulse[0] = chan_pulse[0]+val
    
    From Gui we get 
    Pulse_Sequence
    pulses
    types
    ps_outputs
    pulses_swabian
    types_swabian
    
    write start
        find pulses by name
        add to and update sequence
        
    
    def update_pulses(self, scan_category, shift_value):
        for channel_idx, chan in enumerate(self.parameters['sequence']\
                                           ['ps_output']):
            for name_idx, name in enumerate(self.parameters['sequence']\
                                            ['types_swabian'][channel_idx]):
                if name == self.parameters['name_to_scan']:
                    self.shift_pulses(
                        scan_category, 
                        self.parameters['sequence']['types_swabian'], 
                        self.parameters['sequence']['pulses_swabian'], 
                        channel_idx, name_idx, shift_value
                        )
                    
        return
        
    def shift_pulses(self, scan_category, types, pulses, 
                     channel_idx, name_idx, shift_value):
        if self.parameters['scan_shift'] == 'no_shift':
           new_pulses = self.scan_no_shift(scan_category, types, pulses, 
                        channel_idx, name_idx, shift_value)
        elif self.parameters['scan_shift'] == 'shift_channel':
            new_pulses = self.scan_shift_channel(scan_category, types, pulses, 
                        channel_idx, name_idx, shift_value)
        elif self.parameters['scan_shift'] == 'shift_all':
           new_pulses =  self.scan_shift_all(scan_category, names, pulses, 
                        channel_idx, name_idx, shift_value)
        else:
            print(f"Unrecognized shift type: {self.parameters['scan_shift']}")
        return new_pulses
        
    def scan_shift_all(self, scan_category:str, types, pulses:list, 
                   channel_idx:int, name_idx:int, shift_value:int):
        if scan_category=='duration':
            if self.parameters['add_time']:
                pulses[channel_idx][name_idx][0] += shift_value
            else:
                original_dur = pulses[channel_idx][name_idx-1][0]
                pulses[channel_idx][name_idx-1][0] = shift_value
            ## if sweept pulse is the first in the sequence, 
            ## shift the index 1 to use it to check other pulse start
            if pulses[channel_idx][name_idx-1:name_idx] == []:
                name_idx += 1
        elif scan_category == 'start':
            if self.parameters['add_time']:
                pulses[channel_idx][name_idx][0] += shift_value
                shift_for_other_pulses = shift_value
            else:
                original_start = pulses[channel_idx][name_idx][0]
                pulses[channel_idx][name_idx][0] = shift_value
                shift_for_other_pulses = original_start - shift_value
        else:
            print(f'{scan_category} not recognized, us "start" or "duration"')
        ## looking at the other channels to shift the pulse that occurs 
        ## before the scanned pulse, then break since only one shift per 
        ## channel is need
        for other_chan in types: 
            if not other_chan==channel_idx:
                for other_pulse in other_chan:
                    if other_pulse[0] > pulses[channel_idx][name_idx]:
                        other_pulse[0] += shift_for_other_pulses
                        break
        return pulses
    
    def scan_shift_channel(self, scan_category, names, pulses, 
                        channel_idx, name_idx, shift_value):
        if self.parameters['add_time']:
            pulses[channel_idx][name_idx][0] += shift_value
        else:
            pulses[channel_idx][name_idx][0] = shift_value
        return
        
    def scan_no_shift(scan_category, names, pulses, 
                    channel_idx, name_idx, shift_value):
        if scan_category == 'duration':
            if self.parameters['add_time']:
                pulses[channel_idx][name_idx][0] += shift_value
            else:
                original_dur = pulses[channel_idx][name_idx][0]
                pulses[channel_idx][name_idx][0] = shift_value
            if not pulses[channel_idx][name_idx:name_idx+1] in [[], [0,0]]:
                pulses[channel_idx][name_idx+1] += original_dur - shift_value
        
        elif scan_category == 'start':
            if self.parameters['add_time']:
                if pulses[channel_idx][name_idx-1:name_idx] in [[],[0,0]]:
                    print(f'Pulse {pulses[channel_idx][name_idx]} in channel {channel_idx} cannot shift start time without a pulse before it.')
                    ## if not prior pulse, do nothing
                else:
                    original_start = pulses[channel_idx][name_idx-1][0]
                    pulses[channel_idx][name_idx-1][0] = shift_value
            if not pulses[channel_idx][name_idx:name_idx+1] in [[], [0,0]]:
                pulses[channel_idx][name_idx+1] =+ original_start - shift_value
        else:
            print(f'{scan_category} not recognized, us "start" or "duration"')
            
        return
    
    # def scan_sequence(sefl, ps:Pulse_Sequence, 
    #                   catagory:str, amount:float):
    #     if catagory=='start':
            
    #     elif catagory == 'duration':
            
    #     else:
    #         print(f'Unrecognized scan catagory: {catagory}. Use "start" or "duration"')
    #     return
    

    # Not needed ??
    # def update_sequence(self, ps:Pulse_Sequence, channel, pulse, name):
    #     start, duration = pulse
    #     self.add_pulse(ps, channel, start, duration, name)
    #     for chan_seq in ps.pulses:
    #         for chan_pulse in chan_seq:
    #             if chan_pulse[0]>start:
    #                 pass             
    #     return

def convert_to_swab(sequence):
    new_sequence = []
    for pattern in sequence:
        new_pattern = []
        duration_counter = 0
        for pulse in pattern:
            start, length = pulse
            start = start-duration_counter
            p1 = (start, 0)
            p2 = (length, 1)
            duration_counter = start+length
            new_pattern.extend([p1, p2])
        if not new_pattern[-1][1] == 0:
            new_pattern.append((0,0))
        new_sequence.append(new_pattern)
    return new_sequence

# def get_pulse_indices_swab(pattern_swab):
#     return [i for i, j in enumerate(pattern_swab) 
#             if j[1] > 0]
    
# def generate_sweep(sweep_list, pattern, types, chan):
#     indices = get_pulse_indices_swab(pattern)
#     mask = np.zeros(len(pattern))
#     mask[indices] = 1
#     sweep_num = len(sweep_list)
#     full_sweep = np.tile(mask, (sweep_num, 1)) * sweep_list
#     full_sweep_pattern = np.tile(pattern, (sweep_num,1)) + full_sweep
#     return full_sweep_pattern 

    