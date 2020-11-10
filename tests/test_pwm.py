import unittest
from pthat.pthat import PWM


class TestPwm(unittest.TestCase):

    def setUp(self):
        self.pwm = PWM("X", test_mode=True)
        self.pwm.command_type = "I"
        self.pwm.command_id = 00
        self.pwm.wait_delay = 0
        self.pwm.debug = True

    def test_set_channel(self):
        self.assertEqual("I00UX000000000000*", self.pwm.set_channel())

    def test_set_frequency(self):
        self.assertEqual("I00UX100000000000*", self.pwm.set_frequency(frequency=1000000))

    def test_set_duty_cycle(self):
        self.assertEqual("I00UX000000010000*", self.pwm.set_duty_cycle(duty_cycle=100))

    def test_set_both_channels(self):
        self.assertEqual("I00UA000000000000000000000000*", self.pwm.set_both_channels())


if __name__ == '__main__':
    unittest.main()
