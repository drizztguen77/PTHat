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


xaxis = Axis("X", command_id=1, serial_device="/dev/ttyS0")
xaxis.debug = True

# Get the firmware version
firmware_version_cmd = xaxis.get_firmware_version()
xaxis.send_command(firmware_version_cmd)

# Show the responses
wait_for_responses(xaxis, ["RI00FW*", "CI00FW*"], "------- Get firmware version command responses -------")
