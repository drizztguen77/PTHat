"""
This is an example of setting up an Axis (motor) and starting it, revving it up to a specified RPM and letting it
run for some time and then shutting it down.

This example does not auto send the commands. It gets the command and then sends it to the send_command method.

"""
from pthat.pthat import Axis
import time


def show_responses():
    # Get the responses
    resp = xaxis.get_responses()
    while resp is None:
        print("checking response")
        resp = xaxis.get_responses()

    # Parse the responses
    print(resp)
    if resp is not None:
        xaxis.parse_responses(resp)
    else:
        print("No responses received")


xaxis = Axis("X")
xaxis.command_id = 1
xaxis.debug = True
xaxis.serial_device = "/dev/ttyS0"

# Get the firmware version
firmware_version_cmd = xaxis.get_firmware_version()
xaxis.send_command(firmware_version_cmd)

# Show the responses
# time.sleep(1)
show_responses()
