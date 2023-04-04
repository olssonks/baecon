from NIDAQ_Base import NIDAQ_Base

class NIDAQ_USB6363(NIDAQ_Base):
    
    def __init__(self, configuration:dict)->None:
        
        super().__init__(self, configuration)
        
        if not len(configuration):
            self.properties = self.intialize_properties(self, configuration)
        else:
            self.properties = {'device_name': '',
                               'sample_rate_in': 2e3,
                               'sample_rate_out': 5e3,
                               'analog_in_tasks': [],
                               'analog_in_sample_number': 0,
                               'analog_in_channels': [],
                               'analog_in_clock_source': 'OnBoardClock',
                               'analog_out_tasks': [],
                               'analog_out_sample_number': 0,
                               'analog_out_channels': [],
                               'analog_out_clock_source': 'OnBoardClock'
                               }
        
        return
        
        
    def prep_analog_start_trigger(self, task, trig_channel, trigger_edge='rising', trigger_level=0.0) -> None:
        """Prepares task to start based on the signal from an analogy channel.

        Args:
            task (`task`): _description_
            trig_channel (str): Channel to trigger from. Must be an analog
            channel, e.g., `apfi0` or `ai0`
            trigger_edge (str, optional): Trigger on rising edge or falling edge
            of the signal. Defaults to 'rising'.
            trigger_level (float or int, optional): Signal value when trigger 
            will occur. Defaults to 0.0.
        """    
        chan_name = self.device_name + '/' + trig_channel
        
        trig_edge = self.get_feature('trigger_edge')
        if not trig_edge == None:
            trigger_edge = trig_edge
            
        trig_level = self.get_feature('trigger_level')
        if not trig_level  == None:
            trigger_level = trig_level
        
        task.CfgAnlgEdgeStartTrig(chan_name, 
                                  PyDAQmx_lookup[trig_edge], 
                                  trigger_level)
        
        return
        
        
