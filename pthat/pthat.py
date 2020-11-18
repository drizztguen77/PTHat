"""
Pulse Train Hat Python API
==========================

This API contains classes for the Pulse Train Hat module sold by CNC Design Ltd.

This contains :class:'PTHat' class. This class provides all the primary functionality for the serial command interface
as well as all general commands. It basically builds the commands and sends them to the serial port as specified in
the command interface at http://pthat.com/index.php/command-set/

It includes the ability to run both instant and buffered commands. All commands currently existing for the PTHat
are included in the API.

It also contains supporting classes for :class:'Axis', :class:'ADC', :class:'AUX' and :class:'PWM' commands. Each of
the supporting classes extend the PTHat class.

author:  Curtis White

.. code-block:: python

    from pthat import *

    <put code here after classes are written>
"""
import serial


class PTHat:
    """
    This is the main Pulse Train Hat class. It is used to run commands against the PTHat and to run general commands.
    """
    # Properties
    _version = "0.9.10"  # Version of this API
    command_type = "I"  # I = Instant or B = Buffer
    command_id = 0      # Optional command ID
    debug = False       # Sets debug mode. This just prints additional information
    test_mode = False   # This lets all methods to be run without actually sending them to the serial port
    wait_delay = 0      # Wait delay between commands - 0-9999 -
    #                     Delay in milliseconds: 1000ms = 1 second delay,
    #                     Delay in microseconds: 1000us = 0.001 of a second
    auto_send_command = False   # Automatically send the command when command methods are called
    serial = None       # The serial device

    _motor_enabled = False   # Specifies if the motor is enabled or not. Do not set this as it is set internally
    _received_command_replies_enabled = False    # if received command replies are enabled or not
    _completed_command_replies_enabled = False   # if completed command replies are enabled or not
    _command_end = "*"      # end of command

    __buffer_value = 0000   # Value sent in Byte 2-5 for all buffer commands
    __response_string = ""  # response string from PTHat

    # Generic commands
    __request_port_status_command = "LI"  # Request IO Port Status Command
    __set_wait_delay_command = "W"        # Set wait delay between commands - WW = Milliseconds, WM = Microseconds
    __toggle_motor_enable_line_command = "HT"  # Toggle motor enable line on/off
    __received_command_on_off_replies_command = "R"   # Turn on/off Received Command Replies
    __completed_command_on_off_replies_command = "G"  # Turn on/off Completed Command Replies
    __request_firmware_version_command = "FW"  # Request firmware version command
    __reset_pthat_command = "N"  # Reset the PTHat

    __initiate_buffer_command = "H"    # Initiate the buffer command
    __start_buffer_command = "Z"       # Start the buffer command
    __buffer_loop_start_command = "W"  # Buffer loop start command

    def __init__(self, command_type="I", command_id=0, serial_device="/dev/ttyS0", baud_rate=115200, test_mode=False):
        """
        Constructor

        :param command_type: type of command, I = instant, B = buffered - default I
        :param command_id: optional command ID, 0-99 - default 0
        :param serial_device: serial device - default /dev/ttyS0
        :param baud_rate: serial port baud rate - default 115200
        :param test_mode: if true then serial commands will not actually be sent - default False
        """
        super().__init__()

        self.command_type = command_type
        self.command_id = command_id
        self.serial_device = serial_device  # default to /dev/ttyS0
        self.baud_rate = baud_rate  # default baud rate
        self.test_mode = test_mode

        if not test_mode:
            self.__serial = self.init_serial_interface()  # create serial port object and open it
            self.serial = self.__serial

    def __del__(self):
        """
        Destructor
        """
        # send command to stop all and then close the serial device
        self.reset()
        if not self.test_mode:
            self.__serial.close()

    @property
    def motor_enabled(self):
        """
        Read-only property
        """
        return self._motor_enabled

    @property
    def received_command_replies_enabled(self):
        """
        Read-only property
        """
        return self._received_command_replies_enabled

    @property
    def completed_command_replies_enabled(self):
        """
        Read-only property
        """
        return self._completed_command_replies_enabled

    @property
    def command_end(self):
        """
        Read-only property
        """
        return self._command_end

    @property
    def version(self):
        """
        Read-only property
        """
        return self._version

    def init_serial_interface(self, write_timeout=2, timeout=2):
        """
        Initializes the serial port

        :param write_timeout: write timeout - default 2
        :param timeout: read timeout - default 2
        :return: serial port object
        """
        try:
            return serial.Serial(
                port=self.serial_device,
                baudrate=self.baud_rate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                xonxoff=False,
                rtscts=False,
                write_timeout=write_timeout,
                timeout=timeout
            )
        except Exception as e:
            print(f"Error opening serial port /n/l {e}")
            return False

    def send_command(self, command):
        """
        This method sends the command to the serial port asynchronously

        :param command: command to send
        """
        # TODO change to asynchronous call maybe
        if not self.test_mode:
            self.__serial.write(bytes(command, 'utf-8'))

    def get_all_responses(self):
        """
        This method gets all responses until no more can be returned

        :return: a list of responses
        """
        # TODO make asynchronous maybe and implement callback that the responses are sent to
        responses = []

        # Get all the responses
        resp = self.get_response()
        while resp is not None:
            responses.append(resp)
            resp = self.get_response()

        return responses

    def get_response(self):
        """
        This method gets a single response. A response is the value returned up to an *.

        :return: a single response as a string
        """
        resp_string = None

        # read serial buffer in bytes
        response_bytes = self.__serial.read_until(self._command_end.encode())

        if response_bytes is not None and len(response_bytes) > 0:
            # convert bytes to string
            resp_string = response_bytes.decode()

        return resp_string

    def parse_responses(self, responses):
        """
        Parse the list of responses and set the various values in the class. Returns responses that were not parsed as
        some responses may come from the other classes such as Axis or AUX.

        :param responses: list of responses to parse
        """
        if responses is not None:
            for resp in responses:
                if resp != "":
                    if self.debug:
                        print(f"Response: {resp}")

        # TODO finish this parsing

    def get_io_port_status(self):
        """
        When this request is sent, it will return the state of the Emergency Stop input port and each of the
        Limit Switch input ports. This allows them to be used as general inputs when limits disabled.

        :return: the command to send to the serial port

        Command:

        Byte1	Byte 2-3	Byte 4-5	Byte 6
        ---------------------------------------------------------------------------------------------------------------
        I	    00	        LI	        *

        Command breakdown:

        Byte	    Setting	                Description
        ---------------------------------------------------------------------------------------------------------------
        Byte 1	    I=Instant Command       Sets command to either Instant or Buffer.
                    B=Buffer Command
        Byte 2-3	0-99	                Optional Command ID
        Byte 4-5	LI = Port Status	    Request current Port Status
        Byte 6	    *	                    End of Command

        The PTHAT will send back a reply when it receives a command and also when it has completed a command.
        In this case the received command will be sent back along with the state of the ES/Limit inputs and then
        completed command. If the Command sent ID number was set for bytes 2-3, then this will be returned in the reply.

        IO Port Status Received
        *Result*	                    IO Port Status Completed
        ---------------------------------------------------------------------------------------------------------------
        RI00LI**Result*	                CI00LI*

        *Result* will show as
        L11111*
        Bit5=ES input
        Bit4=X Limit input
        Bit3=Y Limit input
        Bit2=Z Limit input
        Bit1=E Limit input
        """
        if not self._validate_command():
            return False

        command = f"{self.command_type}{self.command_id:02}{self.__request_port_status_command}{self._command_end}"
        if self.debug:
            print(f"get_io_port_status command: {command}")
        if self.auto_send_command:
            self.send_command(command=command)
        return command

    def set_wait_delay(self, period="W", delay=None):
        """
        When this request is sent, it causes a wait delay between buffered commands.
        Typical use is when switching one of the AUX outputs and you want to wait a while for it to complete.
        Note this is a wait and will pause the firmware routines, so do not use if a pulse train channel is running.
        You can set the Wait period to be in Milliseconds or Microseconds.

        :param period: period of time for the delay, W = Milliseconds, M = Microseconds - default W
        :param delay: length of delay - default 0
        :return: the command to send to the serial port

        Command:

        Byte1	Byte 2-3	Byte 4-5	Byte 6-9	Byte 10
        ---------------------------------------------------------------------------------------------------------------
        I	    00	        WW	        1000	    *

        Command breakdown:

        Byte	    Setting	                Description
        ---------------------------------------------------------------------------------------------------------------
        Byte 1	    I=Instant Command       Sets command to either Instant or Buffer.
                    B=Buffer Command
        Byte 2-3	0-99	                Optional Command ID
        Byte 4-5	WW = Milliseconds       Set Wait Delay in either Milliseconds or Microseconds
                    WM = Microseconds
        Byte 6-9	0-9999	                Delay in ms so 1000ms = 1 second delay
                                            Delay is us so 1000us = 0.001 of a second
        Byte 10	    *	                    End of Command

        The PTHAT will send back a reply when it receives a command and also when it has completed a command.
        If the Command sent ID number was set for bytes 2-3, then this will be returned in the reply.

        Received        Completed
        ---------------------------------------------------------------------------------------------------------------
        R00WW*	        C00WW*
        """
        if not self._validate_command():
            return False

        if not period == "W" and not period == "M":
            print(f"Invalid period {period}")
            return False

        if delay is not None:
            self.wait_delay = delay

        if not self._validate_values(self.wait_delay, 0, 9999):
            print(f"Invalid wait delay {delay}")
            return False

        command = f"{self.command_type}{self.command_id:02}{self.__set_wait_delay_command}{period}" \
                  f"{self.wait_delay:04}{self._command_end}"
        if self.debug:
            print(f"set_wait_delay command: {command}")
        if self.auto_send_command:
            self.send_command(command=command)
        return command

    def toggle_motor_enable_line(self):
        """
        Toggles the Motor Enable Line

        :return: the command to send to the serial port

        Command:

        Byte1	Byte 2-3	Byte 4-5	Byte 6
        ---------------------------------------------------------------------------------------------------------------
        I	    00	        HT	        *

        Command breakdown:

        Byte	    Setting	                Description
        ---------------------------------------------------------------------------------------------------------------
        Byte 1	    I=Instant Command       Sets command to either Instant or Buffer.
                    B=Buffer Command
        Byte 2-3	0-99	                Optional Command ID
        Byte 4-5    HT                      Toggle Motor Enable Line On/Off
        Byte 6	    *	                    End of Command

        The PTHAT will send back a reply when it receives a command and also when it has completed a command.
        If the Command sent ID number was set for bytes 2-3, then this will be returned in the reply.

        Toggle Enable Command Received          Toggle Enable Command Completed
        ---------------------------------------------------------------------------------------------------------------
        R00HT*	                                C00HT*
        """
        if not self._validate_command():
            return False

        self._motor_enabled = not self._motor_enabled

        command = f"{self.command_type}{self.command_id:02}{self.__toggle_motor_enable_line_command}{self._command_end}"
        if self.debug:
            print(f"toggle_motor_enable_line command: {command}")
        if self.auto_send_command:
            self.send_command(command=command)
        return command

    def received_command_replies_on(self):
        """
        Turns on the Received Replies.

        :return: the command to send to the serial port

        Command:

        Byte1	Byte 2-3	Byte 4-5	Byte 6
        ---------------------------------------------------------------------------------------------------------------
        I	    00	        R1	        *

        Command breakdown:

        Byte	    Setting	                Description
        ---------------------------------------------------------------------------------------------------------------
        Byte 1	    I=Instant Command       Sets command to either Instant or Buffer.
                    B=Buffer Command
        Byte 2-3	0-99                    Optional Command ID
        Byte 4-5	R1 = Turn On            Turn on/off Received Command Replies
                    R0 = Turn Off
        Byte 6	    *	                    End of Command

        The PTHAT will send back a reply when it receives a command and also when it has completed a command.
        If the Command sent ID number was set for bytes 2-3, then this will be returned in the reply.

        Received Command Replies    Received Command Replies    Received Command Replies    Received Command Replies
        Turned On                   Turned Off                  Turned On                   Turned Off
        Received                    Received                    Completed                   Completed
        ---------------------------------------------------------------------------------------------------------------
        RI00R1*	                    RI00R0*	                    CI00R1*	                    CI00R0*
        """
        if not self._validate_command():
            return False

        self._received_command_replies_enabled = True

        command = f"{self.command_type}{self.command_id:02}{self.__received_command_on_off_replies_command}1" \
                  f"{self._command_end}"
        if self.debug:
            print(f"received_command_replies_on command: {command}")
        if self.auto_send_command:
            self.send_command(command=command)
        return command

    def received_command_replies_off(self):
        """
        Turns off the Received Replies.

        :return: the command to send to the serial port

        Command:

        Byte1	Byte 2-3	Byte 4-5	Byte 6
        ---------------------------------------------------------------------------------------------------------------
        I	    00	        R0	        *

        Command breakdown:

        Byte	    Setting	                Description
        ---------------------------------------------------------------------------------------------------------------
        Byte 1	    I=Instant Command       Sets command to either Instant or Buffer.
                    B=Buffer Command
        Byte 2-3	0-99                    Optional Command ID
        Byte 4-5	R1 = Turn On            Turn on/off Received Command Replies
                    R0 = Turn Off
        Byte 6	    *	                    End of Command

        The PTHAT will send back a reply when it receives a command and also when it has completed a command.
        If the Command sent ID number was set for bytes 2-3, then this will be returned in the reply.

        Received Command Replies    Received Command Replies    Received Command Replies    Received Command Replies
        Turned On                   Turned Off                  Turned On                   Turned Off
        Received                    Received                    Completed                   Completed
        ---------------------------------------------------------------------------------------------------------------
        RI00R1*	                    RI00R0*	                    CI00R1*	                    CI00R0*
        """
        if not self._validate_command():
            return False

        self._received_command_replies_enabled = False

        command = f"{self.command_type}{self.command_id:02}{self.__received_command_on_off_replies_command}0" \
                  f"{self._command_end}"
        if self.debug:
            print(f"received_command_replies_off command: {command}")
        if self.auto_send_command:
            self.send_command(command=command)
        return command

    def completed_command_replies_on(self):
        """
        Turns on the Completed Replies.

        :return: the command to send to the serial port

        Command:

        Byte1	Byte 2-3	Byte 4-5	Byte 6
        ---------------------------------------------------------------------------------------------------------------
        I	    00	        G1	        *

        Command breakdown:

        Byte	    Setting	                Description
        ---------------------------------------------------------------------------------------------------------------
        Byte 1	    I=Instant Command       Sets command to either Instant or Buffer.
                    B=Buffer Command
        Byte 2-3	0-99                    Optional Command ID
        Byte 4-5	G1 = Turn On            Turn on/off Completed Command Replies
                    G0 = Turn Off
        Byte 6	    *	                    End of Command

        The PTHAT will send back a reply when it receives a command and also when it has completed a command.
        If the Command sent ID number was set for bytes 2-3, then this will be returned in the reply.

        Received Command Replies    Received Command Replies    Received Command Replies    Received Command Replies
        Turned On                   Turned Off                  Turned On                   Turned Off
        Received                    Received                    Completed                   Completed
        ---------------------------------------------------------------------------------------------------------------
        RI00G1*	                    RI00G0*	                    CI00G1*	                    CI00G0*
        """
        if not self._validate_command():
            return False

        self._completed_command_replies_enabled = True

        command = f"{self.command_type}{self.command_id:02}{self.__completed_command_on_off_replies_command}1" \
                  f"{self._command_end}"
        if self.debug:
            print(f"completed_command_replies_on command: {command}")
        if self.auto_send_command:
            self.send_command(command=command)
        return command

    def completed_command_replies_off(self):
        """
        Turns off the Completed Replies.

        :return: the command to send to the serial port

        Command:

        Byte1	Byte 2-3	Byte 4-5	Byte 6
        ---------------------------------------------------------------------------------------------------------------
        I	    00	        G0	        *

        Command breakdown:

        Byte	    Setting	                Description
        ---------------------------------------------------------------------------------------------------------------
        Byte 1	    I=Instant Command       Sets command to either Instant or Buffer.
                    B=Buffer Command
        Byte 2-3	0-99                    Optional Command ID
        Byte 4-5	G1 = Turn On            Turn on/off Completed Command Replies
                    G0 = Turn Off
        Byte 6	    *	                    End of Command

        The PTHAT will send back a reply when it receives a command and also when it has completed a command.
        If the Command sent ID number was set for bytes 2-3, then this will be returned in the reply.

        Received Command Replies    Received Command Replies    Received Command Replies    Received Command Replies
        Turned On                   Turned Off                  Turned On                   Turned Off
        Received                    Received                    Completed                   Completed
        ---------------------------------------------------------------------------------------------------------------
        RI00G1*	                    RI00G0*	                    CI00G1*	                    CI00G0*
        """
        if not self._validate_command():
            return False

        self._completed_command_replies_enabled = False

        command = f"{self.command_type}{self.command_id:02}{self.__completed_command_on_off_replies_command}0" \
                  f"{self._command_end}"
        if self.debug:
            print(f"completed_command_replies_off command: {command}")
        if self.auto_send_command:
            self.send_command(command=command)
        return command

    def get_firmware_version(self):
        """
        Requests the Firmware Version from the PTHAT

        :return: the command to send to the serial port

        Command:

        Byte1	Byte 2-3	Byte 4-5	Byte 6
        ---------------------------------------------------------------------------------------------------------------
        I	    00	        FW	        *

        Command breakdown:

        Byte	    Setting	                Description
        ---------------------------------------------------------------------------------------------------------------
        Byte 1	    I=Instant Command       Sets command to either Instant or Buffer.
                    B=Buffer Command
        Byte 2-3	0-99	                Optional Command ID
        Byte 4-5	FW                      Request Firmware
        Byte 6	    *	                    End of Command

        The PTHAT will send back a reply when it receives a command and also when it has completed a command.
        If the Command sent ID number was set for bytes 2-3, then this will be returned in the reply.

        Firmware Command Received       Firmware Command Completed
        *Version*
        ---------------------------------------------------------------------------------------------------------------
        RI00FW**Version*	            CI00FW*
        """
        if not self._validate_command():
            return False

        command = f"{self.command_type}{self.command_id:02}{self.__request_firmware_version_command}{self._command_end}"
        if self.debug:
            print(f"get_firmware_version command: {command}")
        if self.auto_send_command:
            self.send_command(command=command)
        return command

    def reset(self):
        """
        Resets the PTHAT back to turn on state and resets all pulse generators.
        Can be used in an emergency to close everything down and stop the pulse trains.

        :return: the command to send to the serial port

        Command:

        Byte1	Byte 2
        ---------------------------------------------------------------------------------------------------------------
        N	    *

        Command breakdown:

        Byte	    Setting	                Description
        ---------------------------------------------------------------------------------------------------------------
        Byte 1	    N	                    Sends a Reset to the PTHAT
        Byte 2	    *	                    End of Command

        The PTHAT will send back a reply when it receives this command.

        Reset Command Received      Reset Command Completed
        ---------------------------------------------------------------------------------------------------------------
        Nothing	                    Nothing
        """
        command = f"{self.__reset_pthat_command}{self._command_end}"
        if self.debug:
            print(f"PTHat reset command: {command}")
        if self.auto_send_command:
            self.send_command(command=command)

        self.wait_delay = 0
        self.command_type = "I"
        self.command_id = 0
        self._motor_enabled = False
        self._received_command_replies_enabled = False
        self._completed_command_replies_enabled = False
        return command

    def initiate_buffer(self):
        """
        With all the Instant commands you can also send as buffered commands, but you will need to use a couple of
        extra commands to initiate the buffer first using the H0000* command.

        Next you would need to decide how many commands you would like to store in the buffer (up to a maximum of 100
        commands) before sending a Buffer Start command Z0000*.

        With the release of Firmware V5.3 upwards you can now store 2000 commands in the buffer.

        Buffering commands allow you to queue up your commands, so they execute one after the other and reduce latency
        between commands being executed. Instant commands apart from the Stop command cannot be sent while sending
        Buffered commands. We recommend to buffer around 20 commands before sending a Buffer Start command and then to
        send a new command when you get the Complete Reply back, until all your commands have been sent.
        When all commands have been executed from the buffer you will get a **Buffer Empty** Reply come back and you
        will have to Initiate the buffer again to start.

        Initiate the buffer before sending any buffered commands.

        :return: the command to send to the serial port

        Command:

        Byte1	Byte 2-5	Byte 6
        ---------------------------------------------------------------------------------------------------------------
        H	    0000	    *

        Command breakdown:

        Byte	    Setting	                Description
        ---------------------------------------------------------------------------------------------------------------
        Byte 1	    H
        Byte 2-5	0000
        Byte 6	    *	                    End of Command

        The PTHAT will send back a reply when it receives this command.

        Initiate Buffer Command Received
        ---------------------------------------------------------------------------------------------------------------
        RBH000*
        """
        command = f"{self.__initiate_buffer_command}{self.__buffer_value:04}{self._command_end}"
        if self.debug:
            print(f"initiate_buffer command: {command}")
        if self.auto_send_command:
            self.send_command(command=command)
        return command

    def start_buffer(self):
        """
        Start executing buffered commands.

        :return: the command to send to the serial port

        Command:

        Byte1	Byte 2-5	Byte 6
        ---------------------------------------------------------------------------------------------------------------
        Z	    0000	    *

        Command breakdown:

        Byte	    Setting	                Description
        ---------------------------------------------------------------------------------------------------------------
        Byte 1	    Z
        Byte 2-5	0000
        Byte 6	    *	                    End of Command

    The PTHAT will send back a reply when it receives a command.

        Initiate Buffer Command Received
        ---------------------------------------------------------------------------------------------------------------
        RBZ000*
        """
        command = f"{self.__start_buffer_command}{self.__buffer_value:04}{self._command_end}"
        if self.debug:
            print(f"start_buffer command: {command}")
        if self.auto_send_command:
            self.send_command(command=command)
        return command

    def start_buffer_loop(self):
        """
        ***Available Firmware V5.3 upwards***
        Start executing buffered commands.
        With this command it will run through the buffered commands and when it gets to the last, it will go back to
        the first command and repeat all commands in a loop until a Stop command is sent.

        :return: the command to send to the serial port

        Command:

        Byte1	Byte 2-5	Byte 6
        ---------------------------------------------------------------------------------------------------------------
        W	    0000	    *

        Command breakdown:

        Byte	    Setting	                Description
        ---------------------------------------------------------------------------------------------------------------
        Byte 1	    W
        Byte 2-5	0000
        Byte 6	    *	                    End of Command

        The PTHAT will send back a reply when it receives a command.

        Initiate Buffer Command Received
        ---------------------------------------------------------------------------------------------------------------
        RBW000*
        """
        command = f"{self.__buffer_loop_start_command}{self.__buffer_value:04}{self._command_end}"
        if self.debug:
            print(f"start_buffer_loop command: {command}")
        if self.auto_send_command:
            self.send_command(command=command)
        return command

    def rpm_to_frequency(self, rpm, steps_per_rev, round_digits):
        """
        Convert RPM to frequency

        Formula for calculating stepping motor speed.
        Below is the RPM formula for stepping motor drives that use pulse signals to create motion.

        RPM = a/360 * fz * 60

        RPM = Revolutions per minute.
        “a” = step angle (degrees of rotation per step)
        “fz” = pulse frequency in hertz

        step angle = degrees of rotation (360) / steps per revolution

        Example 1:  Drive step resolution is set for 1000 steps per revolution.
        Find step angle: 360 (degrees of rotation) divided by 1000 (steps per revolution) =
                .36 (degrees of rotation per step)
        With input frequency of 1000hz, .36 / 360 * 1000 * 60 = 60 rpm

        Example 2: Drive step resolution is set for 500 steps per revolution.
        Find step angle: 360 (degrees of rotation) divided by 500 (steps per revolution) =
                .72 (degrees of rotation per step)
        With input frequency of 1000hz, .72 / 360 * 1000 * 60 = 120 rpm.

        :param round_digits number of digits to round to
        :param rpm  RPM to convert
        :param steps_per_rev    steps per revolution
        :return: frequency
        """
        step_angle = 360 / float(steps_per_rev)
        convert_step_angle = step_angle / 360 * 60
        if round_digits > 0:
            freq = round(rpm / convert_step_angle, round_digits)
        else:
            freq = round(rpm / convert_step_angle)

        # This is another calculation that gives the same result
        # convert_steps = float(steps_per_rev) * 0.0166666666666667
        # convert_rpm = float(rpm) * convert_steps
        # freq = round(convert_rpm / 0.004, 3) * 0.004

        if self.debug:
            print(f"rpm_to_frequency rpm: {rpm} = frequency: {freq}")
        return freq

    def frequency_to_rpm(self, frequency, steps_per_rev):
        """
        Convert frequency to RPM

        Formula for calculating stepping motor speed.
        Below is the frequency formula for stepping motor drives that use pulse signals to create motion.

        To find required frequency to meet desired speed we must find Fz:
        Fz = RPM / ( (a/360) * 60)

        “fz” = pulse frequency in hertz
        “a” = step angle (degrees of rotation per step)
        RPM = Revolutions per minute.

        step angle = degrees of rotation (360) / steps per revolution

        Step 1. Divide step angle by 360:  .36/360 = .001,  then multiply by 60 (seconds) .001 * 60 = .06
        Step 2. Divide desired speed by .06: Desired speed of 500 rpm’s.   Therefore ; 500 / .06 = 8333.33
            ( 8333.33 is the frequency in hertz required to reach 500 rpm’s for drive set at 1000 steps per revolution)

        :param frequency    the frequency
        :param steps_per_rev    steps per revolution
        :return: RPM
        """
        step_angle = 360 / float(steps_per_rev)
        rpm = round(step_angle / 360 * frequency * 60)
        if self.debug:
            print(f"frequency_to_rpm frequency: {frequency} = rpm: {rpm}")
        return rpm

    def calculate_pulse_count(self, steps_per_rev, total_revs):
        """
        Calculates the pulse count from the steps per revolution and the total revolutions desired.

        Calculation is

        pulse count = steps per rev * total revs

        :param steps_per_rev: steps per revolution
        :param total_revs: total revolutions desired
        :return: pulse count
        """
        pulse_cnt = steps_per_rev * total_revs
        if self.debug:
            print(f"pulse count: {pulse_cnt} = {steps_per_rev} steps per revolution * {total_revs} total revolutions")
        return pulse_cnt

    def calculate_revolutions(self, steps_per_rev, pulse_count):
        """
        Calculates the number of revolutions from the steps per revolution and the pulse count.

        Calculation is

        total revs = pulse count / steps per rev

        :param steps_per_rev: steps per revolution
        :param pulse_count: total pulse count
        :return: number of revolutions
        """
        total_revs = pulse_count / steps_per_rev
        if self.debug:
            print(f"total revolutions: {total_revs} = pulse count: {pulse_count} / {steps_per_rev} steps per revolution")
        return total_revs

    def _validate_command(self):
        """
        Validate command settings that are the same for every command
        :return: true if the command settings are valid, otherwise false
        """
        if not self.command_type == "I" and not self.command_type == "B":
            if self.debug:
                print(f"Invalid command type {self.command_type}")
            return False

        if not self._validate_values(self.command_id, 0, 99):
            if self.debug:
                print(f"Invalid command ID {self.command_id}")
            return False

        return True

    def _validate_values(self, value, start, end):
        """
        Check an value against start and end to make sure it is between them
        :param value: value to check
        :param start: start value
        :param end: end value
        :return: true if the value is between start and end, otherwise false
        """
        if value is not None and start <= value <= end:
            return True
        else:
            return False


class Axis(PTHat):
    """
    This is an Axis object that contains info about an axis. It inherits from PTHat so contains all functionality
    needed to communicate with the PTHat via the serial interface.
    """
    # Properties
    axis = "X"  # X, Y, Z or E or A (all)
    frequency = 0.0  # frequency of the pulse train - 000000.000 - 500000.000
    pulse_count = 0  # required pulse count - 0000000000 - 4294967295
    direction = 0  # direction - 0 = clockwise (cw - forward), 1 = counter clockwise (ccw - reverse)
    start_ramp = 0  # start ramp - 0 = No Ramp, 1 = Ramp
    finish_ramp = 0  # finish ramp - 0 = No Ramp, 1 = Ramp
    ramp_divide = 0  # Ramp divide. Divides target frequency by this value for each ramp increment. 0 - 255
    ramp_pause = 0  # Ramp pause between each ramp increment. 0 - 255
    link_to_adc = 0  # Link to ADC - 0 = No ADC, 1 = Link to ADC1, 2= Link to ADC2
    enable_line_polarity = 0  # Enable line polarity - 0 = Enable Line 0 Volts, 1 = Enable Line 5 Volts
    pulse_count_change_direction = 0  # Sets the Pulse count to change direction on the
    #                                   fly - 0000000000-4294967295
    pulse_counts_sent_back = 0  # Sets the Pulse count at which all Axis pulse counts will be sent
    #                             back - 0000000000-4294967295
    enable_disable_x_pulse_count_replies = 1  # 0=Disable X Axis Pulse Replies, 1=Enable X Axis Pulse Reply
    enable_disable_y_pulse_count_replies = 1  # 0=Disable Y Axis Pulse Replies, 1=Enable Y Axis Pulse Reply
    enable_disable_z_pulse_count_replies = 1  # 0=Disable Z Axis Pulse Replies, 1=Enable Z Axis Pulse Reply
    enable_disable_e_pulse_count_replies = 1  # 0=Disable E Axis Pulse Replies, 1=Enable E Axis Pulse Reply
    pause_all_return_x_pulse_count = 0   # Pause 0=Disable X Axis Pulse Count Replies, 1=Enable X Axis Pulse Count Reply
    pause_all_return_y_pulse_count = 0   # Pause 0=Disable Y Axis Pulse Count Replies, 1=Enable Y Axis Pulse Count Reply
    pause_all_return_z_pulse_count = 0   # Pause 0=Disable Z Axis Pulse Count Replies, 1=Enable Z Axis Pulse Count Reply
    pause_all_return_e_pulse_count = 0   # Pause 0=Disable E Axis Pulse Count Replies, 1=Enable E Axis Pulse Count Reply
    __paused = False
    __started = False

    # Axis commands
    __axis_config_command = "C"  # Set axis configuration command
    __auto_direction_change_command = "B"  # Set auto change direction command
    __auto_count_pulse_out_command = "J"  # Set auto count pulse out command
    __start_axis_command = "S"  # Start axis command
    __start_all_axis_command = "SA"  # Start all axis command
    __stop_axis_command = "T"  # Stop axis command
    __stop_all_axis_command = "TA"  # Stop all axis command
    __pause_resume_axis_command = "P"  # Pause/resume axis command
    __pause_resume_all_axis_command = "PA"  # Pause/resume all axis command
    __request_current_pulse_count_command = "P"  # Request current pulse count - command reversed with axis first (XP)
    __change_axis_speed_command = "Q"  # Change the axis speed on the fly command
    __enable_disable_limit_switches_command = "K"  # enable/disable limit switches command

    def __init__(self, axis, command_type="I", command_id=0, serial_device="/dev/ttyS0", baud_rate=115200,
                 test_mode=False):
        """
        Constructor

        :param command_type: type of command, I = instant, B = buffered - default I
        :param command_id: optional command ID, 0-99 - default 0
        :param serial_device: serial device - default /dev/ttyS0
        :param baud_rate: serial port baud rate - default 115200
        :param test_mode: if true then serial commands will not actually be sent - default False
        """
        super().__init__(command_type=command_type, command_id=command_id, serial_device=serial_device,
                         baud_rate=baud_rate, test_mode=test_mode)
        if str(axis).upper() == "X" or str(axis).upper() == "Y" or str(axis).upper() == "Z" or \
                str(axis).upper() == "E" or str(axis).upper() == "A":
            self.axis = str(axis).upper()
        else:
            self.axis = "X"     # Default to X if an invalid axis is passed

    def set_axis(self, frequency=None, pulse_count=None, direction=None, start_ramp=None,
                 finish_ramp=None, ramp_divide=None, ramp_pause=None, link_to_adc=None, enable_line_polarity=None):
        """
        This Command sets the properties of each Axis, but does not start the pulse train on that Axis.
        A Start Command must be used after to activate.

        :param frequency: frequency of the pulse train, 0.0-500000.0 - default 0.0 or self.frequency
        :param pulse_count: required pulse count, 0-4294967295 - default 0 or self.pulse_count
        :param direction: direction, 0 = forward (CW), 1 = reverse (CCW) - default 0 (forward - CW) or self.direction
        :param start_ramp: start ramp, no ramp = 0, ramp = 1 - default 0 or self.start_ramp
        :param finish_ramp: finish ramp, no ramp = 0, ramp = 1 - default 0 or self.finish_ramp
        :param ramp_divide: ramp divide, 0-255, will divide the target frequency by this value for each ramp
                    increment - default 0 or self.ramp_divide
        :param ramp_pause: ramp pause between each ramp increment, 0-255 - default 0 or self.ramp_pause
        :param link_to_adc: link to ADC, no ADC = 0, ADC1 = 1, ADC2 = 2 - default 0 or self.link_to_adc
        :param enable_line_polarity: enable line polarity, enable line 0 volts = 0, enable line 5 volts = 1 - default 0
                    or self.enable_line_polarity
        :return: the command to send to the serial port

        Command:

        Byte1	Byte 2-3	Byte 4-5	Byte 6-15	Byte 16-25	Byte 26	Byte 27	Byte 28	Byte 29-31	Byte 32-34	Byte 35	Byte 36	Byte 37
        --------------------------------------------------------------------------------------------------------------------------------
        I	    00	        CX	        125000.000	4294967295	1	    1	    1	    100	        010	        0	    1	    *

        Command breakdown:

        Byte	    Setting	                Description
        ---------------------------------------------------------------------------------------------------------------
        Byte 1	    I=Instant Command       Sets command to either Instant or Buffer.
                    B=Buffer Command
        Byte 2-3	0-99	                Optional Command ID
        Byte 4-5	CX = Set X-Axis         Sets which Axis is to be set
                    CY = Set Y-Axis
                    CZ = Set Z-Axis
                    CE = Set E-Axis
        Byte 6-15	000000.000-500000.000	Sets the frequency of the pulse train
        Byte 16-25	0000000000-4294967295	Sets the required pulse count.
        Byte 26	    0-1	                    Direction
                                            0=CW (forward)
                                            1=CCW (reverse)
        Byte 27	    0-1	                    Start Ramp
                                            0=No ramp
                                            1=Ramp
        Byte 28	    0-1	                    Finish Ramp
                                            0=No ramp
                                            1=Ramp
        Byte 29-31	0-255	                Ramp divide. This will divide the target frequency by this value for
                                            each ramp increment
        Byte 32-34	0-255	                Ramp pause between each ramp increment
        Byte 35	    0-2	                    Link to ADC
                                            0=No ADC
                                            1=Link to ADC1
                                            2=Link to ADC2
        Byte 36	    0-1	                    Enable Line Polarity
                                            0=Enable Line 0 Volts
                                            1=Enable Line 5 Volts
        Byte 37	    *	                    End of Command

        The PTHAT will send back a reply when it receives a command and also when it has completed a command.
        If the Command sent ID number was set for bytes 2-3, then this will be returned in the reply.
        These can be turned off if needed.

        X set       Y set       Z set       E set       X set       Y set       Z set       E set
        Received	Received	Received	Received	Completed	Completed	Completed	Completed
        --------------------------------------------------------------------------------------------------------------------------------
        RI00CX*	    RI00CY*	    RI00CZ*	    RI00CE*	    CI00CX*	    CI00CY*	    CI00CZ*	    CI00CE*
        """
        if not self._validate_command():
            return False

        if frequency is not None:
            self.frequency = frequency

        if pulse_count is not None:
            self.pulse_count = pulse_count

        if direction is not None:
            self.direction = direction

        if start_ramp is not None:
            self.start_ramp = start_ramp

        if finish_ramp is not None:
            self.finish_ramp = finish_ramp

        if ramp_divide is not None:
            self.ramp_divide = ramp_divide

        if ramp_pause is not None:
            self.ramp_pause = ramp_pause

        if link_to_adc is not None:
            self.link_to_adc = link_to_adc

        if enable_line_polarity is not None:
            self.enable_line_polarity = enable_line_polarity

        if not self._validate_values(self.frequency, 0.0, 500000.0):
            print(f"Invalid frequency {self.frequency}")
            return False

        if not self._validate_values(self.pulse_count, 0, 4294967295):
            print(f"Invalid pulse count {self.pulse_count}")
            return False

        if not self._validate_values(self.ramp_divide, 0, 255):
            print(f"Invalid ramp divide {self.ramp_divide}")
            return False

        if not self._validate_values(self.ramp_pause, 0, 255):
            print(f"Invalid ramp pause {self.ramp_pause}")
            return False

        if not self._validate_values(self.link_to_adc, 0, 2):
            print(f"Invalid link to ADC {self.link_to_adc}")
            return False

        if not self._validate_values(self.direction, 0, 1):
            print(f"Invalid direction: {self.direction}")
            return False

        if not self._validate_values(self.start_ramp, 0, 1):
            print(f"Invalid start ramp: {self.start_ramp}")
            return False

        if not self._validate_values(self.finish_ramp, 0, 1):
            print(f"Invalid finish ramp: {self.finish_ramp}")
            return False

        if not self._validate_values(self.enable_line_polarity, 0, 1):
            print(f"Invalid enable line polarity {self.enable_line_polarity}")
            return False

        command = f"{self.command_type}{self.command_id:02}{self.__axis_config_command}{self.axis}" \
                  f"{self.frequency:010.3f}{self.pulse_count:010}{self.direction}{self.start_ramp}{self.finish_ramp}" \
                  f"{self.ramp_divide:03}{self.ramp_pause:03}{self.link_to_adc}{self.enable_line_polarity}" \
                  f"{self._command_end}"
        if self.debug:
            print(f"set_axis command: {command}")
        if self.auto_send_command:
            self.send_command(command=command)
        return command

    def set_direction_forward(self):
        """
        Sets the direction to forward

        :return: the command to send to the serial port
        """
        if self.debug:
            print(f"set_direction_forward command")
        return self.set_axis(direction=0)

    def set_direction_reverse(self):
        """
        Sets the direction to reverse

        :return: the command to send to the serial port
        """
        if self.debug:
            print(f"set_direction_reverse command")
        return self.set_axis(direction=1)

    def enable_start_ramp(self):
        """
        Enables the start ramp

        :return: the command to send to the serial port
        """
        if self.debug:
            print(f"enable_start_ramp command")
        return self.set_axis(start_ramp=1)

    def disable_start_ramp(self):
        """
        Disables the start ramp

        :return: the command to send to the serial port
        """
        if self.debug:
            print(f"disable_start_ramp command")
        return self.set_axis(start_ramp=0)

    def enable_finish_ramp(self):
        """
        Enables the finish ramp

        :return: the command to send to the serial port
        """
        if self.debug:
            print(f"enable_finish_ramp command")
        return self.set_axis(finish_ramp=1)

    def disable_finish_ramp(self):
        """
        Disables the finish ramp

        :return: the command to send to the serial port
        """
        if self.debug:
            print(f"disable_finish_ramp command")
        return self.set_axis(finish_ramp=0)

    def enable_line_polarity_0_volts(self):
        """
        Enable the line polarity at 0 volts

        :return: the command to send to the serial port
        """
        if self.debug:
            print(f"enable_line_polarity_0_volts command")
        return self.set_axis(enable_line_polarity=0)

    def enable_line_polarity_5_volts(self):
        """
        Enable the line polarity at 5 volts

        :return: the command to send to the serial port
        """
        if self.debug:
            print(f"enable_line_polarity_5_volts command")
        return self.set_axis(enable_line_polarity=1)

    def set_auto_direction_change(self, pulse_count=None):
        """
        This Command sets the Auto Direction Change of each Axis, but does not start the pulse train on that Axis.
        A Start Command must be used after to activate.

        :param pulse_count: pulse count to change direction on the fly, 0-4294967295 - default 0 or self.pulse_count
        :return: the command to send to the serial port

        Command:

        Byte1	Byte 2-3	Byte 4-5	Byte 6-15	    Byte 16
        --------------------------------------------------------------------------------------------------------------------------------
        I	    00	        BX	        0000000100	    *

        Command breakdown:

        Byte	    Setting	                Description
        ---------------------------------------------------------------------------------------------------------------
        Byte 1	    I=Instant Command       Sets command to either Instant or Buffer.
                    B=Buffer Command
        Byte 2-3	0-99	                Optional Command ID
        Byte 4-5	BX = Set X-Axis         Sets which Axis is to be set to auto change direction
                    BY = Set Y-Axis
                    BZ = Set Z-Axis
                    BE = Set E-Axis
        Byte 6-15	0000000000-4294967295	Sets the Pulse count to change direction on the fly
        Byte 16	    *	                    End of Command

        The PTHAT will send back a reply when it receives a command and also when it has completed a command.
        If the Command sent ID number was set for bytes 2-3, then this will be returned in the reply.
        These can be turned off if needed.

        X set       Y set       Z set       E set       X set       Y set       Z set       E set
        Received	Received	Received	Received	Completed	Completed	Completed	Completed
        ---------------------------------------------------------------------------------------------------------------
        RI00BX*	    RI00BY*	    RI00BZ*	    RI00BE*	    CI00BX*	    CI00BY*	    CI00BZ*	    CI00BE*
        """
        if not self._validate_command():
            return False

        if pulse_count is not None:
            self.pulse_count_change_direction = pulse_count

        if not self._validate_values(self.pulse_count_change_direction, 0000000000, 4294967295):
            print(f"Invalid pulse count to change direction on {self.pulse_count_change_direction}")
            return False

        command = f"{self.command_type}{self.command_id:02}{self.__auto_direction_change_command}{self.axis}" \
                  f"{self.pulse_count_change_direction:010}{self._command_end}"
        if self.debug:
            print(f"set_auto_direction_change command: {command}")
        if self.auto_send_command:
            self.send_command(command=command)
        return command

    def set_auto_count_pulse_out(self, pulse_count=None, xreplies=None, yreplies=None, zreplies=None, ereplies=None):
        """
        This Command sets which Axis and at what pulse count it should send back the current pulse count of each axis.
        It also sends back direction of travel.
        You can also choose what pulse replies are sent back X, Y, Z or E.
        A Start Command must be used after to activate.

        Be aware that this command can cause a lot of data being sent back over the serial port and if you try to
        send other commands while it is sending data back, there could be a clash.

        :param pulse_count: pulse count at which all Axis pulse counts will be sent back, 0-4294967295 - default 0 or
                            self.pulse_count
        :param xreplies: enable/disable X axis pulse count replies, disable = 0, enable = 1 - default 1 or
                         self.enable_disable_x_pulse_count_replies
        :param yreplies: enable/disable Y axis pulse count replies, disable = 0, enable = 1 - default 1 or
                         self.enable_disable_y_pulse_count_replies
        :param zreplies: enable/disable Z axis pulse count replies, disable = 0, enable = 1 - default 1 or
                         self.enable_disable_z_pulse_count_replies
        :param ereplies: enable/disable E axis pulse count replies, disable = 0, enable = 1 - default 1 or
                         self.enable_disable_e_pulse_count_replies
        :return: the command to send to the serial port

        Command:

        Byte1	Byte 2-3	Byte 4-5	Byte 6-15	Byte 16	    Byte 17	    Byte 18	    Byte 19	    Byte 20
        ---------------------------------------------------------------------------------------------------------------
        I	    00	        JX	        0000000100	1	        1	        1	        1	        *

        Command breakdown:

        Byte	    Setting	                Description
        ---------------------------------------------------------------------------------------------------------------
        Byte 1	    I=Instant Command       Sets command to either Instant or Buffer.
                    B=Buffer Command
        Byte 2-3	0-99	                Optional Command ID
        Byte 4-5	JX = Set X-Axis         Sets which Axis is to be set to auto send pulse counts on
                    JY = Set Y-Axis
                    JZ = Set Z-Axis
                    JE = Set E-Axis
        Byte 6-15	0000000000-4294967295	Sets the Pulse count at which all Axis pulse counts will be sent back
        Byte 16	    0-1                     0 = Disable X Axis Pulse Replies
                                            1 = Enable X Axis Pulse Reply
        Byte 17	    0-1                     0 = Disable Y Axis Pulse Replies
                                            1 = Enable Y Axis Pulse Reply
        Byte 18	    0-1                     0 = Disable Z Axis Pulse Replies
                                            1 = Enable Z Axis Pulse Reply
        Byte 19	    0-1                     0 = Disable E Axis Pulse Replies
                                            1 = Enable E Axis Pulse Reply
        Byte 20	    *	                    End of Command

        The PTHAT will send back a reply when it receives a command and also when it has completed a command.
        The Pulse Count and direction that the motor is travelling will be sent back when pulse target is hit.
        If the Command sent ID number was set for bytes 2-3, then this will be returned in the reply.
        These can be turned off if needed.

        X set           Y set           Z set           E set       X set       Y set       Z set       E set
        Received	    Received	    Received	    Received	Completed	Completed	Completed	Completed
        ---------------------------------------------------------------------------------------------------------------
        RI00JX*	        RI00JY*	        RI00JZ*	        RI00JE*	    CI00JX*	    CI00JY*	    CI00JZ*	    CI00JE*

        DI00JX*         DI00JY*         DI00JZ*         DI00JE*
        XP(D)XResult*   XP(D)XResult*   XP(D)XResult*   XP(D)XResult*
        YP(D)YResult*   YP(D)YResult*   YP(D)YResult*   YP(D)YResult*
        ZP(D)ZResult*   ZP(D)ZResult*   ZP(D)ZResult*   ZP(D)ZResult*
        EP(D)EResult*   EP(D)EResult*   EP(D)EResult*   EP(D)EResult*

        (D)=Direction   (D)=Direction   (D)=Direction   (D)=Direction
        of motor        of motor        of motor        of motor
        travel	        travel          travel          travel

        Result=         Result=         Result=         Result=
        0000000000-     0000000000-     0000000000-     0000000000-
        4294967295	    4294967295	    4294967295	    4294967295
        """
        if not self._validate_command():
            return False

        if pulse_count is not None:
            self.pulse_counts_sent_back = pulse_count

        if xreplies is not None:
            self.enable_disable_x_pulse_count_replies = xreplies

        if yreplies is not None:
            self.enable_disable_y_pulse_count_replies = yreplies

        if zreplies is not None:
            self.enable_disable_z_pulse_count_replies = zreplies

        if ereplies is not None:
            self.enable_disable_e_pulse_count_replies = ereplies

        if not self._validate_values(self.pulse_counts_sent_back, 0000000000, 4294967295):
            print(f"Invalid pulse count to send back on {self.pulse_counts_sent_back}")
            return False

        if not self._validate_values(self.enable_disable_x_pulse_count_replies, 0, 1):
            print(f"Invalid enable disable X pulse count replies {self.enable_disable_x_pulse_count_replies}")
            return False

        if not self._validate_values(self.enable_disable_y_pulse_count_replies, 0, 1):
            print(f"Invalid enable disable Y pulse count replies {self.enable_disable_y_pulse_count_replies}")
            return False

        if not self._validate_values(self.enable_disable_z_pulse_count_replies, 0, 1):
            print(f"Invalid enable disable Z pulse count replies {self.enable_disable_z_pulse_count_replies}")
            return False

        if not self._validate_values(self.enable_disable_e_pulse_count_replies, 0, 1):
            print(f"Invalid enable disable E pulse count replies {self.enable_disable_e_pulse_count_replies}")
            return False

        command = f"{self.command_type}{self.command_id:02}{self.__auto_count_pulse_out_command}{self.axis}" \
                  f"{self.pulse_counts_sent_back:010}{self.enable_disable_x_pulse_count_replies}" \
                  f"{self.enable_disable_y_pulse_count_replies}{self.enable_disable_z_pulse_count_replies}" \
                  f"{self.enable_disable_e_pulse_count_replies}{self._command_end}"
        if self.debug:
            print(f"set_auto_count_pulse_out command: {command}")
        if self.auto_send_command:
            self.send_command(command=command)
        return command

    def start(self):
        """
        Start one of the pulse trains running.

        :return: the command to send to the serial port

        Command:

        Byte1	Byte 2-3	Byte 4-5	Byte 6
        ---------------------------------------------------------------------------------------------------------------
        I	    00	        SX	        *

        Command breakdown:

        Byte	    Setting	                Description
        ---------------------------------------------------------------------------------------------------------------
        Byte 1	    I=Instant Command       Sets command to either Instant or Buffer.
                    B=Buffer Command
        Byte 2-3	0-99	                Optional Command ID
        Byte 4-5	SX = Start X-Axis       Sets which Axis is to be started
                    SY = Start Y-Axis
                    SZ = Start Z-Axis
                    SE = Start E-Axis
                    SA = Start All
        Byte 6	    *	                    End of Command

        The PTHAT will send back a reply when it receives a command and also when it has completed a command.
        In this case the completed command will be sent back when the Axis that has been started completes the Pulse
        Count. If the Command sent ID number was set for bytes 2-3, then this will be returned in the reply.

        X Start     Y Start     Z Start     E Start     All Start   X Pulse     Y Pulse     Z Pulse     E Pulse
        Received	Received	Received	Received	Received	Count       Count       Count       Count
                                                                    Complete	Complete	Complete	Complete
        ---------------------------------------------------------------------------------------------------------------
        RI00SX*	    RI00SY*	    RI00SZ*	    RI00SE*	    RI00SA*	    CI00SX*	    CI00SY*	    CI00SZ*	    CI00SE*
        """
        command = f"{self.command_type}{self.command_id:02}{self.__start_axis_command}{self.axis}" \
                  f"{self._command_end}"
        self.__start(command=command)
        return command

    def start_all(self):
        """
        Start all of the pulse trains running.

        :return: the command to send to the serial port

        Command:

        Byte1	Byte 2-3	Byte 4-5	Byte 6
        ---------------------------------------------------------------------------------------------------------------
        I	    00	        SA	        *

        Command breakdown:

        Byte	    Setting	                Description
        ---------------------------------------------------------------------------------------------------------------
        Byte 1	    I=Instant Command       Sets command to either Instant or Buffer.
                    B=Buffer Command
        Byte 2-3	0-99	                Optional Command ID
        Byte 4-5	SX = Start X-Axis       Sets which Axis is to be started
                    SY = Start Y-Axis
                    SZ = Start Z-Axis
                    SE = Start E-Axis
                    SA = Start All
        Byte 6	    *	                    End of Command

        The PTHAT will send back a reply when it receives a command and also when it has completed a command.
        In this case the completed command will be sent back when the Axis that has been started completes the Pulse
        Count. If the Command sent ID number was set for bytes 2-3, then this will be returned in the reply.

        X Start     Y Start     Z Start     E Start     All Start   X Pulse     Y Pulse     Z Pulse     E Pulse
        Received	Received	Received	Received	Received	Count       Count       Count       Count
                                                                    Complete	Complete	Complete	Complete
        ---------------------------------------------------------------------------------------------------------------
        RI00SX*	    RI00SY*	    RI00SZ*	    RI00SE*	    RI00SA*	    CI00SX*	    CI00SY*	    CI00SZ*	    CI00SE*
        """
        command = f"{self.command_type}{self.command_id:02}{self.__start_all_axis_command}" \
                  f"{self._command_end}"
        self.__start(command=command)
        return command

    def __start(self, command):
        """
        Start one of the pulse trains running or start all.

        :param command: command to run to start
        :return: the command to send to the serial port

        Command:

        Byte1	Byte 2-3	Byte 4-5	Byte 6
        ---------------------------------------------------------------------------------------------------------------
        I	    00	        SX	        *

        Command breakdown:

        Byte	    Setting	                Description
        ---------------------------------------------------------------------------------------------------------------
        Byte 1	    I=Instant Command       Sets command to either Instant or Buffer.
                    B=Buffer Command
        Byte 2-3	0-99	                Optional Command ID
        Byte 4-5	SX = Start X-Axis       Sets which Axis is to be started
                    SY = Start Y-Axis
                    SZ = Start Z-Axis
                    SE = Start E-Axis
                    SA = Start All
        Byte 6	    *	                    End of Command

        The PTHAT will send back a reply when it receives a command and also when it has completed a command.
        In this case the completed command will be sent back when the Axis that has been started completes the Pulse
        Count. If the Command sent ID number was set for bytes 2-3, then this will be returned in the reply.

        X Start     Y Start     Z Start     E Start     All Start   X Pulse     Y Pulse     Z Pulse     E Pulse
        Received	Received	Received	Received	Received	Count       Count       Count       Count
                                                                    Complete	Complete	Complete	Complete
        ---------------------------------------------------------------------------------------------------------------
        RI00SX*	    RI00SY*	    RI00SZ*	    RI00SE*	    RI00SA*	    CI00SX*	    CI00SY*	    CI00SZ*	    CI00SE*
        """
        if not self._validate_command():
            return False

        if not self.__started:
            if self.debug:
                print(f"Axis start command: {command}")
            if self.auto_send_command:
                self.send_command(command=command)

            self.__started = True

    def stop(self):
        """
        Stop one of the pulse trains from running. This is a controlled stop, in that the Axis will ramp down
        and not just stop to protect the motors. If you want to use a sudden stop then we recommend a external
        Emergency Stop button that cuts the power or send a Reset command.

        :return: the command to send to the serial port

        Command:

        Byte1	Byte 2-3	Byte 4-5	Byte 6
        ---------------------------------------------------------------------------------------------------------------
        I	    00	        TX	        *

        Command breakdown:

        Byte	    Setting	                Description
        ---------------------------------------------------------------------------------------------------------------
        Byte 1	    I=Instant Command       Sets command to either Instant or Buffer.
                    B=Buffer Command
        Byte 2-3	0-99	                Optional Command ID
        Byte 4-5	TX = Stop X-Axis        Sets which Axis is to be stopped
                    TY = Stop Y-Axis
                    TZ = Stop Z-Axis
                    TE = Stop E-Axis
                    TA = Stop All
        Byte 6	    *	                    End of Command

        The PTHAT will send back a reply when it receives a command and also when it has completed a command.
        In this case the completed command will be sent back when the Axis that has came to a stop.
        If the Command sent ID number was set for bytes 2-3, then this will be returned in the Received reply, but the
        completed command ID will be from the original ID used in the Start command.

        X Stop      Y Stop      Z Stop      E Stop      Stop All    X Pulse     Y Pulse     Z Pulse     E Pulse
        Received    Received    Received    Received    Received	Stopped	    Stopped	    Stopped	    Stopped
        ---------------------------------------------------------------------------------------------------------------
        RI00TX*	    RI00TY*	    RI00TZ*	    RI00TE*	    RI00TA*	    CI00SX*	    CI00SY*	    CI00SZ*	    CI00SE*
        """
        command = f"{self.command_type}{self.command_id:02}{self.__stop_axis_command}{self.axis}{self._command_end}"
        self.__stop(command=command)
        return command

    def stop_all(self):
        """
        Stop all of the pulse trains from running. This is a controlled stop, in that the Axis will ramp down
        and not just stop to protect the motors. If you want to use a sudden stop then we recommend a external
        Emergency Stop button that cuts the power or send a Reset command.

        :return: the command to send to the serial port

        Command:

        Byte1	Byte 2-3	Byte 4-5	Byte 6
        ---------------------------------------------------------------------------------------------------------------
        I	    00	        TA	        *

        Command breakdown:

        Byte	    Setting	                Description
        ---------------------------------------------------------------------------------------------------------------
        Byte 1	    I=Instant Command       Sets command to either Instant or Buffer.
                    B=Buffer Command
        Byte 2-3	0-99	                Optional Command ID
        Byte 4-5	TX = Stop X-Axis        Sets which Axis is to be stopped
                    TY = Stop Y-Axis
                    TZ = Stop Z-Axis
                    TE = Stop E-Axis
                    TA = Stop All
        Byte 6	    *	                    End of Command

        The PTHAT will send back a reply when it receives a command and also when it has completed a command.
        In this case the completed command will be sent back when the Axis that has came to a stop.
        If the Command sent ID number was set for bytes 2-3, then this will be returned in the Received reply, but the
        completed command ID will be from the original ID used in the Start command.

        X Stop      Y Stop      Z Stop      E Stop      Stop All    X Pulse     Y Pulse     Z Pulse     E Pulse
        Received    Received    Received    Received    Received	Stopped	    Stopped	    Stopped	    Stopped
        ---------------------------------------------------------------------------------------------------------------
        RI00TX*	    RI00TY*	    RI00TZ*	    RI00TE*	    RI00TA*	    CI00SX*	    CI00SY*	    CI00SZ*	    CI00SE*
        """
        command = f"{self.command_type}{self.command_id:02}{self.__stop_all_axis_command}" \
                  f"{self._command_end}"
        self.__stop(command=command)
        return command

    def __stop(self, command):
        """
        Stop one or all of the pulse trains from running. This is a controlled stop, in that the Axis will ramp down
        and not just stop to protect the motors. If you want to use a sudden stop then we recommend a external
        Emergency Stop button that cuts the power or send a Reset command.

        :param command stop command
        :return: the command to send to the serial port

        Command:

        Byte1	Byte 2-3	Byte 4-5	Byte 6
        ---------------------------------------------------------------------------------------------------------------
        I	    00	        TX	        *

        Command breakdown:

        Byte	    Setting	                Description
        ---------------------------------------------------------------------------------------------------------------
        Byte 1	    I=Instant Command       Sets command to either Instant or Buffer.
                    B=Buffer Command
        Byte 2-3	0-99	                Optional Command ID
        Byte 4-5	TX = Stop X-Axis        Sets which Axis is to be stopped
                    TY = Stop Y-Axis
                    TZ = Stop Z-Axis
                    TE = Stop E-Axis
                    TA = Stop All
        Byte 6	    *	                    End of Command

        The PTHAT will send back a reply when it receives a command and also when it has completed a command.
        In this case the completed command will be sent back when the Axis that has came to a stop.
        If the Command sent ID number was set for bytes 2-3, then this will be returned in the Received reply, but the
        completed command ID will be from the original ID used in the Start command.

        X Stop      Y Stop      Z Stop      E Stop      Stop All    X Pulse     Y Pulse     Z Pulse     E Pulse
        Received    Received    Received    Received    Received	Stopped	    Stopped	    Stopped	    Stopped
        ---------------------------------------------------------------------------------------------------------------
        RI00TX*	    RI00TY*	    RI00TZ*	    RI00TE*	    RI00TA*	    CI00SX*	    CI00SY*	    CI00SZ*	    CI00SE*
        """
        if not self._validate_command():
            return False

        if self.__started:
            if self.debug:
                print(f"Axis stop command: {command}")
            if self.auto_send_command:
                self.send_command(command=command)

            self.__started = False

    def pause(self, return_x_pulse_cnt=None, return_y_pulse_cnt=None, return_z_pulse_cnt=None, return_e_pulse_cnt=None):
        """
        Pauses one of the pulse trains from running.
        Bytes 6-9 choose to send Pulse count back after pause for each Axis.

        :param return_x_pulse_cnt: X axis pulse count replies, disable = 0, enable = 1 - default 0 or
                                   self.pause_all_return_x_pulse_count
        :param return_y_pulse_cnt: Y axis pulse count replies, disable = 0, enable = 1 - default 0 or
                                   self.pause_all_return_y_pulse_count
        :param return_z_pulse_cnt: Z axis pulse count replies, disable = 0, enable = 1 - default 0 or
                                   self.pause_all_return_z_pulse_count
        :param return_e_pulse_cnt: E axis pulse count replies, disable = 0, enable = 1 - default 0 or
                                   self.pause_all_return_e_pulse_count
        :return: the command to send to the serial port

        Command:

        Byte1	Byte 2-3	Byte 4-5	Byte 6	Byte 7	Byte 8	Byte 9	Byte 10
        ---------------------------------------------------------------------------------------------------------------
        I	    00	        PX	        1	    0	    0	    0	    *

        Command breakdown:

        Byte	    Setting	                Description
        ---------------------------------------------------------------------------------------------------------------
        Byte 1	    I=Instant Command       Sets command to either Instant or Buffer.
                    B=Buffer Command
        Byte 2-3	0-99	                Optional Command ID
        Byte 4-5	PX = Pause X-Axis       Sets which Axis is to be Paused
                    PY = Pause Y-Axis
                    PZ = Pause Z-Axis
                    PE = Pause E-Axis
                    PA = Pause All
        Byte 6	    0-1	                    Sends back pulse count from Axis if set to 1 with:
                                            PA = X-Axis
                                            PX = X-Axis
                                            PY = Y-Axis
                                            PZ = Z-Axis
                                            PE = E-Axis
        Byte 7	    0-1	                    Sends back pulse count from Axis if set to 1 with:
                                            PA = Y-Axis
                                            Set to 0 for PX, PY, PZ, PE
        Byte 8	    0-1 	                Sends back pulse count from Axis if set to 1 with:
                                            PA = Z-Axis
                                            Set to 0 for PX, PY, PZ, PE
        Byte 9	    0-1	                    Sends back pulse count from Axis if set to 1 with:
                                            PA = E-Axis
                                            Set to 0 for PX, PY, PZ, PE
        Byte 10	    *	                    End of Command

        The PTHAT will send back a reply when it receives a command and also when it has completed a command.
        If Pulse Count is selected then it will also send back the pulse count of chosen Axis.
        In this case the completed command will be sent back when the Axis is resumed, after a Pause.
        If the Command sent ID number was set for bytes 2-3, then this will be returned in the reply.

        X Pause         Y Pause         Z Pause         E Pause         Pause All
        Received        Received        Received        Received        Received
        ---------------------------------------------------------------------------------------------------------------
        RI00PX*	        RI00PY*	        RI00PZ*	        RI00PE*	        RI00PA*

        DI00PX*         DI00PY*         DI00PZ*         DI00PE*         DI00PX to E*
        XP(D)XResult*   XP(D)XResult*   XP(D)XResult*   XP(D)XResult*   XP(D)XResult*
        YP(D)YResult*   YP(D)YResult*   YP(D)YResult*   YP(D)YResult*   YP(D)YResult*
        ZP(D)ZResult*   ZP(D)ZResult*   ZP(D)ZResult*   ZP(D)ZResult*   ZP(D)ZResult*
        EP(D)EResult*   EP(D)EResult*   EP(D)EResult*   EP(D)EResult*   EP(D)EResult*

        (D)=Direction   (D)=Direction   (D)=Direction   (D)=Direction   (D)=Direction
        of motor        of motor        of motor        of motor        of motor
        travel          travel          travel          travel          travel

        Result=         Result=         Result=         Result=         Result=
        0000000000-     0000000000-     0000000000-     0000000000-     0000000000-
        4294967295      4294967295      4294967295      4294967295      4294967295
        """
        command = f"{self.command_type}{self.command_id:02}{self.__pause_resume_axis_command}{self.axis}" \
                  f"{self.pause_all_return_x_pulse_count}{self.pause_all_return_y_pulse_count}" \
                  f"{self.pause_all_return_z_pulse_count}{self.pause_all_return_e_pulse_count}{self._command_end}"
        self.__pause(command=command, return_x_pulse_cnt=return_x_pulse_cnt, return_y_pulse_cnt=return_y_pulse_cnt,
                     return_z_pulse_cnt=return_z_pulse_cnt, return_e_pulse_cnt=return_e_pulse_cnt)
        return command

    def pause_all(self, return_x_pulse_cnt=None, return_y_pulse_cnt=None, return_z_pulse_cnt=None,
                  return_e_pulse_cnt=None):
        """
        Pauses all of the pulse trains from running.
        Bytes 6-9 choose to send Pulse count back after pause for each Axis.

        :param return_x_pulse_cnt: X axis pulse count replies, disable = 0, enable = 1 - default 0 or
                                   self.pause_all_return_x_pulse_count
        :param return_y_pulse_cnt: Y axis pulse count replies, disable = 0, enable = 1 - default 0 or
                                   self.pause_all_return_y_pulse_count
        :param return_z_pulse_cnt: Z axis pulse count replies, disable = 0, enable = 1 - default 0 or
                                   self.pause_all_return_z_pulse_count
        :param return_e_pulse_cnt: E axis pulse count replies, disable = 0, enable = 1 - default 0 or
                                   self.pause_all_return_e_pulse_count
        :return: the command to send to the serial port

        Command:

        Byte1	Byte 2-3	Byte 4-5	Byte 6	Byte 7	Byte 8	Byte 9	Byte 10
        ---------------------------------------------------------------------------------------------------------------
        I	    00	        PA	        1	    0	    0	    0	    *

        Command breakdown:

        Byte	    Setting	                Description
        ---------------------------------------------------------------------------------------------------------------
        Byte 1	    I=Instant Command       Sets command to either Instant or Buffer.
                    B=Buffer Command
        Byte 2-3	0-99	                Optional Command ID
        Byte 4-5	PX = Pause X-Axis       Sets which Axis is to be Paused
                    PY = Pause Y-Axis
                    PZ = Pause Z-Axis
                    PE = Pause E-Axis
                    PA = Pause All
        Byte 6	    0-1	                    Sends back pulse count from Axis if set to 1 with:
                                            PA = X-Axis
                                            PX = X-Axis
                                            PY = Y-Axis
                                            PZ = Z-Axis
                                            PE = E-Axis
        Byte 7	    0-1	                    Sends back pulse count from Axis if set to 1 with:
                                            PA = Y-Axis
                                            Set to 0 for PX, PY, PZ, PE
        Byte 8	    0-1 	                Sends back pulse count from Axis if set to 1 with:
                                            PA = Z-Axis
                                            Set to 0 for PX, PY, PZ, PE
        Byte 9	    0-1	                    Sends back pulse count from Axis if set to 1 with:
                                            PA = E-Axis
                                            Set to 0 for PX, PY, PZ, PE
        Byte 10	    *	                    End of Command

        The PTHAT will send back a reply when it receives a command and also when it has completed a command.
        If Pulse Count is selected then it will also send back the pulse count of chosen Axis.
        In this case the completed command will be sent back when the Axis is resumed, after a Pause.
        If the Command sent ID number was set for bytes 2-3, then this will be returned in the reply.

        X Pause         Y Pause         Z Pause         E Pause         Pause All
        Received        Received        Received        Received        Received
        ---------------------------------------------------------------------------------------------------------------
        RI00PX*	        RI00PY*	        RI00PZ*	        RI00PE*	        RI00PA*

        DI00PX*         DI00PY*         DI00PZ*         DI00PE*         DI00PX to E*
        XP(D)XResult*   XP(D)XResult*   XP(D)XResult*   XP(D)XResult*   XP(D)XResult*
        YP(D)YResult*   YP(D)YResult*   YP(D)YResult*   YP(D)YResult*   YP(D)YResult*
        ZP(D)ZResult*   ZP(D)ZResult*   ZP(D)ZResult*   ZP(D)ZResult*   ZP(D)ZResult*
        EP(D)EResult*   EP(D)EResult*   EP(D)EResult*   EP(D)EResult*   EP(D)EResult*

        (D)=Direction   (D)=Direction   (D)=Direction   (D)=Direction   (D)=Direction
        of motor        of motor        of motor        of motor        of motor
        travel          travel          travel          travel          travel

        Result=         Result=         Result=         Result=         Result=
        0000000000-     0000000000-     0000000000-     0000000000-     0000000000-
        4294967295      4294967295      4294967295      4294967295      4294967295
        """
        command = f"{self.command_type}{self.command_id:02}{self.__pause_resume_all_axis_command}" \
                  f"{self.pause_all_return_x_pulse_count}{self.pause_all_return_y_pulse_count}" \
                  f"{self.pause_all_return_z_pulse_count}{self.pause_all_return_e_pulse_count}{self._command_end}"
        self.__pause(command=command, return_x_pulse_cnt=return_x_pulse_cnt, return_y_pulse_cnt=return_y_pulse_cnt,
                     return_z_pulse_cnt=return_z_pulse_cnt, return_e_pulse_cnt=return_e_pulse_cnt)
        return command

    def __pause(self, command, return_x_pulse_cnt=None, return_y_pulse_cnt=None, return_z_pulse_cnt=None,
                return_e_pulse_cnt=None):
        """
        Pauses one or all of the pulse trains from running.
        Bytes 6-9 choose to send Pulse count back after pause for each Axis.

        :param return_x_pulse_cnt: X axis pulse count replies, disable = 0, enable = 1 - default 0 or
                                   self.pause_all_return_x_pulse_count
        :param return_y_pulse_cnt: Y axis pulse count replies, disable = 0, enable = 1 - default 0 or
                                   self.pause_all_return_y_pulse_count
        :param return_z_pulse_cnt: Z axis pulse count replies, disable = 0, enable = 1 - default 0 or
                                   self.pause_all_return_z_pulse_count
        :param return_e_pulse_cnt: E axis pulse count replies, disable = 0, enable = 1 - default 0 or
                                   self.pause_all_return_e_pulse_count
        :return: the command to send to the serial port

        Command:

        Byte1	Byte 2-3	Byte 4-5	Byte 6	Byte 7	Byte 8	Byte 9	Byte 10
        ---------------------------------------------------------------------------------------------------------------
        I	    00	        PX	        1	    0	    0	    0	    *

        Command breakdown:

        Byte	    Setting	                Description
        ---------------------------------------------------------------------------------------------------------------
        Byte 1	    I=Instant Command       Sets command to either Instant or Buffer.
                    B=Buffer Command
        Byte 2-3	0-99	                Optional Command ID
        Byte 4-5	PX = Pause X-Axis       Sets which Axis is to be Paused
                    PY = Pause Y-Axis
                    PZ = Pause Z-Axis
                    PE = Pause E-Axis
                    PA = Pause All
        Byte 6	    0-1	                    Sends back pulse count from Axis if set to 1 with:
                                            PA = X-Axis
                                            PX = X-Axis
                                            PY = Y-Axis
                                            PZ = Z-Axis
                                            PE = E-Axis
        Byte 7	    0-1	                    Sends back pulse count from Axis if set to 1 with:
                                            PA = Y-Axis
                                            Set to 0 for PX, PY, PZ, PE
        Byte 8	    0-1 	                Sends back pulse count from Axis if set to 1 with:
                                            PA = Z-Axis
                                            Set to 0 for PX, PY, PZ, PE
        Byte 9	    0-1	                    Sends back pulse count from Axis if set to 1 with:
                                            PA = E-Axis
                                            Set to 0 for PX, PY, PZ, PE
        Byte 10	    *	                    End of Command

        The PTHAT will send back a reply when it receives a command and also when it has completed a command.
        If Pulse Count is selected then it will also send back the pulse count of chosen Axis.
        In this case the completed command will be sent back when the Axis is resumed, after a Pause.
        If the Command sent ID number was set for bytes 2-3, then this will be returned in the reply.

        X Pause         Y Pause         Z Pause         E Pause         Pause All
        Received        Received        Received        Received        Received
        ---------------------------------------------------------------------------------------------------------------
        RI00PX*	        RI00PY*	        RI00PZ*	        RI00PE*	        RI00PA*

        DI00PX*         DI00PY*         DI00PZ*         DI00PE*         DI00PX to E*
        XP(D)XResult*   XP(D)XResult*   XP(D)XResult*   XP(D)XResult*   XP(D)XResult*
        YP(D)YResult*   YP(D)YResult*   YP(D)YResult*   YP(D)YResult*   YP(D)YResult*
        ZP(D)ZResult*   ZP(D)ZResult*   ZP(D)ZResult*   ZP(D)ZResult*   ZP(D)ZResult*
        EP(D)EResult*   EP(D)EResult*   EP(D)EResult*   EP(D)EResult*   EP(D)EResult*

        (D)=Direction   (D)=Direction   (D)=Direction   (D)=Direction   (D)=Direction
        of motor        of motor        of motor        of motor        of motor
        travel          travel          travel          travel          travel

        Result=         Result=         Result=         Result=         Result=
        0000000000-     0000000000-     0000000000-     0000000000-     0000000000-
        4294967295      4294967295      4294967295      4294967295      4294967295
        """
        if not self._validate_command():
            return False

        if return_x_pulse_cnt is not None:
            self.pause_all_return_x_pulse_count = return_x_pulse_cnt

        if return_y_pulse_cnt is not None:
            self.pause_all_return_y_pulse_count = return_y_pulse_cnt

        if return_z_pulse_cnt is not None:
            self.pause_all_return_z_pulse_count = return_z_pulse_cnt

        if return_e_pulse_cnt is not None:
            self.pause_all_return_e_pulse_count = return_e_pulse_cnt

        if not self._validate_values(self.pause_all_return_x_pulse_count, 0, 1):
            print(f"Invalid pause all return X pulse count {self.pause_all_return_x_pulse_count}")
            return False

        if not self._validate_values(self.pause_all_return_y_pulse_count, 0, 1):
            print(f"Invalid pause all return Y pulse count {self.pause_all_return_y_pulse_count}")
            return False

        if not self._validate_values(self.pause_all_return_z_pulse_count, 0, 1):
            print(f"Invalid pause all return Z pulse count {self.pause_all_return_z_pulse_count}")
            return False

        if not self._validate_values(self.pause_all_return_e_pulse_count, 0, 1):
            print(f"Invalid pause all return E pulse count {self.pause_all_return_e_pulse_count}")
            return False

        if not self.__paused:
            if self.debug:
                print(f"Axis pause command: {command}")
            if self.auto_send_command:
                self.send_command(command=command)

            self.__paused = True

    def resume(self, return_x_pulse_cnt=None, return_y_pulse_cnt=None, return_z_pulse_cnt=None,
               return_e_pulse_cnt=None):
        """
        Resumes one of the pulse trains from running.
        Bytes 6-9 choose to send Pulse count back after pause for each Axis.

        :param return_x_pulse_cnt: X axis pulse count replies, disable = 0, enable = 1 - default 0 or
                                   self.pause_all_return_x_pulse_count
        :param return_y_pulse_cnt: Y axis pulse count replies, disable = 0, enable = 1 - default 0 or
                                   self.pause_all_return_y_pulse_count
        :param return_z_pulse_cnt: Z axis pulse count replies, disable = 0, enable = 1 - default 0 or
                                   self.pause_all_return_z_pulse_count
        :param return_e_pulse_cnt: E axis pulse count replies, disable = 0, enable = 1 - default 0 or
                                   self.pause_all_return_e_pulse_count
        :return: the command to send to the serial port

        Command:

        Byte1	Byte 2-3	Byte 4-5	Byte 6	Byte 7	Byte 8	Byte 9	Byte 10
        ---------------------------------------------------------------------------------------------------------------
        I	    00	        PX	        1	    0	    0	    0	    *

        Command breakdown:

        Byte	    Setting	                Description
        ---------------------------------------------------------------------------------------------------------------
        Byte 1	    I=Instant Command       Sets command to either Instant or Buffer.
                    B=Buffer Command
        Byte 2-3	0-99	                Optional Command ID
        Byte 4-5	PX = Resume X-Axis      Sets which Axis is to be Resumed
                    PY = Resume Y-Axis
                    PZ = Resume Z-Axis
                    PE = Resume E-Axis
                    PA = Resume All
        Byte 6	    0-1	                    Sends back pulse count from Axis if set to 1 with:
                                            PA = X-Axis
                                            PX = X-Axis
                                            PY = Y-Axis
                                            PZ = Z-Axis
                                            PE = E-Axis
        Byte 7	    0-1	                    Sends back pulse count from Axis if set to 1 with:
                                            PA = Y-Axis
                                            Set to 0 for PX, PY,PZ,PE
        Byte 8	    0-1>	                Sends back pulse count from Axis if set to 1 with:
                                            PA = Z-Axis
                                            Set to 0 for PX, PY,PZ,PE
        Byte 9	    0-1	                    Sends back pulse count from Axis if set to 1 with:
                                            PA = E-Axis
                                            Set to 0 for PX, PY,PZ,PE
        Byte 10	    *	                    End of Command

        The PTHAT will send back a reply when it receives a command and also when it has completed a command.
        If Pulse Count is selected then it will also send back the pulse count of chosen Axis.
        In this case the completed command will be sent back when the Axis is resumed, after a Pause.
        If the Command sent ID number was set for bytes 2-3, then this will be returned in the reply.

        X Resume        Y Resume        Z Resume        E Resume        All Resume
        Received        Received        Received        Received        Received
        ---------------------------------------------------------------------------------------------------------------
        CI00PX*	        CI00PY*	        CI00PZ*	        CI00PE*	        CI00PA*
        """
        command = f"{self.command_type}{self.command_id:02}{self.__pause_resume_axis_command}{self.axis}" \
                  f"{self.pause_all_return_x_pulse_count}{self.pause_all_return_y_pulse_count}" \
                  f"{self.pause_all_return_z_pulse_count}{self.pause_all_return_e_pulse_count}{self._command_end}"
        self.__resume(command=command, return_x_pulse_cnt=return_x_pulse_cnt, return_y_pulse_cnt=return_y_pulse_cnt,
                      return_z_pulse_cnt=return_z_pulse_cnt, return_e_pulse_cnt=return_e_pulse_cnt)
        return command

    def resume_all(self, return_x_pulse_cnt=None, return_y_pulse_cnt=None, return_z_pulse_cnt=None,
                   return_e_pulse_cnt=None):
        """
        Resumes all of the pulse trains from running.
        Bytes 6-9 choose to send Pulse count back after pause for each Axis.

        :param return_x_pulse_cnt: X axis pulse count replies, disable = 0, enable = 1 - default 0 or
                                   self.pause_all_return_x_pulse_count
        :param return_y_pulse_cnt: Y axis pulse count replies, disable = 0, enable = 1 - default 0 or
                                   self.pause_all_return_y_pulse_count
        :param return_z_pulse_cnt: Z axis pulse count replies, disable = 0, enable = 1 - default 0 or
                                   self.pause_all_return_z_pulse_count
        :param return_e_pulse_cnt: E axis pulse count replies, disable = 0, enable = 1 - default 0 or
                                   self.pause_all_return_e_pulse_count
        :return: the command to send to the serial port

        Command:

        Byte1	Byte 2-3	Byte 4-5	Byte 6	Byte 7	Byte 8	Byte 9	Byte 10
        ---------------------------------------------------------------------------------------------------------------
        I	    00	        PX	        1	    0	    0	    0	    *

        Command breakdown:

        Byte	    Setting	                Description
        ---------------------------------------------------------------------------------------------------------------
        Byte 1	    I=Instant Command       Sets command to either Instant or Buffer.
                    B=Buffer Command
        Byte 2-3	0-99	                Optional Command ID
        Byte 4-5	PX = Resume X-Axis      Sets which Axis is to be Resumed
                    PY = Resume Y-Axis
                    PZ = Resume Z-Axis
                    PE = Resume E-Axis
                    PA = Resume All
        Byte 6	    0-1	                    Sends back pulse count from Axis if set to 1 with:
                                            PA = X-Axis
                                            PX = X-Axis
                                            PY = Y-Axis
                                            PZ = Z-Axis
                                            PE = E-Axis
        Byte 7	    0-1	                    Sends back pulse count from Axis if set to 1 with:
                                            PA = Y-Axis
                                            Set to 0 for PX, PY,PZ,PE
        Byte 8	    0-1>	                Sends back pulse count from Axis if set to 1 with:
                                            PA = Z-Axis
                                            Set to 0 for PX, PY,PZ,PE
        Byte 9	    0-1	                    Sends back pulse count from Axis if set to 1 with:
                                            PA = E-Axis
                                            Set to 0 for PX, PY,PZ,PE
        Byte 10	    *	                    End of Command

        The PTHAT will send back a reply when it receives a command and also when it has completed a command.
        If Pulse Count is selected then it will also send back the pulse count of chosen Axis.
        In this case the completed command will be sent back when the Axis is resumed, after a Pause.
        If the Command sent ID number was set for bytes 2-3, then this will be returned in the reply.

        X Resume        Y Resume        Z Resume        E Resume        All Resume
        Received        Received        Received        Received        Received
        ---------------------------------------------------------------------------------------------------------------
        CI00PX*	        CI00PY*	        CI00PZ*	        CI00PE*	        CI00PA*
        """
        command = f"{self.command_type}{self.command_id:02}{self.__pause_resume_all_axis_command}" \
                  f"{self.pause_all_return_x_pulse_count}{self.pause_all_return_y_pulse_count}" \
                  f"{self.pause_all_return_z_pulse_count}{self.pause_all_return_e_pulse_count}{self._command_end}"
        self.__resume(command=command, return_x_pulse_cnt=return_x_pulse_cnt, return_y_pulse_cnt=return_y_pulse_cnt,
                      return_z_pulse_cnt=return_z_pulse_cnt, return_e_pulse_cnt=return_e_pulse_cnt)
        return command

    def __resume(self, command, return_x_pulse_cnt=None, return_y_pulse_cnt=None, return_z_pulse_cnt=None,
                 return_e_pulse_cnt=None):
        """
        Resumes one or all of the pulse trains from running.
        Bytes 6-9 choose to send Pulse count back after pause for each Axis.

        :param return_x_pulse_cnt: X axis pulse count replies, disable = 0, enable = 1 - default 0 or
                                   self.pause_all_return_x_pulse_count
        :param return_y_pulse_cnt: Y axis pulse count replies, disable = 0, enable = 1 - default 0 or
                                   self.pause_all_return_y_pulse_count
        :param return_z_pulse_cnt: Z axis pulse count replies, disable = 0, enable = 1 - default 0 or
                                   self.pause_all_return_z_pulse_count
        :param return_e_pulse_cnt: E axis pulse count replies, disable = 0, enable = 1 - default 0 or
                                   self.pause_all_return_e_pulse_count
        :return: the command to send to the serial port

        Command:

        Byte1	Byte 2-3	Byte 4-5	Byte 6	Byte 7	Byte 8	Byte 9	Byte 10
        ---------------------------------------------------------------------------------------------------------------
        I	    00	        PX	        1	    0	    0	    0	    *

        Command breakdown:

        Byte	    Setting	                Description
        ---------------------------------------------------------------------------------------------------------------
        Byte 1	    I=Instant Command       Sets command to either Instant or Buffer.
                    B=Buffer Command
        Byte 2-3	0-99	                Optional Command ID
        Byte 4-5	PX = Resume X-Axis      Sets which Axis is to be Resumed
                    PY = Resume Y-Axis
                    PZ = Resume Z-Axis
                    PE = Resume E-Axis
                    PA = Resume All
        Byte 6	    0-1	                    Sends back pulse count from Axis if set to 1 with:
                                            PA = X-Axis
                                            PX = X-Axis
                                            PY = Y-Axis
                                            PZ = Z-Axis
                                            PE = E-Axis
        Byte 7	    0-1	                    Sends back pulse count from Axis if set to 1 with:
                                            PA = Y-Axis
                                            Set to 0 for PX, PY,PZ,PE
        Byte 8	    0-1>	                Sends back pulse count from Axis if set to 1 with:
                                            PA = Z-Axis
                                            Set to 0 for PX, PY,PZ,PE
        Byte 9	    0-1	                    Sends back pulse count from Axis if set to 1 with:
                                            PA = E-Axis
                                            Set to 0 for PX, PY,PZ,PE
        Byte 10	    *	                    End of Command

        The PTHAT will send back a reply when it receives a command and also when it has completed a command.
        If Pulse Count is selected then it will also send back the pulse count of chosen Axis.
        In this case the completed command will be sent back when the Axis is resumed, after a Pause.
        If the Command sent ID number was set for bytes 2-3, then this will be returned in the reply.

        X Resume        Y Resume        Z Resume        E Resume        All Resume
        Received        Received        Received        Received        Received
        ---------------------------------------------------------------------------------------------------------------
        CI00PX*	        CI00PY*	        CI00PZ*	        CI00PE*	        CI00PA*
        """
        if not self._validate_command():
            return False

        if return_x_pulse_cnt is not None:
            self.pause_all_return_x_pulse_count = return_x_pulse_cnt

        if return_y_pulse_cnt is not None:
            self.pause_all_return_y_pulse_count = return_y_pulse_cnt

        if return_z_pulse_cnt is not None:
            self.pause_all_return_z_pulse_count = return_z_pulse_cnt

        if return_e_pulse_cnt is not None:
            self.pause_all_return_e_pulse_count = return_e_pulse_cnt

        if not self._validate_values(self.pause_all_return_x_pulse_count, 0, 1):
            print(f"Invalid pause all return X pulse count {self.pause_all_return_x_pulse_count}")
            return False

        if not self._validate_values(self.pause_all_return_y_pulse_count, 0, 1):
            print(f"Invalid pause all return Y pulse count {self.pause_all_return_y_pulse_count}")
            return False

        if not self._validate_values(self.pause_all_return_z_pulse_count, 0, 1):
            print(f"Invalid pause all return Z pulse count {self.pause_all_return_z_pulse_count}")
            return False

        if not self._validate_values(self.pause_all_return_e_pulse_count, 0, 1):
            print(f"Invalid pause all return E pulse count {self.pause_all_return_e_pulse_count}")
            return False

        if self.__paused:
            if self.debug:
                print(f"Axis resume command: {command}")
            if self.auto_send_command:
                self.send_command(command=command)

            self.__paused = False

    def get_current_pulse_count(self):
        """
        When this request is sent, it will return of the current pulse count of the running Axis.

        :return: the command to send to the serial port

        Command:

        Byte1	Byte 2-3	Byte 4-5	Byte 6
        ---------------------------------------------------------------------------------------------------------------
        I	    00	        XP	        *

        Command breakdown:

        Byte	    Setting	                Description
        ---------------------------------------------------------------------------------------------------------------
        Byte 1	    I=Instant Command       Sets command to either Instant or Buffer.
                    B=Buffer Command
        Byte 2-3	0-99	                Optional Command ID
        Byte 4-5	XP = Pulse Count X-Axis Request current pulse count for Axis specified
                    YP = Pulse Count X-Axis
                    ZP = Pulse Count X-Axis
                    EP = Pulse Count X-Axis
        Byte 6	    *	                    End of Command

        The PTHAT will send back a reply when it receives a command and also when it has completed a command.
        In this case the received command will be sent back along with the Pulse Count and direction that the motor is
        travelling, then completed command.
        If the Command sent ID number was set for bytes 2-3, then this will be returned in the reply.

        X Pulse Count       Y Pulse Count       Z Pulse Count       E Pulse Count       X Pulse     Y Pulse     Z Pulse     E Pulse
        Received            Received            Received            Received            Count       Count       Count       Count
        *Result*            *Result*            *Result*            *Result*            Completed   Completed   Completed   Completed
        ------------------------------------------------------------------------------------------------------------------------------
        RI00XP*	            RI00YP*	            RI00ZP*	            RI00EP*	            CI00XP*	    CI00YP*	    CI00ZP*	    CI00EP*

        XP(D)XResult	    YP(D)YResult	    ZP(D)ZResult	    EP(D)EResult

        (D)=Direction of    (D)=Direction of    (D)=Direction of    (D)=Direction of
        X motor travel      Y motor travel      Z motor travel      E motor travel

        XResult=            XResult=            XResult=            XResult=
        0000000000-         0000000000-         0000000000-         0000000000-
        4294967295          4294967295          4294967295          4294967295
        """
        if not self._validate_command():
            return False

        command = f"{self.command_type}{self.command_id:02}{self.axis}{self.__request_current_pulse_count_command}" \
                  f"{self._command_end}"
        if self.debug:
            print(f"get_current_pulse_count command: {command}")
        if self.auto_send_command:
            self.send_command(command=command)
        return command

    def change_speed(self, new_frequency):
        """
        This Command changes the speed of each Axis on the fly.
        A Set Axis Command and a Start Command must be used to set the Axis running before this command can be used.

        :param new_frequency: new frequency to change the speed to, 0.0-125000.0 - required
        :return: the command to send to the serial port

        Command:

        Byte1	Byte 2-3	Byte 4-5	Byte 6-15	Byte 16
        ---------------------------------------------------------------------------------------------------------------
        I	    00	        QX	        001000.000	*

        Command breakdown:

        Byte	    Setting	                Description
        ---------------------------------------------------------------------------------------------------------------
        Byte 1	    I=Instant Command       Sets command to either Instant or Buffer.
                    B=Buffer Command
        Byte 2-3	0-99	                Optional Command ID
        Byte 4-5	QX = Set X-Axis         Sets which Axis is to be set
                    QY = Set Y-Axis
                    QZ = Set Z-Axis
                    QE = Set E-Axis
        Byte 6-15	000000.000-125000.000	Sets the frequency of the pulse train
        Byte 16	    *	                    End of Command

        The PTHAT will send back a reply when it receives a command and also when it has completed a command.
        If the Command sent ID number was set for bytes 2-3, then this will be returned in the reply.
        These can be turned off if needed.

        X set       Y set       Z set       E set       X set       Y set       Z set       E set
        Received	Received	Received	Received	Completed	Completed	Completed	Completed
        ---------------------------------------------------------------------------------------------------------------
        RI00QX*	    RI00QY*	    RI00QZ*	    RI00QE*	    CI00QX*	    CI00QY*	    CI00QZ*	    CI00QE*
        """
        self.frequency = new_frequency

        if not self._validate_command():
            return False

        if not self._validate_values(self.frequency, 0.0, 125000.0):
            print(f"Invalid frequency {self.frequency}. Must be between 0.0 and 125000.0")
            return False

        command = f"{self.command_type}{self.command_id:02}{self.__change_axis_speed_command}{self.axis}" \
                  f"{self.frequency:010.3f}{self._command_end}"
        if self.debug:
            print(f"change_speed command: {command}")
        if self.auto_send_command:
            self.send_command(command=command)
        return command

    def enable_limit_switches(self):
        """
        When this request is sent, it will Enable Limit Switch or Emergency Stop inputs. A reset on the PTHAT
        will set them to default of Disable

        :return: the command to send to the serial port

        Command:

        Byte1	Byte 2-3	Byte 4-5	Byte 6	Byte 7
        ---------------------------------------------------------------------------------------------------------------
        I	    00	        KX	        1	    *

        Command breakdown:

        Byte	    Setting	                Description
        ---------------------------------------------------------------------------------------------------------------
        Byte 1	    I=Instant Command       Sets command to either Instant or Buffer.
                    B=Buffer Command
        Byte 2-3	0-99	                Optional Command ID
        Byte 4-5	KX = Set Limit Switch X Set Limit Switch or Emergency Stop Enable/Disable
                    KY = Set Limit Switch Y
                    KZ = Set Limit Switch Z
                    KE = Set Limit Switch E
                    KS = Set Emergency Stop
        Byte 6	    0=Disable               Switches selected Limit Switch to Enable/Disable
                    1=Enable
        Byte 7	    *	                    End of Command

        The PTHAT will send back a reply when it receives a command and also when it has completed a command.
        If the Command sent ID number was set for bytes 2-3, then this will be returned in the reply.

        X Limit     Y Limit     Z Limit     E Limit     Emergency       X Limit     Y Limit     Z Limit     E Limit     Emergency
        Received    Received    Received    Received    Stop            Completed   Completed   Completed   Completed   Stop
                                                        Received                                                        Completed
        ---------------------------------------------------------------------------------------------------------------------------
        R00KX*	    R00KY*	    R00KZ*	    R00KE*	    R00KS*	        C00KX*	    C00KY*	    C00KZ*	    C00KE*	    C00KS*
        """
        if not self._validate_command():
            return False

        command = f"{self.command_type}{self.command_id:02}{self.__enable_disable_limit_switches_command}{self.axis}1" \
                  f"{self._command_end}"
        if self.debug:
            print(f"enable_limit_switches command: {command}")
        if self.auto_send_command:
            self.send_command(command=command)
        return command

    def disable_limit_switches(self):
        """
        When this request is sent, it will Disable Limit Switch or Emergency Stop inputs. A reset on the PTHAT
        will set them to default of Disable

        :return: the command to send to the serial port

        Command:

        Byte1	Byte 2-3	Byte 4-5	Byte 6	Byte 7
        ---------------------------------------------------------------------------------------------------------------
        I	    00	        KX	        0	    *

        Command breakdown:

        Byte	    Setting	                Description
        ---------------------------------------------------------------------------------------------------------------
        Byte 1	    I=Instant Command       Sets command to either Instant or Buffer.
                    B=Buffer Command
        Byte 2-3	0-99	                Optional Command ID
        Byte 4-5	KX = Set Limit Switch X Set Limit Switch or Emergency Stop Enable/Disable
                    KY = Set Limit Switch Y
                    KZ = Set Limit Switch Z
                    KE = Set Limit Switch E
                    KS = Set Emergency Stop
        Byte 6	    0=Disable               Switches selected Limit Switch to Enable/Disable
                    1=Enable
        Byte 7	    *	                    End of Command

        The PTHAT will send back a reply when it receives a command and also when it has completed a command.
        If the Command sent ID number was set for bytes 2-3, then this will be returned in the reply.

        X Limit     Y Limit     Z Limit     E Limit     Emergency       X Limit     Y Limit     Z Limit     E Limit     Emergency
        Received    Received    Received    Received    Stop            Completed   Completed   Completed   Completed   Stop
                                                        Received                                                        Completed
        ---------------------------------------------------------------------------------------------------------------------------
        R00KX*	    R00KY*	    R00KZ*	    R00KE*	    R00KS*	        C00KX*	    C00KY*	    C00KZ*	    C00KE*	    C00KS*
        """
        if not self._validate_command():
            return False

        command = f"{self.command_type}{self.command_id:02}{self.__enable_disable_limit_switches_command}{self.axis}0" \
                  f"{self._command_end}"
        if self.debug:
            print(f"disable_limit_switches command: {command}")
        if self.auto_send_command:
            self.send_command(command=command)
        return command

    def enable_emergency_stop(self):
        """
        When this request is sent, it will Disable Limit Switch or Emergency Stop inputs. A reset on the PTHAT
        will set them to default of Disable

        :return: the command to send to the serial port

        Command:

        Byte1	Byte 2-3	Byte 4-5	Byte 6	Byte 7
        ---------------------------------------------------------------------------------------------------------------
        I	    00	        KS	        1	    *

        Command breakdown:

        Byte	    Setting	                Description
        ---------------------------------------------------------------------------------------------------------------
        Byte 1	    I=Instant Command       Sets command to either Instant or Buffer.
                    B=Buffer Command
        Byte 2-3	0-99	                Optional Command ID
        Byte 4-5	KX = Set Limit Switch X Set Limit Switch or Emergency Stop Enable/Disable
                    KY = Set Limit Switch Y
                    KZ = Set Limit Switch Z
                    KE = Set Limit Switch E
                    KS = Set Emergency Stop
        Byte 6	    0=Disable               Switches selected Limit Switch to Enable/Disable
                    1=Enable
        Byte 7	    *	                    End of Command

        The PTHAT will send back a reply when it receives a command and also when it has completed a command.
        If the Command sent ID number was set for bytes 2-3, then this will be returned in the reply.

        X Limit     Y Limit     Z Limit     E Limit     Emergency       X Limit     Y Limit     Z Limit     E Limit     Emergency
        Received    Received    Received    Received    Stop            Completed   Completed   Completed   Completed   Stop
                                                        Received                                                        Completed
        ---------------------------------------------------------------------------------------------------------------------------
        R00KX*	    R00KY*	    R00KZ*	    R00KE*	    R00KS*	        C00KX*	    C00KY*	    C00KZ*	    C00KE*	    C00KS*
        """
        if not self._validate_command():
            return False

        command = f"{self.command_type}{self.command_id:02}{self.__enable_disable_limit_switches_command}S1" \
                  f"{self._command_end}"
        if self.debug:
            print(f"enable_emergency_stop command: {command}")
        if self.auto_send_command:
            self.send_command(command=command)
        return command

    def disable_emergency_stop(self):
        """
        When this request is sent, it will Disable Limit Switch or Emergency Stop inputs. A reset on the PTHAT
        will set them to default of Disable

        :return: the command to send to the serial port

        Command:

        Byte1	Byte 2-3	Byte 4-5	Byte 6	Byte 7
        ---------------------------------------------------------------------------------------------------------------
        I	    00	        KX	        1	    *

        Command breakdown:

        Byte	    Setting	                Description
        ---------------------------------------------------------------------------------------------------------------
        Byte 1	    I=Instant Command       Sets command to either Instant or Buffer.
                    B=Buffer Command
        Byte 2-3	0-99	                Optional Command ID
        Byte 4-5	KX = Set Limit Switch X Set Limit Switch or Emergency Stop Enable/Disable
                    KY = Set Limit Switch Y
                    KZ = Set Limit Switch Z
                    KE = Set Limit Switch E
                    KS = Set Emergency Stop
        Byte 6	    0=Disable               Switches selected Limit Switch to Enable/Disable
                    1=Enable
        Byte 7	    *	                    End of Command

        The PTHAT will send back a reply when it receives a command and also when it has completed a command.
        If the Command sent ID number was set for bytes 2-3, then this will be returned in the reply.

        X Limit     Y Limit     Z Limit     E Limit     Emergency       X Limit     Y Limit     Z Limit     E Limit     Emergency
        Received    Received    Received    Received    Stop            Completed   Completed   Completed   Completed   Stop
                                                        Received                                                        Completed
        ---------------------------------------------------------------------------------------------------------------------------
        R00KX*	    R00KY*	    R00KZ*	    R00KE*	    R00KS*	        C00KX*	    C00KY*	    C00KZ*	    C00KE*	    C00KS*
        """
        if not self._validate_command():
            return False

        command = f"{self.command_type}{self.command_id:02}{self.__enable_disable_limit_switches_command}S0" \
                  f"{self._command_end}"
        if self.debug:
            print(f"disable_emergency_stop command: {command}")
        if self.auto_send_command:
            self.send_command(command=command)
        return command

    def reset(self):
        """
        Call reset on the parent class and then reset all the variables
        """
        super().reset()
        self.frequency = 0.0
        self.pulse_count = 0
        self.direction = 0
        self.start_ramp = 0
        self.finish_ramp = 0
        self.ramp_divide = 0
        self.ramp_pause = 0
        self.link_to_adc = 0
        self.enable_line_polarity = 0
        self.pulse_count_change_direction = 0
        self.pulse_counts_sent_back = 0
        self.enable_disable_x_pulse_count_replies = 1
        self.enable_disable_y_pulse_count_replies = 1
        self.enable_disable_z_pulse_count_replies = 1
        self.enable_disable_e_pulse_count_replies = 1
        self.pause_all_return_x_pulse_count = 0
        self.pause_all_return_y_pulse_count = 0
        self.pause_all_return_z_pulse_count = 0
        self.pause_all_return_e_pulse_count = 0
        self.__paused = False
        self.__started = False

    def _validate_command(self):
        """
        Validate command settings that are the same for every axis command
        :return: true if the command settings are valid, otherwise false
        """
        if not self.axis == "X" and not self.axis == "Y" and not self.axis == "Z" and not self.axis == "E":
            if self.debug:
                print(f"Invalid axis {self.axis}")
            return False

        return super()._validate_command()


class ADC(PTHat):
    """
    This is an ADC class containing info about an ADC. It inherits from PTHat so contains all functionality
    needed to communicate with the PTHat via the serial interface.
    """
    # Properties
    adc_number = 1  # ADC number - Currently 1 or 2

    # ADC commands
    __request_adc_reading_command = "D"  # Request current ADC value - D1 = ADC1 Result, D2 = ADC2 Result

    def __init__(self, adc_number, command_type="I", command_id=0, serial_device="/dev/ttyS0", baud_rate=115200,
                 test_mode=False):
        """
        Constructor

        :param adc_number: ADC number, 1 or 2
        :param command_type: type of command, I = instant, B = buffered - default I
        :param command_id: optional command ID, 0-99 - default 0
        :param serial_device: serial device - default /dev/ttyS0
        :param baud_rate: serial port baud rate - default 115200
        :param test_mode: if true then serial commands will not actually be sent - default False
        """
        super().__init__(command_type=command_type, command_id=command_id, serial_device=serial_device,
                         baud_rate=baud_rate, test_mode=test_mode)
        if self._validate_values(adc_number, 1, 2):
            if self.debug:
                print(f"Valid ADC number {self.adc_number}.")
            self.adc_number = adc_number
        else:
            self.adc_number = 1     # Default to 1 if they pass an invalid number

    def get_reading(self, adc_number=None):
        """
        When this request is sent, it will return the value of the ADC requested.

        :param adc_number ADC number, 1 or 2 - default 1 or self.adc_number
        :return: the command to send to the serial port

        Command:

        Byte1	Byte 2-3	Byte 4-5	Byte 6
        ---------------------------------------------------------------------------------------------------------------
        I	    00	        D1	        *

        Command breakdown:

        Byte	    Setting	                Description
        ---------------------------------------------------------------------------------------------------------------
        Byte 1	    I=Instant Command       Sets command to either Instant or Buffer.
                    B=Buffer Command
        Byte 2-3	0-99	                Optional Command ID
        Byte 4-5	D1= ADC1 Result         Request current ADC value
                    D2= ADC2 Result
        Byte 6	    *	                    End of Command

        The PTHAT will send back a reply when it receives a command and also when it has completed a command.
        In this case the received command will be sent back along with the ADC result and then completed command.
        If the Command sent ID number was set for bytes 2-3, then this will be returned in the reply.

        ADC1 Received       ADC2 Received       ADC1            ADC2
        *Result*	        *Result*            Completed       Completed
        ---------------------------------------------------------------------------------------------------------------
        RI00D1**Result*	    RI00D2**Result*	    CI00D1*	        CI00D2*
        """
        if not self._validate_command():
            return False

        if adc_number is not None:
            self.adc_number = adc_number

        if not self._validate_values(self.adc_number, 1, 2):
            print(f"Invalid ADC number {self.adc_number}. Should be 1 or 2")
            return False

        command = f"{self.command_type}{self.command_id:02}{self.__request_adc_reading_command}{self.adc_number}" \
                  f"{self._command_end}"
        if self.debug:
            print(f"get_reading command: {command}")
        if self.auto_send_command:
            self.send_command(command=command)
        return command

    def reset(self):
        """
        Call reset on the parent class and then reset all the variables
        """
        super().reset()

        self.adc_number = 1


class AUX(PTHat):
    """
    This is an AUC class containing info about an AUX. It inherits from PTHat so contains all functionality
    needed to communicate with the PTHat via the serial interface.
    """
    # Properties
    aux_number = 1  # ADC number, currently 1, 2 or 3

    # AUX commands
    __set_on_off_aux_output_command = "A"  # Set on/off AUX output command - A1 = Set AUX1, A2 = Set AUX2, A3 = Set AUX3

    def __init__(self, aux_number, command_type="I", command_id=0, serial_device="/dev/ttyS0", baud_rate=115200,
                 test_mode=False):
        """
        Constructor

        :param aux_number: AUX number, 1-3
        :param command_type: type of command, I = instant, B = buffered - default I
        :param command_id: optional command ID, 0-99 - default 0
        :param serial_device: serial device - default /dev/ttyS0
        :param baud_rate: serial port baud rate - default 115200
        :param test_mode: if true then serial commands will not actually be sent - default False
        """
        super().__init__(command_type=command_type, command_id=command_id, serial_device=serial_device,
                         baud_rate=baud_rate, test_mode=test_mode)
        if self._validate_values(aux_number, 1, 3):
            if self.debug:
                print(f"Valid AUX number {self.aux_number}.")
            self.aux_number = aux_number
        else:
            self.aux_number = 1     # Default to 1 if they pass an invalid number

    def output_on(self, aux_number=None):
        """
        When this request is sent, it will switch on the Aux port.

        :param aux_number: AUX number, 1-3, default 1 or self.aux_number
        :return: the command to send to the serial port

        Command:

        Byte1	Byte 2-3	Byte 4-5	Byte 6	Byte 7
        ---------------------------------------------------------------------------------------------------------------
        I	    00	        A1	        1	    *

        Command breakdown:

        Byte	    Setting	                Description
        ---------------------------------------------------------------------------------------------------------------
        Byte 1	    I=Instant Command       Sets command to either Instant or Buffer.
                    B=Buffer Command
        Byte 2-3	0-99	                Optional Command ID
        Byte 4-5    A1 = Set Aux1           Set Aux port for switching
                    A2 = Set Aux2
                    A3 = Set Aux3
        Byte 6	    0=Off                   Switches selected Aux On or Off
                    1=On
        Byte 7	    *	                    End of Command

        The PTHAT will send back a reply when it receives a command and also when it has completed a command.
        If the Command sent ID number was set for bytes 2-3, then this will be returned in the reply.

        Aux1 Received   Aux2 Received	Aux3 Received	Aux1 Completed	Aux2 Completed	Aux3 Completed
        ---------------------------------------------------------------------------------------------------------------
        R00A1*	        R00A2*	        R00A3*	        C00A1*	        C00A2*	        C00A3*
        """
        if not self._validate_command():
            return False

        if aux_number is not None:
            self.aux_number = aux_number

        if not self._validate_values(self.aux_number, 1, 3):
            print(f"Invalid AUX number {self.aux_number}. Should be between 1 and 3")

        command = f"{self.command_type}{self.command_id:02}{self.__set_on_off_aux_output_command}{self.aux_number}1" \
                  f"{self._command_end}"
        if self.debug:
            print(f"output_on command: {command}")
        if self.auto_send_command:
            self.send_command(command=command)
        return command

    def output_off(self, aux_number=None):
        """
        When this request is sent, it will switch off the Aux port.

        :param aux_number: AUX number, 1-3, default 1 or self.aux_number
        :return: the command to send to the serial port

        Command:

        Byte1	Byte 2-3	Byte 4-5	Byte 6	Byte 7
        ---------------------------------------------------------------------------------------------------------------
        I	    00	        A1	        0	    *

        Command breakdown:

        Byte	    Setting	                Description
        ---------------------------------------------------------------------------------------------------------------
        Byte 1	    I=Instant Command       Sets command to either Instant or Buffer.
                    B=Buffer Command
        Byte 2-3	0-99	                Optional Command ID
        Byte 4-5    A1 = Set Aux1           Set Aux port for switching
                    A2 = Set Aux2
                    A3 = Set Aux3
        Byte 6	    0=Off                   Switches selected Aux On or Off
                    1=On
        Byte 7	    *	                    End of Command

        The PTHAT will send back a reply when it receives a command and also when it has completed a command.
        If the Command sent ID number was set for bytes 2-3, then this will be returned in the reply.

        Aux1 Received   Aux2 Received	Aux3 Received	Aux1 Completed	Aux2 Completed	Aux3 Completed
        ---------------------------------------------------------------------------------------------------------------
        R00A1*	        R00A2*	        R00A3*	        C00A1*	        C00A2*	        C00A3*
        """
        if not self._validate_command():
            return False

        if aux_number is not None:
            self.aux_number = aux_number

        if not self._validate_values(self.aux_number, 1, 3):
            print(f"Invalid AUX number {self.aux_number}. Should be between 1 and 3")

        command = f"{self.command_type}{self.command_id:02}{self.__set_on_off_aux_output_command}{self.aux_number}0" \
                  f"{self._command_end}"
        if self.debug:
            print(f"output_off command: {command}")
        if self.auto_send_command:
            self.send_command(command=command)
        return command

    def reset(self):
        """
        Call reset on the parent class and then reset all the variables
        """
        super().reset()

        self.aux_number = 1


class PWM(PTHat):
    """
    This is an PWM class containing info about an PWM. It inherits from PTHat so contains all functionality
    needed to communicate with the PTHat via the serial interface.

    From Firmware V5.3 onwards there are commands for controlling two dedicated PWM channels. Details for PWM can be
    found here: http://pthat.com/index.php/pwm/
    """
    # Properties
    axis = "X"  # Sets which Axis is to be set - X or Y, if UA then this doesn't matter as it will do both X and Y
    frequency = 0  # Frequency for the channel is in 1Hz steps - 0000000-1000000
    duty_cycle = 0   # Sets the Duty Cycle 0-100%, The last 2 digits are decimal places. So 08050 would be 80.5%

    # Used for Set Both PWM Channels Command only
    frequency_x = 0  # Sets the Frequency for the channel in 1Hz steps for X-Axis
    frequency_y = 0  # Sets the Frequency for the channel in 1Hz steps for Y-Axis
    duty_cycle_x = 0   # Sets the Duty Cycle 0-100% for X-Axis
    duty_cycle_y = 0   # Sets the Duty Cycle 0-100% for Y-Axis

    # PWM commands
    __set_pwm_channel_command = "U"  # Sets the PWM channel - UX= Set X-Axis, UY= Set Y-Axis
    __set_both_pwm_channels_command = "UA"  # Sets both PWM channels in one command - UA= Set X-Axis and Y-Axis

    def __init__(self, axis, command_type="I", command_id=0, serial_device="/dev/ttyS0", baud_rate=115200,
                 test_mode=False):
        """
        Constructor

        :param axis: axis for this class
        :param command_type: type of command, I = instant, B = buffered - default I
        :param command_id: optional command ID, 0-99 - default 0
        :param serial_device: serial device - default /dev/ttyS0
        :param baud_rate: serial port baud rate - default 115200
        :param test_mode: if true then serial commands will not actually be sent - default False
        """
        super().__init__(command_type=command_type, command_id=command_id, serial_device=serial_device,
                         baud_rate=baud_rate, test_mode=test_mode)
        if str(axis).upper() == "X" or str(axis).upper() == "Y" or str(axis).upper() == "A":
            self.axis = axis.upper()
        else:
            self.axis = "X"     # Default to X if they pass an invalid axis

    def set_channel(self, frequency=None, duty_cycle=None):
        """
        ***Available Firmware V5.3 upwards***
        This Command sets the Frequency and Pulse Width for the desired channel.
        It then also starts it.

        :param frequency: frequency for the channel in 1Hz steps, 0000000-1000000 - default 0 or self.frequency
        :param duty_cycle: duty cycle 0-100%. The last 2 digits are decimal places. So 08050 would be 80.5% - default 0
                           or self.duty_cycle
        :return: the command to send to the serial port

        Command:

        Byte1	Byte 2-3	Byte 4-5	Byte 6-12	Byte 13-17	Byte 18
        ---------------------------------------------------------------------------------------------------------------
        I	    00	        UX	        0000000	    00000	    *

        Command breakdown:

        Byte	    Setting	                Description
        ---------------------------------------------------------------------------------------------------------------
        Byte 1	    I=Instant Command       Sets command to either Instant or Buffer.
                    B=Buffer Command
        Byte 2-3	0-99	                Optional Command ID
        Byte 4-5	UX= Set X-Axis          Sets which Axis is to be set
                    UY= Set Y-Axis
        Byte 6-12	0000000-1000000	        Sets the Frequency for the channel in 1Hz steps
        Byte 14-17	00000	                Sets the Duty Cycle 0-100%
                                            The last 2 digits are decimal places. So 08050 would be 80.5%
        Byte 18	    *	                    End of Command

        The PTHAT will send back a reply when it receives a command and also when it has completed a command.
        If the Command sent ID number was set for bytes 2-3, then this will be returned in the reply.
        These can be turned off if needed.

        X set       Y set       X set       Y set
        Received	Received	Completed   Completed
        ---------------------------------------------------------------------------------------------------------------
        RI00UX*	    RI00UY*	    CI00UX*	    CI00UY*
        """
        if not self._validate_command():
            return False

        if not self.axis == "X" and not self.axis == "Y":
            print(f"Invalid axis {self.axis}. Should be X or Y")
            return False

        if frequency is not None:
            self.frequency = frequency

        if duty_cycle is not None:
            self.duty_cycle = duty_cycle

        if not self._validate_values(self.frequency, 0, 1000000):
            print(f"Invalid frequency {self.frequency}. Should be between 0 and 1000000")
            return False

        if not self._validate_values(self.duty_cycle, 0, 100):
            print(f"Invalid duty cycle {self.duty_cycle}. Should be between 0 and 100")
            return False

        self.duty_cycle = self.duty_cycle * 100

        command = f"{self.command_type}{self.command_id:02}{self.__set_pwm_channel_command}{self.axis}" \
                  f"{self.frequency:07}{self.duty_cycle:05}{self._command_end}"
        if self.debug:
            print(f"set_channel command: {command}")
        if self.auto_send_command:
            self.send_command(command=command)
        return command

    def set_frequency(self, frequency):
        """
        Set the PWM frequency

        :param frequency: frequency for the channel in 1Hz steps, 0000000-1000000 - default 0
        :return: the command to send to the serial port
        """
        return self.set_channel(frequency=frequency)

    def set_duty_cycle(self, duty_cycle):
        """
        Set the PWM duty cycle

        :param duty_cycle: duty cycle 0-100%. The last 2 digits are decimal places. So 08050 would be 80.5% - default 0
        :return: the command to send to the serial port
        """
        return self.set_channel(duty_cycle=duty_cycle)

    def set_both_channels(self, frequencyx=None, frequencyy=None, duty_cyclex=None, duty_cycley=None):
        """
        ***Available Firmware V5.3 upwards***
        This Command sets the Frequency and Pulse Width for both channels at the same time.
        It then also starts both together.

        :param frequencyx: frequency for the X channel in 1Hz steps, 0000000-1000000 - default 0 or self.frequency_x
        :param frequencyy: frequency for the Y channel in 1Hz steps, 0000000-1000000 - default 0 or self.frequency_y
        :param duty_cyclex: duty cycle for X channel 0-100%. The last 2 digits are decimal places. So 08050 would be
                    80.5% - default 0 or self.duty_cycle_x
        :param duty_cycley: duty cycle for Y channel 0-100%. The last 2 digits are decimal places. So 08050 would be
                    80.5% - default 0 or self.duty_cycle_x
        :return: the command to send to the serial port

        Command:

        Byte1	Byte 2-3	Byte 4-5	Byte 6-12	Byte 13-17	Byte 18-24	Byte 25-29	Byte 30
        ---------------------------------------------------------------------------------------------------------------
        I	    00	        UX	        0000000	    00000	    0000000	    00000	    *

        Command breakdown:

        Byte	    Setting	                    Description
        ---------------------------------------------------------------------------------------------------------------
        Byte 1	    I=Instant Command           Sets command to either Instant or Buffer.
                    B=Buffer Command
        Byte 2-3	0-99	                    Optional Command ID
        Byte 4-5	UA=Set X-Axis and Y-Axis	Sets both X-Axis and Y-Axis settings
        Byte 6-12	0000000-1000000	            Sets the Frequency for the channel in 1Hz steps for X-Axis
        Byte 14-17	00000	                    Sets the Duty Cycle 0-100% for X-Axis
                                                The last 2 digits are decimal places. So 08050 would be 80.5%
        Byte 18-24	0000000-1000000	            Sets the Frequency for the channel in 1Hz steps for Y-Axis
        Byte 25-29	00000	                    Sets the Duty Cycle 0-100% for Y-Axis
                                                The last 2 digits are decimal places. So 08050 would be 80.5%
        Byte 30	    *	                        End of Command

        The PTHAT will send back a reply when it receives a command and also when it has completed a command.
        If the Command sent ID number was set for bytes 2-3, then this will be returned in the reply.
        These can be turned off if needed.

        Set both PWM channels       Set both PWM channels
        Received	                Completed
        ---------------------------------------------------------------------------------------------------------------
        RI00UA*	                    CI00UA*
        """
        if not self._validate_command():
            return False

        if frequencyx is not None:
            self.frequency_x = frequencyx

        if frequencyy is not None:
            self.frequency_y = frequencyy

        if duty_cyclex is not None:
            self.duty_cycle_x = duty_cyclex

        if duty_cycley is not None:
            self.duty_cycle_y = duty_cycley

        if not self._validate_values(self.frequency_x, 0, 1000000):
            print(f"Invalid frequency X {self.frequency_x}. Should be between 0 and 1000000")
            return False

        if not self._validate_values(self.frequency_y, 0, 1000000):
            print(f"Invalid frequency Y {self.frequency_y}. Should be between 0 and 1000000")
            return False

        if not self._validate_values(self.duty_cycle_x, 0, 100):
            print(f"Invalid duty cycle X {self.duty_cycle_x}. Should be between 0 and 100")
            return False

        if not self._validate_values(self.duty_cycle_y, 0, 100):
            print(f"Invalid duty cycle Y {self.duty_cycle_y}. Should be between 0 and 100")
            return False

        self.duty_cycle_x = self.duty_cycle_x * 100
        self.duty_cycle_y = self.duty_cycle_y * 100

        command = f"{self.command_type}{self.command_id:02}{self.__set_both_pwm_channels_command}" \
                  f"{self.frequency_x:07}{self.duty_cycle_x:05}{self.frequency_y:07}{self.duty_cycle_y:05}" \
                  f"{self._command_end}"
        if self.debug:
            print(f"set_both_channels command: {command}")
        if self.auto_send_command:
            self.send_command(command=command)
        return command

    def reset(self):
        """
        Call reset on the parent class and then reset all the variables
        """
        super().reset()

        self.frequency = 0
        self.duty_cycle = 0
        self.frequency_x = 0
        self.frequency_y = 0
        self.duty_cycle_x = 0
        self.duty_cycle_y = 0
