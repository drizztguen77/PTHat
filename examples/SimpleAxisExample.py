"""
This is an example of setting up an Axis (motor) and starting it, revving it up to a specified RPM and letting it
run for some time and then shutting it down.

This example does not auto send the commands. It gets the command and then sends it to the send_command method.

"""
from pthat.pthat import Axis


def show_responses():
    # Get the responses
    resp = xaxis.get_responses()

    # Parse the responses
    if resp is not None:
        xaxis.parse_responses(resp)
    else:
        print(f"No responses received")


steps_per_rev = int(input("How many steps per revolution [400]? ") or "400")
total_revolutions = int(input("How many total revolutions [20]? ") or "20")
rpm = int(input("How many RPMs [200]? ") or "200")

xaxis = Axis("X")
xaxis.command_id = 1
xaxis.debug = True

# Get the firmware version
firmware_version_cmd = xaxis.get_firmware_version()
xaxis.send_command(firmware_version_cmd)

# Show the responses
show_responses()

# Setup the axis with values to start the motor
xaxis.frequency = xaxis.rpm_to_frequency(rpm=rpm, steps_per_rev=steps_per_rev, round_digits=3)
xaxis.pulse_count = xaxis.calculate_pulse_count(steps_per_rev, total_revolutions)
xaxis.direction = 0                 # clockwise
xaxis.start_ramp = 1                # ramp up
xaxis.finish_ramp = 1               # ramp down
xaxis.ramp_divide = 100             # divide frequency by this for ramp increment
xaxis.ramp_pause = 10               # pause between each ramp increment
xaxis.enable_line_polarity = 1      # 5 volts

set_axis_cmd = xaxis.set_axis()
xaxis.send_command(set_axis_cmd)

# Get the responses - look for both responses to be returned before continuing
responses = xaxis.get_responses()
while not all(x in responses for x in ["RI01CX*", "CI01CX*"]):
    responses = responses + xaxis.get_responses()

# Start the motor
xaxis.send_command(xaxis.start())

# Check for both reply and complete responses to be returned
responses = xaxis.get_responses()
while not all(x in responses for x in ["RI01SX*", "CI01SX*"]):
    responses = responses + xaxis.get_responses()

# Get the pulse count
xaxis.send_command(xaxis.get_current_pulse_count())

# The response should come back with 3 replies
pulse_reply = f"XP0{xaxis.pulse_count:010}*"
responses = xaxis.get_responses()
while not all(x in responses for x in ["RI01XP*", pulse_reply, "CI01XP*"]):
    responses = responses + xaxis.get_responses()

# Print the responses
xaxis.parse_responses(responses)