import time
from typing import Optional, Tuple, Union
import functools

from .device import SerialDevice, check_initialized, check_serial


class ScitechLamp(SerialDevice):
    def __init__(
            self, 
            name: str,
            port: str,
            baudrate: int = 9600,
            timeout: Optional[float] = 2.5,
            poll_interval: float = 0.1):

        super().__init__(name, port, baudrate, timeout)
        self._poll_interval = poll_interval

    # check_error already has serial check
    # easier to just set is_intialized False at the very beginning
    # do for all receivers
    def initialize(self) -> Tuple[bool, str]:
        # if not self.ser.is_open:
        #     return (False, "Serial port " + self._port + " is not open. ")
        flag, msg = self.is_light_on()

        was_successful, message = self.check_error() # just used to flush error and serial input buffer if there is an error
        if not was_successful:
            return (was_successful, message)

        self.ser.reset_input_buffer() # flush the serial input buffer even if there was no error

        # Make sure initialization of settings was successful
        was_successful, message = self.check_error()
        if not was_successful:
            self._is_initialized = False
            return (was_successful, message)

        for axis in self._axis_list:
            was_homed, message = self.home(axis)
            if not was_homed:
                self._is_initialized = False
                return (was_homed, message)
    
        self._is_initialized = True
        return (True, "Successfully initialized axes by setting units to mm, settings max/current speeds, and homing. Current position set to zero.")

    # move_speed_absolute already has serial check
    def deinitialize(self, reset_init_flag: bool = True) -> Tuple[bool, str]:
        # if not self.ser.is_open:
        #     return (False, "Serial port " + self._port + " is not open. ")

        for axis in self._axis_list:
            was_zeroed, message = self.move_speed_absolute(0.0, speed=None, axis_number=axis)
            if not was_zeroed:
                return (was_zeroed, message)

        if reset_init_flag:
            self._is_initialized = False

        return (True, "Successfully deinitialized axes by moving to position zero.")

    # make a home_all function
    @check_serial
    def home(self, axis_number: int) -> Tuple[bool, str]:
        # if not self.ser.is_open:
        #     return (False, "Serial port " + self._port + " is not open. ")

        command = str(axis_number) + "OR4\r"
        self.ser.write(command.encode('ascii'))

        while self.is_any_moving():
            time.sleep(self._poll_interval)
        # pause one more time in case motor stopped moving but position has not been reset yet     
        time.sleep(self._poll_interval)

        was_successful, message = self.check_error()
        if not was_successful:
            return (was_successful, message)
        else:
            return (True, "Successfully homed axes " + str(axis_number))

    # Consider a decorator for checks?
    @check_serial
    @check_initialized
    @check_axis_num
    def move_speed_absolute(self, axis_number: int = 1, position: Optional[float] = None, speed: Optional[float] = None) -> Tuple[bool, str]:
        # if not self.ser.is_open:
        # #     return (False, "Serial port " + self._port + " is not open. ")
        # if not self.is_axis_num_valid(axis_number):
        #     return (False, "Axis number is not valid or not part of passed tuple during construction.")
        # if not self._is_initialized:
        #     return (False, "ESP301 axes are not initialized.")
        
        # I want axis number to be the first arg so the decorator can pick it up as arg[0]
        # but I also want axis_number to have a default value of 1, so position needs a default value now
        if position is None:
            return (False, "Position was not specified")

        if speed is None:
            speed = self._default_speed

        command = str(axis_number) + "VA" + str(speed) +"\r"
        self.ser.write(command.encode('ascii'))

        was_successful, message = self.check_error()
        if not was_successful:
            return (was_successful, message)

        if position >= 0.0:
            sign = "+"
        else:
            sign = "-"

        # removed the WS command because it causes timeouts when checking if moving 
        # command = str(axis_number) + "PA" + sign + str(abs(position)) + ";" + str(axis_number) + "WS\r"
        command = str(axis_number) + "PA" + sign + str(abs(position)) + "\r"
        self.ser.write(command.encode('ascii'))

        while self.is_moving(axis_number):
            time.sleep(self._poll_interval)

        was_successful, message = self.check_error()
        if not was_successful:
            return (was_successful, message)
        else:
            return (True, "Successfully completed absolute move at " + str(position))

    @check_serial
    @check_initialized
    @check_axis_num
    def move_speed_relative(self, axis_number: int = 1, distance: Optional[float] = None, speed: Optional[float] = None) -> Tuple[bool, str]:
        # if not self.ser.is_open:
        # #     return (False, "Serial port " + self._port + " is not open. ")
        # if not self.is_axis_num_valid(axis_number):
        #     return (False, "Axis number is not valid or not part of passed tuple during construction.")
        # if not self._is_initialized:
        #     return (False, "ESP301 axes are not initialized.")
        if distance is None:
            return (False, "Distance was not specified")
        
        if speed is None:
            speed = self._default_speed

        command = str(axis_number) + "VA" + str(speed) +"\r"
        self.ser.write(command.encode('ascii'))

        was_successful, message = self.check_error()
        if not was_successful:
            return (was_successful, message)

        if distance >= 0.0:
            sign = "+"
        else:
            sign = "-"

        # removed the WS command because it causes timeouts when checking if moving 
        # command = str(axis_number) + "PR" + sign + str(abs(distance)) + ";" + str(axis_number) + "WS\r"
        command = str(axis_number) + "PR" + sign + str(abs(distance)) + "\r"

        self.ser.write(command.encode('ascii'))

        while self.is_moving(axis_number):
            time.sleep(self._poll_interval)

        was_successful, message = self.check_error()
        if not was_successful:
            return (was_successful, message)
        else:
            return (True, "Successfully completed relative move by " + str(distance))


    def is_light_on(self) -> bool:
        # check if lamp is turned on or off : 1 if on, 0 if off
        was_successful, msg = self.check_error()


        
        if res[0] == '1':
            return True
        else :
            return False


    def turn_on_simulator(self) -> Tuple[bool, str]:
        #first chck if light is on
        is_on = self.is_light_on()
        if is_on :
            return(True, "Solar simulator is already turned on")
        else:
            command = "START\r"
            self.ser.write(command.encode('ascii'))
            time.sleep(0.5)
            response = self.ser.readline().decode('ascii')
            if response[-2:] == '01':
                return (True, "Succesfully turned on the Solar simulator.")
            else :
                light_on = self.is_light_on()
                if light_on :
                    return (True, "Succesfully turned on the Solar simulator.")
                else:
                    return (False,  "")





    @check_serial
    def check_error(self) -> Tuple[bool, str]:
        # not needed for queries, but use when instructing to do something
        
        # if not self.ser.is_open:
        #     return (False, "Serial port " + self._port + " is not open. ")

        command = "C1\r"
        self.ser.write(command.encode())
        time.sleep(0.5)
        response = self.ser.readline()

        if response == b'':
            return (False, "Response timed out.")
        
        response = response.strip().decode('ascii')[0:2]

        if response == 'OK':
            return (True, "No errors.")
        else:
            # flush the error buffer
            for n in range(10):
                self.ser.write(command.encode())
                self.ser.readline()
            # flush the serial input buffer
            time.sleep(0.5)
            self.ser.reset_input_buffer()
            return (False, "Something went wrong.")

    def check_power(self) -> Tuple[bool,Union[str,float]] :
        # check the power of lamp
        command = 'FS\r'
        self.ser.write(command.encode())
        time.sleep(0.5)
        response = self.ser.readall()

        flag, msg = self.check_error()

        if response == b'' :
            return (False, "Response timed out.")
        else :
            return (True, float(response.decode('ascii').[44:49])/100)

    def check_cooler(self) -> Tuple[bool, Union[str, float]] :
        # check if coller is on or off : 1 if on, 0 if off
        command = 'FS\r'
        self.ser.write(command.encode())
        time.sleep(0.5)
        response = self.ser.readall()

        if response == b'' :
            return (False, "Response timed out.")
        else:
            return (True, float(response.decode('ascii').[66:67]))

    def check_lamp(self) -> Tuple[bool, Union[str, float]] :
        # check if lamp is turned on or off : 1 if on, 0 if off
        command = 'FS\r'
        self.ser.write(command.encode())
        time.sleep(0.5)
        response = self.ser.readall()

        if response == b'' :
            return (False, "Response timed out.")
        else:
            return (True, float(response.decode('ascii').[74:75]))

    def check_output(self) -> Tuple[bool,Union[str,float]] :
        # check current output percentage(%)
        command = 'FS\r'
        self.ser.write(command.encode())
        time.sleep(0.5)
        response = self.ser.readall()

        if response == b'' :
            return (False, "Response timed out.")
        else :
            return (True, float(response.decode('ascii').[111:115])/10)

    def check_shutter(self) -> Tuple[bool,Union[str,float]] :
        # check shutter : 0 if open, 1 if closed
        command = 'FS\r'
        self.ser.write(command.encode())
        time.sleep(0.5)
        response = self.ser.readall()

        if response == b'' :
            return (False, "Response timed out.")
        else :
            return (True, float(response.decode('ascii').[157:158]))


    def check_attenuator(self) -> Tuple[bool, Union[str, float]] :
        # check attenuator(% transmittance)
        command = 'FS\r'
        self.ser.write(command.encode())
        time.sleep(0.5)
        response = self.ser.readall()

        if response == b'' :
            return (False, "Response timed out.")
        else:
            return (True, float(response.decode('ascii').[171:174]))