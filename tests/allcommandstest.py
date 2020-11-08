
from pthat.pthat import *

# Create the main class
pthat = PTHat(test_mode=True)

# Test PTHat
# Instant Commands
print("PTHat Instant Commands")
pthat.command_id = 1
pthat.debug = True
pthat.wait_delay = 300

pthat.get_io_port_status()
pthat.set_wait_delay("W")
pthat.set_wait_delay("M")
pthat.set_wait_delay("W", 500)
pthat.toggle_motor_enable_line()
pthat.received_command_replies_on()
pthat.received_command_replies_off()
pthat.completed_command_replies_on()
pthat.completed_command_replies_off()
pthat.get_firmware_version()
print("-" * 50)

# Buffer Commands
print("PTHat Buffer Commands")
pthat.command_type = "B"
pthat.command_id = 2
pthat.get_io_port_status()
pthat.set_wait_delay("W")
pthat.set_wait_delay("M")
pthat.set_wait_delay("W", 500)
pthat.toggle_motor_enable_line()
pthat.received_command_replies_on()
pthat.received_command_replies_off()
pthat.completed_command_replies_on()
pthat.completed_command_replies_off()
pthat.get_firmware_version()
pthat.initiate_buffer()
pthat.start_buffer()
pthat.start_buffer_loop()
print("-" * 50)

print("PTHat RPM and Frequency Conversions")
pthat.rpm_to_frequency(rpm=3000, steps_per_rev=200, round_digits=0)
pthat.rpm_to_frequency(rpm=3000, steps_per_rev=200, round_digits=3)
pthat.frequency_to_rpm(frequency=10000, steps_per_rev=200)
# Do reset last so we don't have to set all the variables again
print("-" * 50)

print("PTHat Reset Command")
pthat.reset()

print("-" * 50)
print("-" * 50)

# Test Axis
# Create all 4 valid axis'
print("Axis X Commands")
xaxis = Axis("X", True)
xaxis.debug = True
xaxis.frequency = 10000.0
xaxis.pulse_count = 1234567899
xaxis.direction = 0
xaxis.start_ramp = 0
xaxis.finish_ramp = 0
xaxis.ramp_divide = 0
xaxis.ramp_pause = 255
xaxis.link_to_adc = 0
xaxis.enable_line_polarity = 0
xaxis.pulse_count_change_direction = 1234567899
xaxis.pulse_counts_sent_back = 1234567899
xaxis.enable_disable_x_pulse_count_replies = 1
xaxis.enable_disable_y_pulse_count_replies = 0
xaxis.enable_disable_z_pulse_count_replies = 0
xaxis.enable_disable_e_pulse_count_replies = 0
xaxis.pause_all_return_x_pulse_count = 1
xaxis.pause_all_return_y_pulse_count = 0
xaxis.pause_all_return_z_pulse_count = 0
xaxis.pause_all_return_e_pulse_count = 0

xaxis.set_axis()
xaxis.set_direction_forward()
xaxis.set_direction_reverse()
xaxis.enable_start_ramp()
xaxis.disable_start_ramp()
xaxis.enable_finish_ramp()
xaxis.disable_finish_ramp()
xaxis.enable_line_polarity_0_volts()
xaxis.enable_line_polarity_5_volts()
xaxis.set_auto_direction_change()
xaxis.set_auto_count_pulse_out()
xaxis.start()
xaxis.start_all()
xaxis.stop()
xaxis.stop_all()
xaxis.pause()
xaxis.pause_all()
xaxis.resume()
xaxis.resume_all()
xaxis.get_current_pulse_count()
xaxis.change_speed(frequency=125000.000)
xaxis.enable_limit_switches()
xaxis.disable_limit_switches()
xaxis.enable_emergency_stop()
xaxis.disable_emergency_stop()
xaxis.reset()

print("-" * 50)
print("Axis Y Commands")
yaxis = Axis("Y", True)
yaxis.debug = True
yaxis.frequency = 10000.0
yaxis.pulse_count = 1234567899
yaxis.direction = 0
yaxis.start_ramp = 0
yaxis.finish_ramp = 0
yaxis.ramp_divide = 0
yaxis.ramp_pause = 255
yaxis.link_to_adc = 0
yaxis.enable_line_polarity = 0
yaxis.pulse_count_change_direction = 1234567899
yaxis.pulse_counts_sent_back = 1234567899
yaxis.enable_disable_x_pulse_count_replies = 0
yaxis.enable_disable_y_pulse_count_replies = 1
yaxis.enable_disable_z_pulse_count_replies = 0
yaxis.enable_disable_e_pulse_count_replies = 0
yaxis.pause_all_return_x_pulse_count = 0
yaxis.pause_all_return_y_pulse_count = 1
yaxis.pause_all_return_z_pulse_count = 0
yaxis.pause_all_return_e_pulse_count = 0

yaxis.set_axis()
yaxis.set_direction_forward()
yaxis.set_direction_reverse()
yaxis.enable_start_ramp()
yaxis.disable_start_ramp()
yaxis.enable_finish_ramp()
yaxis.disable_finish_ramp()
yaxis.enable_line_polarity_0_volts()
yaxis.enable_line_polarity_5_volts()
yaxis.set_auto_direction_change()
yaxis.set_auto_count_pulse_out()
yaxis.start()
yaxis.start_all()
yaxis.stop()
yaxis.stop_all()
yaxis.pause()
yaxis.pause_all()
yaxis.resume()
yaxis.resume_all()
yaxis.get_current_pulse_count()
yaxis.change_speed(frequency=125000.000)
yaxis.enable_limit_switches()
yaxis.disable_limit_switches()
yaxis.enable_emergency_stop()
yaxis.disable_emergency_stop()
yaxis.reset()

print("-" * 50)
print("Axis Z Commands")
zaxis = Axis("Z", True)
zaxis.debug = True
zaxis.frequency = 10000.0
zaxis.pulse_count = 1234567899
zaxis.direction = 0
zaxis.start_ramp = 1
zaxis.finish_ramp = 1
zaxis.ramp_divide = 255
zaxis.ramp_pause = 255
zaxis.link_to_adc = 2
zaxis.enable_line_polarity = 1
zaxis.pulse_count_change_direction = 1234567899
zaxis.pulse_counts_sent_back = 1234567899
zaxis.enable_disable_x_pulse_count_replies = 0
zaxis.enable_disable_y_pulse_count_replies = 0
zaxis.enable_disable_z_pulse_count_replies = 1
zaxis.enable_disable_e_pulse_count_replies = 0
zaxis.pause_all_return_x_pulse_count = 0
zaxis.pause_all_return_y_pulse_count = 0
zaxis.pause_all_return_z_pulse_count = 1
zaxis.pause_all_return_e_pulse_count = 0

zaxis.set_axis()
zaxis.set_direction_forward()
zaxis.set_direction_reverse()
zaxis.enable_start_ramp()
zaxis.disable_start_ramp()
zaxis.enable_finish_ramp()
zaxis.disable_finish_ramp()
zaxis.enable_line_polarity_0_volts()
zaxis.enable_line_polarity_5_volts()
zaxis.set_auto_direction_change()
zaxis.set_auto_count_pulse_out()
zaxis.start()
zaxis.start_all()
zaxis.stop()
zaxis.stop_all()
zaxis.pause()
zaxis.pause_all()
zaxis.resume()
zaxis.resume_all()
zaxis.get_current_pulse_count()
zaxis.change_speed(frequency=125000.000)
zaxis.enable_limit_switches()
zaxis.disable_limit_switches()
zaxis.enable_emergency_stop()
zaxis.disable_emergency_stop()
zaxis.reset()

print("-" * 50)
print("Axis Z Commands")
eaxis = Axis("E", True)
eaxis.debug = True
eaxis.frequency = 10000.0
eaxis.pulse_count = 1234567899
eaxis.direction = 1
eaxis.start_ramp = 0
eaxis.finish_ramp = 0
eaxis.ramp_divide = 0
eaxis.ramp_pause = 255
eaxis.link_to_adc = 3
eaxis.enable_line_polarity = 0
eaxis.pulse_count_change_direction = 1234567899
eaxis.pulse_counts_sent_back = 1234567899
eaxis.enable_disable_x_pulse_count_replies = 0
eaxis.enable_disable_y_pulse_count_replies = 0
eaxis.enable_disable_z_pulse_count_replies = 0
eaxis.enable_disable_e_pulse_count_replies = 1
eaxis.pause_all_return_x_pulse_count = 0
eaxis.pause_all_return_y_pulse_count = 0
eaxis.pause_all_return_z_pulse_count = 0
eaxis.pause_all_return_e_pulse_count = 1

eaxis.set_axis()
eaxis.set_direction_forward()
eaxis.set_direction_reverse()
eaxis.enable_start_ramp()
eaxis.disable_start_ramp()
eaxis.enable_finish_ramp()
eaxis.disable_finish_ramp()
eaxis.enable_line_polarity_0_volts()
eaxis.enable_line_polarity_5_volts()
eaxis.set_auto_direction_change()
eaxis.set_auto_count_pulse_out()
eaxis.start()
eaxis.start_all()
eaxis.stop()
eaxis.stop_all()
eaxis.pause()
eaxis.pause_all()
eaxis.resume()
eaxis.resume_all()
eaxis.get_current_pulse_count()
eaxis.change_speed(frequency=125000.000)
eaxis.enable_limit_switches()
eaxis.disable_limit_switches()
eaxis.enable_emergency_stop()
eaxis.disable_emergency_stop()
eaxis.reset()

print("-" * 50)
print("-" * 50)

# Test ADC
# Create all valid ADCs
adc1 = ADC(1, True)
adc2 = ADC(2, True)

print("-" * 50)
print("-" * 50)

# Test AUX
# Create all valid AUXs
aux1 = AUX(1, True)
aux2 = AUX(2, True)
aux3 = AUX(3, True)

print("-" * 50)
print("-" * 50)

# Test PWM
# Create all valid PWMs
pwmx = PWM("X", True)
pwmy = PWM("Y", True)
