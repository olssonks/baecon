from baecon import Device

import pyvisa

class SG380(Device):
    
    def __init__(self, configuration:dict=None):
            
        self.parameters = {'frequency': 0,
                           'phase': 0,
                           'amplitude': 0,
                           'enabled': False,
                           'modulation_enabled': False,
                           'modulation_type': 'IQ',
                           'modulation_function': 'External',
                           'modulation_dev': 0,
                           'modulation_rate': 0
                           }
        
        self.latent_parameters = {'IPaddress': '127.0.0.1',
                                  'port': '5025',
                                  'read_termination': 'r\n'}

        self.device = self.connnect_to_device(configuration)
        
        super().__init__(configuration)
        
        for param, value in list(self.parameters.items()):
            self.write(param, value)
        
        return
    
    
    def connnect_to_device(self, configuration:dict):
        connection_settings = configuration['latent_parameters']
        if 'IPaddress' in connection_settings:
            device = self.IP_device_connection(configuration)
        elif 'GPIB' in connection_settings:
            device = self.GPIB_device_connection(configuration)
        else:
            print('No supported connection type found (TCPI or GPIB).')
            print('Connection attempt aborted.')
            return
        
        return device
    
    
    def IP_device_connection(self, configuration:dict):
        """Takes IP address and port from the configuration dictionary and connects
        to the device. If no IP address is given, connection attempt is aborted.
        
        Commmunication handled with `PyVISA-Py <https://pyvisa.readthedocs.io/projects/pyvisa-py/en/latest/index.html>`_.

        Args:
            configuration (dict): Dictionary containing device parameter configruations.

        Returns:
            device: `PyVISA TCPIPSocket <https://pyvisa.readthedocs.io/en/latest/api/resources.html#pyvisa.resources.TCPIPSocket>`_\
            a type of PyVISA resource.
        """    
        try:
            self.address = configuration['latent_parameters']["IPaddress"]
        except KeyError:
            print("IPaddress not specified, check device.")
            print("Device connection aborted.")
            return
        try:
            port = configuration['latent_parameters']["port"]
        except KeyError:
            print("port not specified, using default: 5025")
            return
        try:
            rm = pyvisa.ResourceManager('@py')
            device = rm.open_resource('TCPIP0::'+self.address+'::'+port+'::SOCKET')
            device.read_termination = self.latent_parameters['read_termination']
        except Exception as e:
            if 'timeout' in str(e):
                print('Timeout: Device not found, connection aborted.')
            else:
                print(f'Error: {e}')
                print('Connection aborted.')
        
        return device
        
        
    def GPIB_device_connection(self, configuration:dict):
        """Takes GPIB number and connects to the device. If no GPIB
        is given, connection attempt is aborted.
        
        Commmunication handled with `PyVISA-Py <https://pyvisa.readthedocs.io/projects/pyvisa-py/en/latest/index.html>`_.

        Args:
            configuration (dict): Dictionary containing device parameter configruations.

        Returns:
            device: `PyVISA GPIBInstrument <https://pyvisa.readthedocs.io/en/latest/api/resources.html#pyvisa.resources.GPIBInstrument>`_\
            a type of PyVISA resource.
        """    
        try:
            self.address = configuration['latent_parameters']["GPIB"]
            rm = pyvisa.ResourceManager()
            device = rm.open_resource('GPIB0::'+str(self.address)+'::INSTR')
            device.read_termination = self.latent_parameters['read_termination']
        except KeyError:
            print("GPIB Number not specified, check device configurations.")
            print("Device connection aborted.")
            return
        
        return device
    
    # def intialize_parameters(self, configuration):
    #     '''populate parameters from config file or present device values'''
    #     if "Parameters" in configuration:
    #         for key,value in list(configuration['Parameters'].items()):
    #             self.parameters.update({key: value})
    #     else: 
    #         print('No parameters found, using defaults')
    #         print(self.parameters)
    #     return
    
    def output(self, value):
        self.write('enabled', value)
        return
    
    def write(self, parameter, value):
        """Sends a message to the device to set `parameter` to `value`.
        Messages are ASCII text blocks following the IEEE-488.2 standard `see 
        pg. 54 of the SG380 manual <https://www.thinksrs.com/products/sg380.html>`_
        
        `parameter` is used to index the correct function from the dictionary 
        of command functions.
        
        Reading a value from the device or writing a value to the device 
        depends on if a `?` comes after command. The `read_toggle` argument
        facilitates adding this `?` to the message.
        
        Args:
            parameter (str): Parameter on device to change.
            value (any): New value for the device parameter.
        """        
        msg = self.commands[parameter](self, value, read_toggle='')
        self.device.write(msg)
        self.parameters[parameter] = value
        return
        
        
    def read(self, parameter, value=None):
        """Sends a message to device querying the present value of 
        `parameter`, reads value sent from device and returns it.
        
        Otherwise, details of `write` also apply to `read`.
        
        Args:
            parameter (str): Parameter to get from device.

        Returns:
            int, float, or string: Reading of device parameter.
        """        
        msg = self.commands[parameter](self, value='', read_toggle = '?')
        reading = self.device.query(msg)
        self.parameters[parameter] = reading
        return reading
    

    def freq(self, value, read_toggle):
        """Sets or queries frequency of device. 

        Args:
            value (int or float): Frequency in MHz
            read_toggle (str): Empty or `?` for set or query.

        Returns:
            str: Message to send to device.
        """        
        units = ' MHz'
        value = round(value, 6) ## round to Hz
        message = 'FREQ' + read_toggle + ' ' + str(value) + units
        return message
    
    def phase(self, value, read_toggle):
        """Sets or queries phase of device. 

        Args:
            value (int or float): Phase in degrees.
            read_toggle (str): Empty or `?` for set or query.

        Returns:
            str: Message to send to device.
        """    
        units = '' ## degrees
        value = int(value) ## round to 1 degree
        message = 'PHAS' + read_toggle + ' ' + str(value) + units
        return message
    
    def amp(self, value, read_toggle):
        """Sets or queries amplitude of device. There are two output ports for
        frequencies below 1 MHz (BNC socket: `AMPL`) and above 1 MHz (N-type 
        socket: `AMPR`). Device automatically switchs outpus when changing
        the frequency ranges.

        Args:
            value (str): Amplitude in dBm.
            read_toggle (str): Empty or `?` for set or query.

        Returns:
            str: Message to send to device.
        """    
        if float(self.parameters['frequency']) < 1: ## 1 MHz
            prefix = 'AMPL'
        else:
            prefix = 'AMPR'
        units = '' ## dBm
        value = round(value, 2) ## round to 0.01 dBm
        message = prefix + read_toggle + ' ' + str(value) + units
        return message
    
    def status(self, value, read_toggle):
        """Sets or queries output status of device. Checks BNC socket (`ENBL`) 
        or N-type socket (`ENBR`) for frequencies below or above 1 MHz
        respectively.

        Args:
            value (int or bool): 0/1 or False/True for off/on.
            read_toggle (str): Empty or `?` for set or query.

        Returns:
            str: Message to send to device.
        """    
        ## 0 or 1 for off or on
        if float(self.parameters['frequency']) < 1: ## 1 MHz
            prefix = 'ENBL'
        else:
            prefix = 'ENBR'
        suffix = ''
        units = '' ## no units
        message = prefix + read_toggle + ' ' + str(int(value)) + units
        return message
    
    
    def mod_type(self, value, read_toggle):
        """Sets or queries what type of modulation of device. Device will always
        have a modulation type, but modulation will be enabled or disabled
        by a different command.

        Args:
            value (str): Modulation type to set device to.
            read_toggle (str): Empty or `?` for set or query.

        Returns:
            str: Message to send to device.
        """    
        modulation_types = {'AM': '0', 'FM': '1', 'PM': '2', 
                            'Sweep': '3', 'Pulse': '4', 
                            'Blank': '5', 'IQ':'6'}
        if value == '':
            mod_type = ''
        else:
            mod_type = modulation_types[value]
        message = ('TYPE' + mod_type + read_toggle + ' ')
        return message
        
    
    def mod_function(self, value, read_toggle):
        """Sets or queries what type of modulation function to use, such as 
        ramp or square wave. Depending on the `modulation Type` the communciation
        command changes. 

        Args:
            value (str): Modulation function to use
            read_toggle (_type_): _description_

        Returns:
            str: Message to send to device.
        """ 
        modulation_types = {'AM': ' MFNC', 'FM': ' MFNC', 'PM': 'MFNC', 
                            'Sweep': 'SFNC', 'Pulse': 'PFNC', 
                            'Blank': 'PFNC', 'IQ':'QFNC'}
        
        modulation_functions = {'Sine':'0' , 'Ramp': '1', 'Triangle': '2',
                                'Square':'3', 'Noise': '4', 'External': '5'}
        if value == '':
            func_number = ''
        else:
            func_number = modulation_functions[value]
        message = (modulation_types[self.parameters['modulation_type']] 
                   + read_toggle + func_number)
        return message
    
    def mod_dev(self, value, read_toggle):
        deviation_types = {'AM': ' ADEP', 'FM': ' FDEV', 'PM': 'PDEV', 
                            'Sweep': 'SDEV'}

        message = (deviation_types[self.parameters['modulation_type']] 
                   + read_toggle + str(value))
        return message
    
    def mod_rate(self, value, read_toggle):
        rate_types = {'AM': ' RATE', 'FM': ' RATE', 'PM': 'RATE', 
                            'Sweep': 'SRAT', 'IQ':'RATE'}

        message = (rate_types[self.parameters['modulation_type']] 
                   + read_toggle + str(value))
        return message
        
    
    def mod_enable(self, value, read_toggle):
        """Enables or disables modulation depending on `value` of `1` or `0`

        Args:
            value (int or bool): Enables or disables modulation
            read_toggle (_type_): _description_

        Returns:
            str: Message to send to device.
        """   
        
        message = 'MODL' + read_toggle + str(int(value))
        return message
    
    
    def SetMWSweep(self, center, span, rate):
        ## needs updating
        cntr = center
        dev = span/2
        
        bands = [band * 1e6 for band in \
                 Sweep_bands[self.get_freq_sweep_range(cntr)]
                ]
        
        if (cntr-dev) < bands[0] or (cntr+dev)> bands[1]:
            print('Scan out of range: reduce span or shift center')
        else:
            self.inst.write('MODL 1')
            self.inst.write('TYPE 3') ## 3 for sweep
            self.SetMWFreq(center)
            self.inst.write(f'SDEV {dev} Hz')
            self.inst.write(f'SRAT {rate} Hz')
            self.inst.write('SFNC 1') ## 1 for ramp
        return
    
    commands = {'frequency': freq, 
                'phase': phase,
                'amplitude': amp,
                'enabled': status,
                'modulation_enabled': mod_enable,
                'modulation_type': mod_type,
                'modulation_function': mod_function,
                'modulation_dev': mod_dev,
                'modulation_rate': mod_rate
                }
    
    # translate_dict = {'Frequency': {'command': 'FREQ','units': 'MHz',} 
    #                   'Phase': {'command': 'PHAS', 'units': ''}, #Degrees
    #                   'Amplitude': {'command': 'PHAS', 'units': ''},
    #                   }
## end SRS class