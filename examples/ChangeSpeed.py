"""
This is an example of setting up an Axis (motor) and starting it, revving it up to a specified RPM, then changing the
speed up and then finally shutting it down.

This example does not auto send the commands. It gets the command and then sends it to the send_command method.
"""
from pthat.pthat import Axis
import time

ramp_up_speed = 100


def wait_for_responses(axis, responses_to_check, msg):
    responses = axis.get_all_responses()
    while not all(x in responses for x in responses_to_check):
        responses = responses + axis.get_all_responses()

    # Print the responses
    print(msg)
    axis.parse_responses(responses)


def change_speed(axis, old_rpm, new_rpm, ramp_up):
    time.sleep(3)
    old_frequency = axis.rpm_to_frequency(rpm=old_rpm, steps_per_rev=steps_per_rev, round_digits=3)
    new_frequency = axis.rpm_to_frequency(rpm=new_rpm, steps_per_rev=steps_per_rev, round_digits=3)

    resps = None
    for x in range(int(old_frequency), int(new_frequency), int(ramp_up)):
        axis.send_command(axis.change_speed(x))

        # Check for both reply and complete responses to be returned
        wait_for_responses(xaxis, ["RI01QX*", "CI01QX*"], "")

    # Print the responses
    print(f"------- Speed changed to {new_rpm} - command responses -------")
    xaxis.parse_responses(resps)


steps_per_rev = int(input("How many steps per revolution [1600]? ") or "1600")
direction = 0               # Forward
rpm = 300                   # Start RPM
pulse_count = 4294967295    # Set to max so we can start and stop it when desired

xaxis = Axis("X", command_id=1, serial_device="/dev/ttyS0")
xaxis.debug = True

# Setup the axis with values to start the motor
frequency = xaxis.rpm_to_frequency(rpm=rpm, steps_per_rev=steps_per_rev, round_digits=3)
set_axis_cmd = xaxis.set_axis(frequency=frequency, pulse_count=pulse_count, direction=direction,
                              start_ramp=1, finish_ramp=1, ramp_divide=100, ramp_pause=10, enable_line_polarity=1)
xaxis.send_command(set_axis_cmd)
# Get the responses - look for both responses to be returned before continuing
wait_for_responses(xaxis, ["RI01CX*", "CI01CX*"], "------- Set axis command responses -------")

# Start the motor
xaxis.send_command(xaxis.start())
# Check for both reply and complete responses to be returned
wait_for_responses(xaxis, ["RI01SX*"], "------- Start command responses -------")

# Change the speed
# First calculate the ramp up frequency for the original speed
frequency = xaxis.rpm_to_frequency(rpm=rpm, steps_per_rev=steps_per_rev, round_digits=3)
# ramp_up_freq = frequency / ramp_up_speed
ramp_up_freq = 160

# Speed up 100 RPM's
new_speed_rpm_100 = rpm + 100
change_speed(xaxis, rpm, new_speed_rpm_100, ramp_up_freq)

# Speed up 200 more RPM's
new_speed_rpm_200 = new_speed_rpm_100 + 200
change_speed(xaxis, new_speed_rpm_100, new_speed_rpm_200, ramp_up_freq)

time.sleep(3)

# Shut it all down
xaxis.send_command(xaxis.stop())
# Check for both reply and complete responses to be returned
wait_for_responses(xaxis, ["RI01TX*", "CI01SX*"], "------- Stop command responses -------")
