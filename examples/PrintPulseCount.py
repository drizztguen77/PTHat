"""
This is an example of setting up an Axis (motor) and starting it, revving it up to a specified RPM and letting it
run for some time and then shutting it down.

This example does not auto send the commands. It gets the command and then sends it to the send_command method.
"""
from pthat.pthat import Axis


def wait_for_responses(axis, responses_to_check, msg):
    responses = axis.get_all_responses()
    while not all(x in responses for x in responses_to_check):
        responses = responses + axis.get_all_responses()

    # Print the responses
    print(msg)
    axis.parse_responses(responses)


def print_pulse_count_responses(axis):
    responses = axis.get_all_responses()
    # XP(D)XResult*
    while any(x for x in responses if x.startswith(f"{axis.axis}P")):
        axis.parse_responses(responses)
        responses = axis.get_all_responses()

    axis.parse_responses(responses)


steps_per_rev = int(input("How many steps per revolution [1600]? ") or "1600")
total_revolutions = int(input("How many total revolutions [50]? ") or "50")
rpm = int(input("How many RPMs [500]? ") or "500")
rdc = int(rpm / 10)      # Calculate ramp divide. 10% of rpm seems to work at least up to 1500 rpm
ramp_divide = int(input(f"Ramp divide 0-255 [{rdc}]? ") or f"{rdc}")
ramp_pause = int(input("Ramp pause 0-255 [10]? ") or "10")
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
                              start_ramp=1, finish_ramp=1, ramp_divide=ramp_divide, ramp_pause=ramp_pause, enable_line_polarity=1)
xaxis.send_command(set_axis_cmd)
# Get the responses - look for both responses to be returned before continuing
wait_for_responses(xaxis, ["RI01CX*", "CI01CX*"], "------- Set axis command responses -------")

# Send back pulse count for each full revolution
xaxis.send_command(xaxis.set_auto_count_pulse_out(pulse_count=steps_per_rev, xreplies=1))
wait_for_responses(xaxis, ["RI01JX*"], "------- Set auto count pulse out command responses -------")

# Start the motor
xaxis.send_command(xaxis.start())
# Check for both reply and complete responses to be returned
wait_for_responses(xaxis, ["RI01SX*", "CI01SX*", "DI01JX*"], "------- Start command responses -------")

# Print the pulse counts
print_pulse_count_responses(axis=xaxis)

wait_for_responses(xaxis, ["CI01JX*"], "------- Auto count pulse out command responses complete -------")
