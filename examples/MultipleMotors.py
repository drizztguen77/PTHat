"""
This is an example of setting up two motors and starting them at the same time

This example auto sends the commands.
"""
from pthat.pthat import Axis


def show_responses(axis):
    resps = axis.get_all_responses()

    # Parse the responses
    if resps is not None:
        axis.parse_responses(resps)
    else:
        print("No responses received")


def wait_for_responses(responses_to_check, msg):
    responses = xaxis.get_all_responses()
    while not all(x in responses for x in responses_to_check):
        responses = responses + xaxis.get_all_responses()

    # Print the responses
    print(msg)
    xaxis.parse_responses(responses)


steps_per_rev = int(input("How many steps per revolution [1600]? ") or "1600")
total_revolutions = int(input("How many total revolutions [50]? ") or "50")
rpm = int(input("How many RPMs [500]? ") or "500")
direct = input("Direction (Forward = F, Reverse = R) [F]? ") or "F"
direction = 0
if direct.upper() == "F":
    direction = 0
else:
    direction = 1

# X axis
xaxis = Axis("X", command_id=1, serial_device="/dev/ttyS0")
xaxis.debug = True
xaxis.auto_send_command = True

# Calculate frequency and pulse count
frequency = xaxis.rpm_to_frequency(rpm=rpm, steps_per_rev=steps_per_rev, round_digits=3)
pulse_count = xaxis.calculate_pulse_count(steps_per_rev, total_revolutions)

# Setup the X axis
rdc = int(rpm / 10)
xaxis.set_axis(frequency=frequency, pulse_count=pulse_count, direction=direction,
               start_ramp=1, finish_ramp=1, ramp_divide=rdc, ramp_pause=10, enable_line_polarity=1)
# Get the responses - look for both responses to be returned before continuing
wait_for_responses(["RI01CX*", "CI01CX*"], "------- Set X axis command responses -------")


# Y axis
yaxis = Axis("Y", command_id=2, serial_device="/dev/ttyS0")
yaxis.debug = True
yaxis.auto_send_command = True

# Setup the X axis
yaxis.set_axis(frequency=frequency, pulse_count=pulse_count, direction=direction,
               start_ramp=1, finish_ramp=1, ramp_divide=100, ramp_pause=10, enable_line_polarity=1)
# Get the responses - look for both responses to be returned before continuing
wait_for_responses(["RI02CY*", "CI02CY*"], "------- Set Y axis command responses -------")

# Start all motors - either axis can be used to call the start all method
xaxis.start_all()
# Get the responses - look for all responses to be returned before continuing
wait_for_responses(["RI01SX*", "RI02SY*", "CI01SX*", "CI02SY*"], "------- Start all axis command responses -------")
