"""
This is an example of setting up an Axis (motor) and starting it, revving it up to a specified RPM and letting it
run for some time and then shutting it down.

This example does not auto send the commands. It gets the command and then sends it to the send_command method.

"""
from pthat.pthat import Axis
import time


response_string = ""


def show_responses(axis):
    # Get the responses
    resp = get_responses(axis, response_string)
    while resp is None or resp == "":
        resp += get_responses(axis, response_string)

    # Parse the responses
    print(resp)
    if resp is not None:
        xaxis.parse_responses(resp)
    else:
        print("No responses received")


def get_responses(axis, resp_string):
    """
    This method gets the responses from the serial port. It calls a callback method that can
    be implemented to do whatever is needed based on the response.
    """
    responses = None
    if not axis.test_mode:
        response_waiting_size = 0
        while axis.serial.in_waiting <= 7:
            response_waiting_size = axis.serial.in_waiting

        if response_waiting_size:
            if axis.debug:
                print(f"response waiting size: {response_waiting_size}")
            # read serial buffer
            response_bytes = axis.serial.read(response_waiting_size)
            # convert bytes to string
            resp_string += response_bytes.decode()
            # Find the end of the response
            response_index = resp_string.rfind(axis._command_end)
            # create list of responses
            responses = resp_string[0:response_index].split(axis._command_end)
            # add incomplete response for next check
            resp_string = resp_string[response_index:]
            print(resp_string)

    return responses


xaxis = Axis("X")
xaxis.command_id = 1
xaxis.debug = True
xaxis.serial_device = "/dev/ttyS0"

# Get the firmware version
firmware_version_cmd = xaxis.get_firmware_version()
xaxis.send_command(firmware_version_cmd)

# Show the responses
# time.sleep(1)
show_responses(xaxis)
