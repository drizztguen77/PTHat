"""
This is an example of setting up an Axis (motor) and starting it, revving it up to a specified RPM, then changing the
speed up and then finally shutting it down. This one changes the speed by using the set command which includes ramp up.

This example does not auto send the commands. It gets the command and then sends it to the send_command method.
"""
from pthat.pthat import Axis
import time

ramp_up_speed = 100


def show_responses(axis):
    resps = axis.get_all_responses()

    # Parse the responses
    if resps is not None:
        axis.parse_responses(resps)
    else:
        print("No responses received")


def change_speed(axis, new_rpm):
    time.sleep(3)
    new_frequency = axis.rpm_to_frequency(rpm=new_rpm, steps_per_rev=steps_per_rev, round_digits=3)

    change_speed_set_axis_cmd = xaxis.set_axis(frequency=new_frequency, pulse_count=pulse_count, direction=direction,
                                               start_ramp=1, finish_ramp=1, ramp_divide=100, ramp_pause=10,
                                               enable_line_polarity=1)
    xaxis.send_command(change_speed_set_axis_cmd)

    # Check for both reply and complete responses to be returned
    resps = axis.get_all_responses()
    while not all(x in responses for x in ["RI01SX*"]):
        resps = resps + axis.get_all_responses()

    # Print the responses
    print(f"------- Speed changed to {new_rpm} - command responses -------")
    xaxis.parse_responses(resps)


steps_per_rev = int(input("How many steps per revolution [1600]? ") or "1600")
total_revolutions = int(input("How many total revolutions [50]? ") or "50")
rpm = int(input("How many RPMs to start with [400]? ") or "400")
direction = 0               # Forward

xaxis = Axis("X", command_id=1, serial_device="/dev/ttyS0")
xaxis.debug = True

# Setup the axis with values to start the motor
frequency = xaxis.rpm_to_frequency(rpm=rpm, steps_per_rev=steps_per_rev, round_digits=3)
pulse_count = xaxis.calculate_pulse_count(steps_per_rev, total_revolutions)

set_axis_cmd = xaxis.set_axis(frequency=frequency, pulse_count=pulse_count, direction=direction,
                              start_ramp=1, finish_ramp=1, ramp_divide=100, ramp_pause=10, enable_line_polarity=1)
xaxis.send_command(set_axis_cmd)

# Get the responses - look for both responses to be returned before continuing
responses = xaxis.get_all_responses()
while not all(x in responses for x in ["RI01CX*", "CI01CX*"]):
    responses = responses + xaxis.get_all_responses()

# Print the responses
print(f"------- Set axis command responses -------")
xaxis.parse_responses(responses)

# Start the motor
xaxis.send_command(xaxis.start())

# Check for both reply and complete responses to be returned
responses = xaxis.get_all_responses()
while not all(x in responses for x in ["RI01SX*"]):
    responses = responses + xaxis.get_all_responses()

# Print the responses
print(f"------- Start command responses -------")
xaxis.parse_responses(responses)

# Change the speed
# First calculate the ramp up frequency for the original speed
frequency = xaxis.rpm_to_frequency(rpm=rpm, steps_per_rev=steps_per_rev, round_digits=3)
# ramp_up_freq = frequency / ramp_up_speed
ramp_up_freq = 160

# Speed up 100 RPM's
new_speed_rpm_100 = rpm + 100
change_speed(xaxis, new_speed_rpm_100)

# Speed up 200 more RPM's
new_speed_rpm_200 = new_speed_rpm_100 + 200
change_speed(xaxis, new_speed_rpm_200)

time.sleep(3)

# Shut it all down
xaxis.send_command(xaxis.stop())

# Check for both reply and complete responses to be returned
responses = xaxis.get_all_responses()
while not all(x in responses for x in ["RI01TX*", "CI01SX*"]):
    responses = responses + xaxis.get_all_responses()

# Print the responses
print(f"------- Stop command responses -------")
xaxis.parse_responses(responses)
