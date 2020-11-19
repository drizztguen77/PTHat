"""
This just stops the motor in case a bug is encountered leaving the motor running.
"""
from pthat.pthat import Axis


xaxis = Axis("X", command_id=1, serial_device="/dev/ttyS0")
xaxis.auto_send_command = True

xaxis.stop()
