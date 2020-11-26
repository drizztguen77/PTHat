"""
This just stops the motor in case a bug is encountered leaving the motor running.
"""
from pthat.pthat import Axis


xaxis = Axis("X", test_mode=True)

rpm = int(input("Enter RPM to calculate: "))
ramp_up_speed = int(input("Enter ramp up speed: "))
steps_per_rev = int(input("Enter the steps per revolution: "))

frequency = xaxis.rpm_to_frequency(rpm=rpm, steps_per_rev=steps_per_rev, round_digits=3)
if ramp_up_speed == 0:
    ramp_up_freq = frequency
else:
    ramp_up_freq = frequency / ramp_up_speed
ramp_up_rpm = xaxis.frequency_to_rpm(frequency=ramp_up_freq, steps_per_rev=steps_per_rev)

print(f"Ramp up: {ramp_up_freq} Hz = {ramp_up_rpm} RPM")
