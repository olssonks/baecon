import sys
sys.path.insert(0,'C:\\Users\\walsworth1\\Documents\\Jupyter_Notebooks\\baecon')
import baecon as bc

from baecon import Device

from dataclasses import dataclass, field
import numpy as np

import pulsestreamer

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
    total_duration: float
    ps_output     : list = field(default_factory=list)
    pulses        : list = field(default_factory=list)
    pulses_swabian: list = field(default_factory=list)
    types         : list = field(default_factory=list)
    types_swabian : list = field(default_factory=list)
    
@dataclass
class Pulse:
    """Data structure for defining a pulse. 
    
       The data structure is simple and can be easily shared between different
       devices. 
    """    
    type      : str
    duration  : float
    start_time: float
    end_time  : float = field(init=False)
    def __post_init__(self):
        self.end_time = self.duration + self.start_time
    
## under score in the name to differentiate between pulsestreamer.PulseStreamer
class Pulse_Streamer(Device):
    
    def __init__(self, configuration: dict) -> None:
        """Set parameters for this `Device` class and connect to physical 
        instrument

        Args:
            configuration (dict, optional): Dictionary of device parameters.
                Defaults defined here will be used if no `configuration` is
                provided.
        """
        self.parameters = {'sequence'     : {},
                           'type_to_scan' : 'pi/2',
                           'scan_catagory': 'start',
                           'scan_shift'   : 'no_shift',
                           'add_time'     : True,
                           'loop_number'  : -1 ## infinite
                           }
        
        self.latent_parameters = {'IPaddress': '127.0.0.1'} 
        
        self.device, self.pulse_sequence = self.connect_to_device(configuration)
        
        super.__init__(configuration)
        
        self.sequence = Pulse_Sequence()
        
        ## need methods for dictionary to/from Pulse_Sequence
        
        return

    def connect_to_device(self, configuration) -> tuple(pulsestreamer.PulseStreamer,
                                                        pulsestreamer.Sequence):
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
        connection_settings = configuration['latent_parameters']
        if 'IPaddress' in connection_settings:
            self.latent_parameters.update({'IPaddress': connection_settings['IPaddress']})
            ps_device = pulsestreamer.PulseStreamer(self.latent_parameters['IPaddress'])
            sequence = ps_device.CreateSequence()
        else:
            print('No IPaddress specificed in "latent_parameters".')
        return ps_device, sequence

    # Writing and Reading will be device specfic as connect types and command are all different
    def write(self, parameter:str, value:float) -> None:
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
        new_pulses = self.update_pulses(parameter, value)
        self.update_device(new_pulses)
        self.device.stream(self.parameters['sequence'].pulses_swabian, 
                           int(self.parameters['loop_number']))
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
        
    
    def update_device(self, new_pulses:list[Pulse]) -> None:
        """Sends pulse sequence to the Pulse Streamer device.
        
        We need to individually update each channel on the Pulse Streamer. 
        This methods loops through the channels defined in `Pulse_Streamer.ps_output`
        which lists the Pulse Streamer output channels for the sequence. A full
        pulse pattern (single channel pulse sequence) is sent to a Pulse Streamer
        channel.

        Args:
            new_pulses (_type_): New pulse sequence to send to the device. These
                have been updated based on the `parameter` and `value` entries.
        """    
        for ch_idx, channel in enumerate(new_pulses):
            ## check if channel is analog or digital
            ## ps_outputs in form 'PS-0',...,'PS-7', 'PS-A0', 'PS-A1'
            ps_output = self.parameters['sequence'].ps_output[ch_idx]
            if "A" in ps_output:
                self.pulse_sequence.setAnalog(
                    int(ps_output[-1]), 
                    self.parameters['sequence'].pulses_swabian[ch_idx]
                    )
            else:
                self.pulse_sequence.setDigital(
                    int(ps_output[-1]), 
                    self.parameters['sequence'].pulses_swabian[ch_idx]
                    )
        return
    
    def update_pulses(self, scan_category:str, shift_value:float)->list[Pulse]:
        """Generates new pulse sequence to send to the Pulse Streamer device.
        
           This sequence is in the Pulse Streamer format, i.e., the `pulses_swabian`
           sequence is updated and returned.

        Args:
            scan_category (_type_): _description_
            shift_value (_type_): _description_

        Returns:
            list: _description_
        """    
        for channel_idx, chan in enumerate(self.parameters['sequence'].ps_output):
            for type_idx, name in enumerate(self.parameters['sequence']\
                                            .types_swabian[channel_idx]):
                if name == self.parameters['type_to_scan']:
                    new_pulses = self.shift_pulses(
                        scan_category, 
                        self.parameters['sequence'].types_swabian, 
                        self.parameters['sequence'].pulses_swabian,
                        channel_idx, type_idx, shift_value
                        )
        return new_pulses
        
    def shift_pulses(self, scan_category:str, types:list[str], pulses:list[Pulse], 
                     channel_idx:int, type_idx:int, shift_value:int) -> list[Pulse]:
        """Updates `pulses_swabian`, the Pulse Streamer format of the pulse 
           sequence based on type of shift.

        Args:
            scan_category (str): _description_
            types (list): _description_
            pulses (list): _description_
            channel_idx (int): _description_
            type_idx (int): _description_
            shift_value (int): _description_

        Returns:
            _type_: _description_
        """        
        if self.parameters['scan_shift'] == 'no_shift':
           new_pulses = self.scan_no_shift(scan_category, types, pulses, 
                        channel_idx, type_idx, shift_value)
        elif self.parameters['scan_shift'] == 'shift_channel':
            new_pulses = self.scan_shift_channel(scan_category, types, pulses, 
                        channel_idx, type_idx, shift_value)
        elif self.parameters['scan_shift'] == 'shift_all':
           new_pulses =  self.scan_shift_all(scan_category, types, pulses, 
                        channel_idx, type_idx, shift_value)
        else:
            print(f"Unrecognized shift type: {self.parameters['scan_shift']}")
        return new_pulses

      
    def scan_shift_all(self, scan_category:str, types:list[str], pulses:list[Pulse], 
                   channel_idx:int, type_idx:int, shift_value:int) -> list[Pulse]:
        
        if scan_category=='duration':
            self.shift_all_duration(pulses, channel_idx, type_idx, shift_value)
        elif scan_category == 'start':
            shift_for_other_pulses \
            = self.shift_all_start(pulses, channel_idx, type_idx, shift_value)
        else:
            print(f'{scan_category} not recognized, us "start" or "duration"')

        for other_chan in types: 
        ## looking at the other channels to shift, then break since only 
        ## one shift per channel is need
            if not other_chan==channel_idx:
                for other_pulse in other_chan:
                    if other_pulse.start_time > pulses[channel_idx][type_idx]:
                        other_pulse.start_time += shift_for_other_pulses
                        break
        return pulses
        
    def shift_all_duration(self, pulses:list[Pulse], channel_idx:int, 
                           type_idx:int, shift_value:int) -> None:
        if self.parameters['add_time']:
            pulses[channel_idx][type_idx].start_time += shift_value
        else:
            original_dur = pulses[channel_idx][type_idx-1].start_time
            pulses[channel_idx][type_idx-1].start_time = shift_value
        ## if sweept pulse is the first in the sequence, 
        ## shift the index 1 to use it to check other pulse start
        if pulses[channel_idx][type_idx-1:type_idx] == []:
            type_idx += 1
        return
        
    def shift_all_start(self, pulses:list[Pulse], channel_idx:int, 
                        type_idx:int, shift_value:int) -> int:
        if self.parameters['add_time']:
            pulses[channel_idx][type_idx].start_time += shift_value
            shift_for_other_pulses = shift_value
        else:
            original_start = pulses[channel_idx][type_idx].start_time
            pulses[channel_idx][type_idx].start_time = shift_value
            shift_for_other_pulses = original_start - shift_value
        return shift_for_other_pulses
    
    
    def scan_shift_channel(self, scan_category:str, types:list[Pulse], pulses:list[Pulse], 
                   channel_idx:int, type_idx:int, shift_value:int) -> None:
        if self.parameters['add_time']:
            pulses[channel_idx][type_idx].start_time += shift_value
        else:
            pulses[channel_idx][type_idx].start_time = shift_value
        return


    def scan_no_shift(self, scan_category:str, types:list[Pulse], pulses:list[Pulse], 
                   channel_idx:int, type_idx:int, shift_value:int) -> None:
        if scan_category == 'duration':
            self.no_shift_duration(self, pulses, channel_idx, type_idx, shift_value)
        elif scan_category == 'start':
            self.no_shift_start(self, pulses, channel_idx, type_idx, shift_value)
        else:
            print(f'{scan_category} not recognized, us "start" or "duration"')
            
        return

    def no_shift_duration(self, pulses:list[Pulse], channel_idx:int, 
                          type_idx:int, shift_value:int) -> None:
        if self.parameters['add_time']:
            pulses[channel_idx][type_idx].start_time += shift_value
        else:
            original_dur = pulses[channel_idx][type_idx].start_time
            pulses[channel_idx][type_idx].start_time = shift_value
        if not pulses[channel_idx][type_idx:type_idx+1] in [[], [0,0]]:
            pulses[channel_idx][type_idx+1] += original_dur - shift_value
        return

    def no_shift_start(self, pulses:list[Pulse], channel_idx:int, 
                       type_idx:int, shift_value:int):
        if self.parameters['add_time']:
            if pulses[channel_idx][type_idx-1:type_idx] in [[],[0,0]]:
                print(f'Pulse {pulses[channel_idx][type_idx]} in channel \
                        {channel_idx} cannot shift start time without a pulse before it.')
                ## if not prior pulse, do nothing
            else:
                original_start = pulses[channel_idx][type_idx-1].start_time
                pulses[channel_idx][type_idx-1].start_time = shift_value
        if not pulses[channel_idx][type_idx:type_idx+1] in [[], [0,0]]:
            pulses[channel_idx][type_idx+1] =+ original_start - shift_value
        return


    def convert_Pulse_Sequence(self) -> None:
        pulses = self.parameters['sequence'].pulses
        types  = self.parameters['sequence'].types
        
        pulses_swabian, types_swabian = self.convert_to_swabian(pulses, types)
        
        self.parameters['sequence'].pulses_swabian = pulses_swabian
        self.parameters['sequence'].types_swabian  = types_swabian
        return
    
    def convert_to_swabian(self, sequence:list, types:list[str]) -> tuple[list]:
        """Take sequence in "human readable" sequence format and turns it into
           the proper format for the PulseStreamer device.
           
           "Human readable" means a pulses in a pulse sequence is defined by
           their absolute start time and their duration. The PulseStreamer takes
           pulses in the format of relative start time, i.e., how long after the
           end of the last pulst, and duration as well. 

        Args:
            self (_type_): _description_
            list (_type_): _description_

        Returns:
            _type_: _description_
        """        
        new_sequence = []
        new_types = []
        for ch_idx, chan in enumerate(sequence):
            new_pattern = []
            names_holder = []
            duration_counter = 0
            for p_idx, pulse in enumerate(chan):
                start = pulse.start_time-duration_counter
                p1 = (start, 0)
                p2 = (pulse.duration, 1)
                duration_counter = start+pulse.duration
                new_pattern.extend([p1, p2])
                names_holder.extend(('Zero', types[ch_idx][p_idx]))
            if not new_pattern[-1][1] == 0:
                ## capping all patterns with (0,0) will pad anything that is 
                ## shorter than the longest pulse pattern with zeros in that 
                ## channel until the end of the sequence
                new_pattern.append((0,0))
                names_holder.append('Zero')
            new_sequence.append(new_pattern)
            new_types.append(names_holder)
        return (new_sequence, new_types,)

if __name__ == "__main__":
