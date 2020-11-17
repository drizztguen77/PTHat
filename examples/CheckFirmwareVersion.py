"""
This is an example of setting up an Axis (motor) and starting it, revving it up to a specified RPM and letting it
run for some time and then shutting it down.

This example does not auto send the commands. It gets the command and then sends it to the send_command method.

"""
from pthat.pthat import Axis


def show_responses(axis):
    responses = axis.get_all_responses()

    # Parse the responses
    if responses is not None:
        xaxis.parse_responses(responses)
    else:
        print("No responses received")


xaxis = Axis("X", command_id=1, serial_device="/dev/ttyS0")
xaxis.debug = True

# Get the firmware version
firmware_version_cmd = xaxis.get_firmware_version()
xaxis.send_command(firmware_version_cmd)

# Show the responses
show_responses(xaxis)
