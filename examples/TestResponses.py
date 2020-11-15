"""
This is an example of setting up an Axis (motor) and starting it, revving it up to a specified RPM and letting it
run for some time and then shutting it down.

This example does not auto send the commands. It gets the command and then sends it to the send_command method.

"""
from pthat.pthat import Axis
import time

response_size = 7


def show_responses(axis):
    responses = []
    # Get the responses
    resp = get_response(axis)
    while resp is not None:
        responses.append(resp)
        resp = get_response(axis)

    # Parse the responses
    print(responses)
    if resp is not None:
        xaxis.parse_responses(resp)
    else:
        print("No responses received")


def get_response(axis):
    """
    This method gets the responses from the serial port. It calls a callback method that can
    be implemented to do whatever is needed based on the response.
    """
    resp_string = None
    if not axis.test_mode:
        response_waiting_size = axis.serial.in_waiting
        while 0 < response_waiting_size <= response_size:
            response_waiting_size = axis.serial.in_waiting

        if response_waiting_size:
            if axis.debug:
                print(f"response waiting size: {response_waiting_size}")
            # read serial buffer
            response_bytes = axis.serial.read(response_waiting_size)
            # convert bytes to string
            resp_string = response_bytes.decode()
            print(f"resp_string : {resp_string}")

    return resp_string


xaxis = Axis("X")
xaxis.command_id = 1
xaxis.debug = True
xaxis.serial_device = "/dev/ttyS0"

# Get the firmware version
firmware_version_cmd = xaxis.get_firmware_version()
xaxis.send_command(firmware_version_cmd)

# Show the responses
time.sleep(1)
show_responses(xaxis)
