import unittest
from pthat.pthat import Axis


class TestAxis(unittest.TestCase):

    def setUp(self):
        self.axis = Axis("X", command_type="I", command_id=0, test_mode=True)
        self.axis.debug = True
        self.axis.frequency = 125000.0
        self.axis.pulse_count = 4294967295
        self.axis.direction = 1
        self.axis.start_ramp = 1
        self.axis.finish_ramp = 1
        self.axis.ramp_divide = 100
        self.axis.ramp_pause = 10
        self.axis.link_to_adc = 0
        self.axis.enable_line_polarity = 1
        self.axis.pulse_count_change_direction = 0
        self.axis.pulse_counts_sent_back = 0
        self.axis.wait_delay = 0
        self.axis.enable_disable_x_pulse_count_replies = 1
        self.axis.enable_disable_y_pulse_count_replies = 1
        self.axis.enable_disable_z_pulse_count_replies = 1
        self.axis.enable_disable_e_pulse_count_replies = 1
        self.axis.pause_all_return_x_pulse_count = 0
        self.axis.pause_all_return_y_pulse_count = 0
        self.axis.pause_all_return_z_pulse_count = 0
        self.axis.pause_all_return_e_pulse_count = 0

    def test_set_axis(self):
        self.assertEqual("I00CX125000.000429496729511110001001*", self.axis.set_axis())

    def test_set_direction_forward(self):
        self.assertEqual("I00CX125000.000429496729501110001001*", self.axis.set_direction_forward())

    def test_set_direction_reverse(self):
        self.assertEqual("I00CX125000.000429496729511110001001*", self.axis.set_direction_reverse())

    def test_enable_start_ramp(self):
        self.assertEqual("I00CX125000.000429496729511110001001*", self.axis.enable_start_ramp())

    def test_disable_start_ramp(self):
        self.assertEqual("I00CX125000.000429496729510110001001*", self.axis.disable_start_ramp())

    def test_enable_finish_ramp(self):
        self.assertEqual("I00CX125000.000429496729511110001001*", self.axis.enable_finish_ramp())

    def test_disable_finish_ramp(self):
        self.assertEqual("I00CX125000.000429496729511010001001*", self.axis.disable_finish_ramp())

    def test_enable_line_polarity_0_volts(self):
        self.assertEqual("I00CX125000.000429496729511110001000*", self.axis.enable_line_polarity_0_volts())

    def test_enable_line_polarity_5_volts(self):
        self.assertEqual("I00CX125000.000429496729511110001001*", self.axis.enable_line_polarity_5_volts())

    def test_set_auto_direction_change(self):
        self.axis.pulse_count_change_direction = 100
        self.assertEqual("I00BX0000000100*", self.axis.set_auto_direction_change())

    def test_set_auto_count_pulse_out(self):
        self.axis.pulse_counts_sent_back = 100
        self.axis.enable_disable_x_pulse_count_replies = 1
        self.axis.enable_disable_y_pulse_count_replies = 0
        self.axis.enable_disable_z_pulse_count_replies = 0
        self.axis.enable_disable_e_pulse_count_replies = 0
        self.assertEqual("I00JX00000001001000*", self.axis.set_auto_count_pulse_out())

    def test_start(self):
        self.assertEqual("I00SX*", self.axis.start())

    def test_start_all(self):
        self.assertEqual("I00SA*", self.axis.start_all())

    def test_stop(self):
        self.assertEqual("I00TX*", self.axis.stop())

    def test_stop_all(self):
        self.assertEqual("I00TA*", self.axis.stop_all())

    def test_pause(self):
        self.assertEqual("I00PX0000*", self.axis.pause())

    def test_pause_all(self):
        self.assertEqual("I00PA0000*", self.axis.pause_all())

    def test_resume(self):
        self.assertEqual("I00PX0000*", self.axis.resume())

    def test_resume_all(self):
        self.assertEqual("I00PA0000*", self.axis.resume_all())

    def test_get_current_pulse_count(self):
        self.assertEqual("I00XP*", self.axis.get_current_pulse_count())

    def test_change_speed(self):
        self.assertEqual("I00QX001000.000*", self.axis.change_speed(new_frequency=1000.000))

    def test_enable_limit_switches(self):
        self.assertEqual("I00KX1*", self.axis.enable_limit_switches())

    def test_disable_limit_switches(self):
        self.assertEqual("I00KX0*", self.axis.disable_limit_switches())

    def test_enable_emergency_stop(self):
        self.assertEqual("I00KS1*", self.axis.enable_emergency_stop())

    def test_disable_emergency_stop(self):
        self.assertEqual("I00KS0*", self.axis.disable_emergency_stop())


if __name__ == '__main__':
    unittest.main()
