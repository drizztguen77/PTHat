"""
This is an example of setting up an Axis (motor) and starting it, revving it up to a specified RPM, then changing the
speed up and down and then finally shutting it down.

This example does not auto send the commands. It gets the command and then sends it to the send_command method.
"""
from pthat.pthat import Axis
import time


def show_responses(axis):
    resps = axis.get_all_responses()

    # Parse the responses
    if resps is not None:
        axis.parse_responses(resps)
    else:
        print("No responses received")


def change_speed(axis, revspermin):
    time.sleep(3)
    new_frequency = axis.rpm_to_frequency(rpm=revspermin, steps_per_rev=steps_per_rev, round_digits=3)
    axis.send_command(axis.change_speed(new_frequency))

    # Check for both reply and complete responses to be returned
    resps = axis.get_all_responses()
    while not all(x in resps for x in ["RI01QX*", "CI01QX*"]):
        resps = resps + axis.get_all_responses()

    # Print the responses
    print(f"------- Speed changed to {revspermin} - command responses -------")
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
change_speed(xaxis, rpm + 100)
change_speed(xaxis, rpm + 200)

# Shut it all down
xaxis.send_command(xaxis.stop())

# Check for both reply and complete responses to be returned
responses = xaxis.get_all_responses()
while not all(x in responses for x in ["RI01TX*", "CI01SX*"]):
    responses = responses + xaxis.get_all_responses()

# Print the responses
print(f"------- Stop command responses -------")
xaxis.parse_responses(responses)
