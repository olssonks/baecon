import serial

"""
Old Class, needs to be converted to a baecon Device.
"""


### TPI Command hex codes '\x08\x09'->'0809'

CMD_get = "07"
CMD_set = "08"

CMD_Freq = "09"
CMD_Ampl = "0A"
CMD_Stat = "0B"
CMD_User = "01"
CMD_Trig = "13"
CMD_FreqIncr = "21"
CMD_FreqIncr = "1C"
CMD_Scan = "27"


class TPI:
    """
    General Functions
        Initialze(port)

        getMWAmpl() in dBm
        setMWAmpl(power) in dBm

        getMWFreq() in GHz
        setMWFreq(freq) in GHz

        getMWStat() returns on/off
        setMWStat(bool) turns output on/off

        close()

    TPI specific
        Reset()

        GetMWSweepFreqIncr()
        SetMWSweepFreqIncr()


    """

    def __init__(self):
        ## default scan parameters
        self.sp_default = {
            "freq_func": 0,  ## no scan
            "freq_high": 110000,  ## kHz
            "freq_low": 100000,  ## kHz
            "ampl_func": 0,  ## no scan
            "ampl_high": 2,  ## dBm
            "ampl_low": 0,  ## dBm
            "scan_type": 1,  ## 1/2 incr freq/ampl or 3/4 fit freq/ampl
            "freq_incr": 1000,  ## kHz
            "ampl_incr": 1,  ## dBm
            "freq_time": 100,  ## ms
            "ampl_time": 100,  ## ms
            "tote_time": 1000,  ## ms (not used here)
            "status": 00,  ## 0/1 for off/on
            "scan_num": 0,  ## 0 thru 60e3, 0 = Continuous
            "scan_gap": 5,  ## ms
            "stat_gap": 0,  ## 0/1 for output on/off between scans
            "freq_gap": 0,  ## 0/1 for jump to low or stay high in gap
            "ampl_gap": 0,  ## 0/1 for don't/do step between scan
            "ampl_rep": 0,  ## repeat ampl sequence (???, not used here)
        }
        self.sp = self.sp_default
        return

    def Initialize(self, port):
        self.port = port
        self.inst = serial.Serial(
            port,
            baudrate=3e6,
            bytesize=8,
            parity=serial.PARITY_NONE,
            stopbits=1,
            timeout=10,
            rtscts=True,  ## Request-to-Send handshake
        )

        cmd = CMD_get + CMD_User
        msg = self.hex_message(cmd)
        self.inst.write(msg)

        ret_msg = self.read(7 + 1).hex()
        ret_control = ret_msg[-8:-2]
        user_control = cmd + "01"  ## 01 returned if user control enabled

        init_good = """
            TPI Ininitialization Succesful
            User Control Established
            """
        init_bad = """
            TPI Ininitialization Failed
            """

        if ret_control == user_control:
            print(init_good)
        else:
            print(init_bad)

        return

    def Reset(self):
        self.inst.reset_input_buffer()
        self.inst.reset_output_buffer()

        cmd = CMD_get + CMD_User
        msg = self.hex_message(cmd)
        self.inst.write(msg)

        ret_msg = self.read(7 + 1).hex()
        ret_control = ret_msg[-8:-2]
        user_control = cmd + "01"  ## 01 returned if user control enabled

        reset_good = """
            TPI Reset Succesful
            User Control Established
            """
        reset_bad = """
            TPI Rest Failed
            """

        if ret_control == user_control:
            print(reset_good)
        else:
            print(reset_bad)

        return

    def getMWAmpl(self):
        ## ampl values single bytes denoting dBm
        ## need hex value of second to last byte
        cmd = CMD_get + CMD_Ampl
        msg = self.hex_message(cmd)
        self.inst.write(msg)

        ret_msg = self.read(7 + 1).hex()

        ## want last bytes (2 characters) sans checksum
        ampl_u = int(ret_msg[-4:-2], 16)  ## yields unsigned integer
        ampl = uint8_to_int8(ampl_u)

        return ampl

    def SetMWAmpl(self, ampl_setting):
        ## ampl_setting will be in dBm from -90 to +10
        ## convert int to unsigned int, then convert to single byte hex value
        ampl_hex = f"{ampl_setting & 0xFF:0x}"

        cmd = CMD_set + CMD_Ampl
        msg = self.hex_message(cmd, setting=ampl_hex)
        self.inst.write(msg)
        ret_msg = self.read(7 + 1).hex()
        ## additional single byte of power level returned

        if not confirm_setting(cmd, ret_msg):
            print("TPI did not properly receive Power Command")

        int(ret_msg[-4:-2], 16)  ## yield unsigned integer
        ampl_ret = uint8_to_int8(ampl_u)

        if not ampl_ret == ampl_setting:
            print(f"Power not set to requested value, set to {ampl_ret}.")

        return

    def GetMWFreq(self):
        ## freq values are four bytes long in kHz units given from least
        ## to most significant, message returned is 7 + 6 bytes long
        ## need hex value of second to last byte

        cmd = CMD_get + CMD_Freq
        msg = self.hex_message(cmd)
        self.inst.write(msg)
        ret_msg = self.read(7 + 4).hex()

        ret_freq = ret_msg[-10:-2]  ## last 4 bytes (8 characters) sans checksum

        freq_array = [ret_freq[i : i + 2] for i in range(0, len(setting), 2)]
        freq_array.reverse()  ## put most sig. byte first
        freq = int("".join(freq_array), 16)  ## integer from hex base

        return freq

    def SetMWFreq(self, freq_setting):
        ## freq_setting will be in kHz from 35 to 4400000
        ## convert int to unsigned int, then convert to four byte hex value
        freq_hex = f"{freq_setting & 0xFF:08x}"

        cmd = CMD_set + CMD_Freq
        msg = self.hex_message(cmd, setting=freq_hex)
        self.inst.write(msg)
        ret_msg = self.read(7 + 0).hex()
        ## no setting bytes returned

        if not confirm_setting(cmd, ret_msg):
            print("TPI did not properly receive Frequency Command")

        return

    def GetMWStat(self):
        ## freq values are four bytes long in kHz units given from least
        ## to most significant, message returned is 7 + 6 bytes long
        ## need hex value of second to last byte

        cmd = CMD_get + CMD_Stat
        msg = self.hex_message(cmd)
        self.inst.write(msg)
        ret_msg = self.read(7 + 1).hex()

        ## last 4 bytes (8 characters) sans checksum
        ret_stat = int(ret_msg[-4:-2])

        stat_dict = {"0": "Off", "1": "On"}

        return stat_dict[ret_stat]

    def SetMWSet(self, stat_setting):
        ## ampl_setting will be in dBm from -90 to +10
        ## convert int to unsigned int, then convert to single byte hex value
        stat_hex = f"{stat_setting & 0xFF:0x}"

        cmd = CMD_set + CMD_Stat
        msg = self.hex_message(cmd, setting=stat_hex)
        self.inst.write(msg)
        ret_msg = self.read(7 + 0).hex()
        ## no setting bytes returned

        if not confirm_setting(cmd, ret_msg):
            print("TPI did not properly receive On/Off Command")

        return

    def SetFreqScan(self, freq_low, freq_high, steps, duration=10):
        ## frequencies given in MHz, convert to kHz

        freq_incr = (freq_high - freq_low) / steps * 10e3

        self.sp["freq_low"] = freq_low * 10e3
        self.sp["freq_high"] = freq_high * 10e3
        self.sp["freq_incr"] = int(freq_incr)  ## round to kHz
        self.sp["freq_time"] = duration

        self.SetScanParams()

        return

    def SetScanParams(self):
        """
        Converts scan parameters dictionary to proper 41 byte scan string
        TPI always needs to be sent some values within the accepted range
        for all scan parameters
        """
        scan_msg = ""

        scan_msg += "{:02x}".format(self.sp["freq_func"])
        scan_msg += self.LSB_order("{:08x}".format(self.sp["freq_high"]))
        scan_msg += self.LSB_order("{:08x}".format(self.sp["freq_low"]))

        scan_msg += "{:02x}".format(self.sp["ampl_func"])
        scan_msg += self.LSB_order("{:04x}".format(int(self.sp["ampl_high"] & 0xFF)))
        scan_msg += self.LSB_order("{:04x}".format(int(self.sp["ampl_low"] & 0xFF)))

        scan_msg += "{:02x}".format(self.sp["scan_type"])

        scan_msg += self.LSB_order("{:08x}".format(self.sp["freq_incr"]))
        scan_msg += "{:02x}".format(self.sp["ampl_incr"])

        scan_msg += self.LSB_order("{:08x}".format(self.sp["freq_time"]))
        scan_msg += self.LSB_order("{:08x}".format(self.sp["ampl_time"]))
        scan_msg += self.LSB_order("{:08x}".format(self.sp["tote_time"]))

        scan_msg += "{:02x}".format(self.sp["status"])

        scan_msg += self.LSB_order("{:04x}".format(self.sp["scan_num"]))
        scan_msg += self.LSB_order("{:04x}".format(self.sp["scan_gap"]))

        scan_msg += "{:02x}".format(self.sp["stat_gap"])
        scan_msg += "{:02x}".format(self.sp["freq_gap"])
        scan_msg += "{:02x}".format(self.sp["ampl_gap"])
        scan_msg += "{:02x}".format(self.sp["ampl_rep"])

        if not (len(scan_msg) == 82):
            "Scan message not formatted correctly"
        else:
            pass

        return scan_msg

    ### Utility Functions
    """
    communication done in hex, all commands have form:
        [4 byte header] [body bytes] [checksum byte]
        header: always begins with 0xAA, 0x55
                3rd byte is high order byte of 16 bit integer telling number of
                bytes in the body
                4th byte is low order byte of the 16 bit integer
        body: communicates operation to TPI
        checksum: 0xFF - (3rd header by + 4th header byte + body bytes)
    """

    def hex_message(self, cmd, setting=[]):
        """
        args
            cmd: Four character string denoting the two hex values for the
                 for the operation to the TPI to perform
            setting: Even character string denoting hex values of setting
                     value to set the TPI to. Number of characters depends
                     on the operation, e.g. freq = 8 characters
                     * only need setting when change values on TPI

        return
            byte array of message to send to the TPI
        """

        header = "AA55"
        ## TPI wants setting least to most significant bytes of setting
        ##
        setting_array = [setting[i : i + 2] for i in range(0, len(setting), 2)]
        setting_array.reverse()

        inst_array = [cmd[:2], cmd[2:], *setting_array]
        instruction = "".join(inst_array)

        # four character hex value denoting number of bits in instruction
        instruction_length = f"{len(inst_array):04x}"

        checksum = perform_checksum(inst_array)

        message = header + instruction_length + instruction + checksum

        return bytes.fromhex(message)

    def perform_checksum(self, byte_array):
        """
        args
            byte: array of two character elements denoting hex value
        return
            two character string denoting checksum hex value
        """

        ## four character hex value denoting number of bits in instruction
        array_length = f"{len(byte_array):04x}"

        ## integer sum of bytes
        byte_sum = int(array_length[:2], 16) + int(array_length[2:], 16)
        for bite in byte_array:
            byte_sum += int(bite, 16)

        ## ones' compliment of integer sum
        ## cannot just use '~byte_sum' since Python uses twos' compliment
        ## on integers since integers are signed by default:
        ## i.e. 8bit int: -128,...0,1,...127
        ## need to use unsigned int: i.e. 8bit uint: 0, ...127,128,...255
        ## use (~byte_sum & 0xFF), where 0x forces operate to happen with uint
        ## 0xF forces 4bit uint, 0xFF forces 8bit, etc.
        ## TPI wants an 8bit checksum value, i.e. single byte hex value
        ## https://stackoverflow.com/questions/7278779...
        ## .../bit-wise-operation-unary-invert

        return hex(~byte_sum & 0xFF)[2:]

    def confirm_setting(self, cmd, returned_hex):
        """
        The TPI will send back the two cmd bytes if the setting is changed

        arg
            cmd: Four character string denoting the two hex values
            returned_hex: full hex array that was read from the TPI

        return
            boolean: True is returned cmd bytes match sent cmd bytes
        """

        ## first 4 bytes (8 characters) are the header bytes
        ## bytes 5 and 6  (9th, 10th, 11th, and 12th characters) are
        ## the cmd bytes
        returned_cmd = returned_hex[8:12]

        return cmd == returned_cmd

    def LSB_order(self, msg):
        """
        orders message into least significant byte (LSB) first
        arg
            msg: byte value in hex, even number string
        return
            string of hex bytes in proper LSB order
        """
        msg_array = [msg[i : i + 2] for i in range(0, len(msg), 2)]
        msg_array.reverse()
        msg_LSB = "".join(msg_array)

        return msg_LSB

    def uint8_to_int8(uinteger):
        binary_str = f"{uinteger:08b}"

        n_length = len(binary_str)

        integer = -1 * int(binary_str[0]) * 2 ** (n_length - 1)

        for N, dig in enumerate(binary_str[-1:-n_length:-1]):
            integer += int(dig) * 2**N

        return integer


##### End TPI class
