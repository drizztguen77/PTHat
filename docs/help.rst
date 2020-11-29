Help
====

To use this API just import the class or module needed as follows

.. code-block:: python

   from pthat.pthat import Axis


Then you can use it as described in the API documentation. The API will return the serial commands to be sent directly
to the serial device if desired.

There is a flag **auto_send_command** that is a boolean. If this flag is set to true, then when any of the command
methods are called it will automatically send that command to the serial device. If auto_send_command is set to false
then it will not send the command and will just return the command string that needs to be sent to the serial device.

There are several examples that show how to utilize various features in the API. You can find them in the *examples*
directory. The example SimpleAxis.py shows the basics of controlling a single motor.
