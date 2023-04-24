from baecon import Device

from dataclasses import dataclass, field


@dataclass
class Pulse_Sequence: ## Maybe different name to not be confused with PulseStreamer sequencies
    """To make the scan of the sequence, we'll have a copy or holder of the original sequence
       so that when scanning we are adding/setting time with respect to the orignal sequence
       if start = 4us and scan is add 1,2,3, we want 5, 6, 7 to be out come
       not (4+1), (4+1+2), (4+1+2+3)
    """
    pulses: list = field(default_factory=list)
    pulses_swabian: list = field(default_factory=list)
    channels: list = field(default_factory=list)
    names: list = field(default_factory=list)
    

class PulseStreamer(Device):
    def __init__(self, configuration: dict = None) -> None:
        """Add initionalization specifcs for the type of insturment.

        Args:
            configuration (dict, optional): _description_. Defaults to None.
        """
        self.parameters = {'sequence': "", ##sequence dataclass???
                           'scan_channel': 0,
                           'pulse_names': [],
                           'name_to_scan': ''
                           'scan_catagory': '',
                           'scan_shift': ''
                           'add_time': True
                           }
        
        self.latent_parameters = {'IPaddress': '127.0.0.1'} 
        
        super.__init__(configuration)
        
        return


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
    
    def update_sequence(self, ):
        shift_value = 1.5
        scan_name = 'mw'
        for channel_idx, chan in enumerate(names):
            for name_idx, name in enumerate(chan):
                if name == scan_name:
                    shift_pulses(scan_type, names, pulses, 
                    channel_idx, name_idx, shift_value)
        return
        
    def shift_pulses():
        if no_shift:
            scan_no_shift(scan_type, names, pulses, 
                        channel_idx, name_idx, shift_value)
        elif shift_channel:
            scan_shift_channel(scan_type, names, pulses, 
                        channel_idx, name_idx, shift_value)
        else shift_all:
            scan_shift_all(scan_type, names, pulses, 
                        channel_idx, name_idx, shift_value)
        return
        
    def scan_shift_all(self, scan_type, names, pulses, 
                   channel_idx, name_idx, shift_value):
        if scan_type=='duration':
            if add_time:
                pulses[channel_idx][name_idx][0] += shift_value
            else:
                original_dur = pulses[channel_idx][name_idx-1][0]
                pulses[channel_idx][name_idx-1][0] = shift_value
            ## if sweept pulse is the first in the sequence, 
            ## shift the index 1 to use it to check other pulse start
            if pulses[channel_idx][name_idx-1:name_idx] == []:
                name_idx += 1
        elif scan_type == 'start':
            if add_time:
                pulses[channel_idx][name_idx][0] += shift_value
                shift_for_other_pulses = shift_value
            else:
                original_start = pulses[channel_idx][name_idx][0]
                pulses[channel_idx][name_idx][0] = shift_value
                shift_for_other_pulses = original_start - shift_value
        else:
            print(f'{scan_type} not recognized, us "start" or "duration"')
        ## looking at the other channels to shift the pulse that occurs 
        ## before the scanned pulse, then break since only one shift per 
        ## channel is need
        for other_chan in names: 
            if not other_chan==channel_idx:
                for other_pulse in other_chan:
                    if other_pulse[0] > pulses[channel_idx][name_idx]:
                        other_pulse[0] += shift_for_other_pulses
                        break
        return
    
    def scan_shift_channel(self, scan_type, names, pulses, 
                        channel_idx, name_idx, shift_value):
        if add_time:
            pulses[channel_idx][name_idx][0] += shift_value
        else:
            pulses[channel_idx][name_idx][0] = shift_value
        return
    
    def scan_sequence(sefl, ps:Pulse_Sequence, 
                      catagory:str, amount:float):
        if catagory=='start':
            
        elif catagory == 'duration':
            
        else:
            print(f'Unrecognized scan catagory: {catagory}. Use "start" or "duration"')
        return
    

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

    