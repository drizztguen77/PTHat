import unittest
from pthat.pthat import PTHat


class TestPthat(unittest.TestCase):

    def setUp(self):
        self.pthat = PTHat(test_mode=True)
        self.pthat.command_type = "I"
        self.pthat.command_id = 0
        self.pthat.wait_delay = 0
        self.pthat.debug = True

    def test_get_io_port_status(self):
        self.assertEqual("I00LI*", self.pthat.get_io_port_status())

    def test_set_wait_delay_milliseconds(self):
        self.assertEqual("I00WW1000*", self.pthat.set_wait_delay(period="W", delay=1000))

    def test_set_wait_delay_microseconds(self):
        self.assertEqual("I00WM1000*", self.pthat.set_wait_delay(period="M", delay=1000))

    def test_toggle_motor_enable_line(self):
        self.assertEqual("I00HT*", self.pthat.toggle_motor_enable_line())

    def test_received_command_replies_on(self):
        self.assertEqual("I00R1*", self.pthat.received_command_replies_on())

    def test_received_command_replies_off(self):
        self.assertEqual("I00R0*", self.pthat.received_command_replies_off())

    def test_completed_command_replies_on(self):
        self.assertEqual("I00G1*", self.pthat.completed_command_replies_on())

    def test_completed_command_replies_off(self):
        self.assertEqual("I00G0*", self.pthat.completed_command_replies_off())

    def test_get_firmware_version(self):
        self.assertEqual("I00FW*", self.pthat.get_firmware_version())

    def test_initiate_buffer(self):
        self.assertEqual("H0000*", self.pthat.initiate_buffer())

    def test_start_buffer(self):
        self.assertEqual("Z0000*", self.pthat.start_buffer())

    def test_start_buffer_loop(self):
        self.assertEqual("W0000*", self.pthat.start_buffer_loop())

    def test_reset(self):
        self.assertEqual("N*", self.pthat.reset())

    def test_rpm_to_frequency(self):
        self.assertEqual(self.pthat.rpm_to_frequency(rpm=800, steps_per_rev=200, round_digits=0), 2667)

    def test_frequency_to_rpm(self):
        self.assertEqual(self.pthat.frequency_to_rpm(frequency=2667, steps_per_rev=200), 800)

    def test_calculate_pulse_count(self):
        self.assertEqual(self.pthat.calculate_pulse_count(steps_per_rev=200, total_revs=50), 10000)


if __name__ == '__main__':
    unittest.main()
