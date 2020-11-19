"""
This is an example of setting up an Axis (motor) and starting it, then pausing it and then resuming and letting it
run for some time and then shutting it down.

This example does not auto send the commands. It gets the command and then sends it to the send_command method.
"""
from pthat.pthat import Axis


def show_responses(axis):
    resps = axis.get_all_responses()

    # Parse the responses
    if resps is not None:
        axis.parse_responses(resps)
    else:
        print("No responses received")


steps_per_rev = int(input("How many steps per revolution [1600]? ") or "1600")
total_revolutions = int(input("How many total revolutions [50]? ") or "50")
rpm = int(input("How many RPMs [500]? ") or "500")
direct = input("Direction (Forward = F, Reverse = R) [F]? ") or "F"
direction = 0
if direct.upper() == "F":
    direction = 0
else:
    direction = 1

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

input("Press enter to pause: ")
xaxis.send_command(xaxis.pause())

# Check for the reply response to be returned
responses = xaxis.get_all_responses()
while not all(x in responses for x in ["RI01PX*"]):
    responses = responses + xaxis.get_all_responses()

# Print the responses
print(f"------- Pause command responses -------")
xaxis.parse_responses(responses)

input("Press enter to resume: ")
xaxis.send_command(xaxis.resume())

# Check for both reply and complete responses to be returned
responses = xaxis.get_all_responses()
while not all(x in responses for x in ["RI01PX*", "CI01PX*"]):
    responses = responses + xaxis.get_all_responses()

# Print the responses
print(f"------- Resume command responses -------")
xaxis.parse_responses(responses)

# Get the pulse count
xaxis.send_command(xaxis.get_current_pulse_count())

# The response should come back with 3 replies
pulse_reply = f"XP{xaxis.direction}{xaxis.pulse_count:010}*"
responses = xaxis.get_all_responses()
while not all(x in responses for x in ["RI01XP*", pulse_reply, "CI01XP*"]):
    responses = responses + xaxis.get_all_responses()

# Print the responses
print(f"------- Get pulse count command responses -------")
xaxis.parse_responses(responses)
