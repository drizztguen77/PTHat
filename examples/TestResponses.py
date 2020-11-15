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
    resp = get_responses(axis)
    while resp is not None:
        responses.extend(resp)
        resp = get_responses(axis)

    # Parse the responses
    print(responses)
    if resp is not None:
        xaxis.parse_responses(resp)
    else:
        print("No responses received")


def get_responses(axis):
    """
    This method gets the responses from the serial port. It calls a callback method that can
    be implemented to do whatever is needed based on the response.
    """
    resp_string = ""
    responses = None
    if not axis.test_mode:
        response_waiting_size = axis.serial.in_waiting
        while response_waiting_size > 0:
            if axis.debug:
                print(f"response waiting size: {response_waiting_size}")
            # read serial buffer
            response_bytes = axis.serial.read(response_waiting_size or 1)
            # convert bytes to string
            resp_string += response_bytes.decode()
            print(f"resp_string : {resp_string}")

            # Find the end of the response
            response_index = resp_string.rfind(axis._command_end)
            if response_index >= 0:
                # create list of responses
                responses = resp_string[0:response_index].split(axis._command_end)
                # add incomplete response for next check
                resp_string = resp_string[response_index:]
                print(f"Incomplete bytes: {resp_string}")

            # See if there is any more to read
            response_waiting_size = axis.serial.in_waiting
            print(f"Remaining bytes waiting: {response_waiting_size}")

    return responses


xaxis = Axis("X")
xaxis.command_id = 1
xaxis.debug = True
xaxis.serial_device = "/dev/ttyS0"

# Get the firmware version
firmware_version_cmd = xaxis.get_firmware_version()
xaxis.send_command(firmware_version_cmd)

# Show the responses
#time.sleep(1)
show_responses(xaxis)
