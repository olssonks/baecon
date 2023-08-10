import pyvisa

"""
Old class, needs to be converted to baecon Device
"""


class SG4400L:
    """
    General Functions
        getMWampl() in dBm
        getMWfreq() in GHz
        getMWstat()

        setMWampl(power) in dBm
        setMWfreq(freq) in GHz
        setMWstat(bool) turns output on/off

        close()

    DSI specific
        getVernier()
        setVernier(power) in arb. unit

        reset()

    """

    def __init__(self, IPaddress, port=10001):  ## DSI tcpip port number
        ## create, open, and configure connection
        rm = pyvisa.ResourceManager("@py")
        self.inst = rm.open_resource("TCPIP0::" + IPaddress + "::" + port + "::SOCKET")
        self.inst.read_termination = "\r\n"  ## specific termination for DSI
        return

    def GetMWAmpl(self):
        reading = self.inst.query("POWER?")
        ## always returned in as string ending with 'dBm'
        ## ex: '-1.1dBm'
        return float(reading[:-3])

    def GetMWFreq(self):
        reading = self.inst.query("FREQ:CW?")
        ## always returned in as string ending with 'HZ'
        ## ex: 400 MHZ read as '400000000HZ'
        return float(reading[:-2]) / 1e9

    def GetMWStat(self):
        reading = self.inst.query("OUTP:STAT?")
        if reading == "OFF":
            state = 0
        elif reading == "ON":
            state = 1
        else:
            print("Error: output state not read correctly")
            state = "error"
        return state

    def SetMWAmpl(self, value):
        ## value in dBm (-45 to +15)
        prefix = "POWER "
        suffix = ""  ## no suffix needed
        value = round(value * 2) / 2  ## rounds to 0.5 steps (DSI limited)
        msg = prefix + value + suffix
        self.inst.write(msg)
        return

    def SetMWFreq(self, value):
        ## value in GHz from 35MHz to 4.4 GHz in 1 Hz resolution
        prefix = "FREQ:CW "
        suffix = " HZ"  ## always inputs in Hz units
        value = value * 1e9  ## rounds to 0.5 steps (DSI limited)
        msg = prefix + str(value) + suffix
        self.inst.write(msg)
        return

    def SetMWFreq(self, value):
        ## 0 or 1 for off or on
        prefix = "OUTPUT:STAT "
        suffix = ""
        if value == 1:
            state = "ON"
        elif value == 0:
            state = "OFF"
        else:
            print("Value must be 0 or 1 for off or on")
            state = "OFF"  ## defaults to
        state = value * 1e9  ## rounds to 0.5 steps (DSI limited)
        msg = prefix + state + suffix
        self.inst.write(msg)
        return

    def GetVernier(self):
        reading = self.inst.query("VERNIER?")  ## no units
        return float(reading)

    def SetVernier(self, value):
        ## interger from -300 to 50 with no units
        prefix = "VERNIER "
        suffix = ""
        value = int(value)

        if -301 < value and value < 51:
            ## no change needed
            pass
        elif value < -300:
            print("Setting too low, set to -300 instead.")
            print("Setting must be between -300 and 50.")
            value = -300
        elif 50 < value:
            print("Setting too high, set to 50 instead.")
            print("Setting must be between -300 and 50.")
            value = 50
        else:
            print("Unable to read setting, set to 0 instead.")
            value = 0

        msg = prefix + str(value) + suffix
        self.inst.write(msg)

        return

    def Reset(self):
        self.inst.write("*RST")
        return
