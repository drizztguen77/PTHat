import unittest
from pthat.pthat import ADC


class TestAdc(unittest.TestCase):

    def setUp(self):
        self.adc = ADC(1, test_mode=True)
        self.adc.command_type = "I"
        self.adc.command_id = 00
        self.adc.wait_delay = 0
        self.adc.debug = True

    def test_get_reading(self):
        self.assertEqual("I00D1*", self.adc.get_reading())


if __name__ == '__main__':
    unittest.main()
