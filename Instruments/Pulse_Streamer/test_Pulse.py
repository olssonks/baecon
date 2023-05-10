import unittest

from Pulse_Streamer import Pulse


class Test_Pulse(unittest.TestCase):

    def test_init(self)->None:
        test_pulse = Pulse('RABI', 0.5, 1)
        
        self.assertEqual(test_pulse.type, 'RABI')
        self.assertEqual(test_pulse.duration, 0.5)
        self.assertEqual(test_pulse.start_time, 1.0)
        self.assertEqual(test_pulse.end_time, 1.5)
        return
        
if __name__ == '__main__':
    unittest.main()