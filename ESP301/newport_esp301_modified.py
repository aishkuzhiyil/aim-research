import time
from typing import List, Optional, Tuple, Union
import functools

from .device import SerialDevice, check_initialized, check_serial


def check_axis_num(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        # could be a kwarg or arg
        if 'axis_number' in kwargs:
            axis_number = kwargs['axis_number']
        else:
            axis_number = args[0]
            
        if not self.is_axis_num_valid(axis_number):
            return (False, "Axis number is not valid or not part of passed tuple during construction.")
        return func(self, *args, **kwargs)
    return wrapper

class NewportESP301(SerialDevice):
    def __init__(
            self, 
            name: str,
            port: str,
            baudrate: int = 921600,
            timeout: Optional[float] = 1.0,
            axis_list: Tuple[int, ...] = (1,),
            #default_speed: float = 10.0,
            default_speed_list: List[float] = [10.0, 10.0, 10.0],
            max_speed_list: List[float] = [100.0, 40.0, 20.0],
            units_list: List[str] = ['millimeter', 'millimeter', 'degree'],
            poll_interval: float = 0.1):

        super().__init__(name, port, baudrate, timeout)
        self._axis_list = axis_list
        #self._default_speed = default_speed #make list
        self._default_speed_list = default_speed_list
        self._poll_interval = poll_interval
        #self._max_speed = 200.0 # make list
        self._max_speed_list = max_speed_list
        self._units_list = units_list

    # @property
    # def default_speed(self) -> float:
    #     return self._default_speed

    @property
    def default_speed_list(self) -> List[float]:
        return self._default_speed_list
    
    def axis_default_speed(self, axis_number: int = 1) -> float:
        return self._default_speed_list[axis_number-1]

    # @default_speed.setter
    # def default_speed(self, speed: float):
    #     if speed > 0.0 and speed < self._max_speed:
    #         self._default_speed = speed

    def set_axis_default_speed(self, axis_number: int = 1, speed: float = 10.0) -> Tuple[bool, str]:
        if axis_number not in self._axis_list:
            return (False, "Invalid axis number")
        if speed <= 0.0 or speed > self._max_speed_list[axis_number-1]:
            return (False, "Speed is out of bounds.")
        else:
            self._default_speed_list[axis_number-1] = speed
            return (True, "Successfully set default speed for axis " + str(axis_number) + " to " + str(speed) + " " + self._units_list[axis_number-1] + "s/s.")


    # check_error already has serial check
    # easier to just set is_intialized False at the very beginning
    # do for all receivers
    def initialize(self) -> Tuple[bool, str]:
        # if not self.ser.is_open:
        #     return (False, "Serial port " + self._port + " is not open. ")

        unit_mappings = {
                    'encoder count': '0', 
                    'motor step': '1',
                    'millimeter': '2',
                    'micrometer': '3',
                    'inches': '4',
                    'milli-inches': '5', 
                    'micro-inches': '6',
                    'degree': '7',
                    'gradian': '8',
                    'radian': '9',
                    'milliradian': '10',
                    'microradian': '11',
                }

        was_successful, message = self.check_error() # just used to flush error and serial input buffer if there is an error
        if not was_successful:
            return (was_successful, message)

        self.ser.reset_input_buffer() # flush the serial input buffer even if there was no error

        for axis in self._axis_list:
            # Make sure axis motor is turned on
            was_turned_on, message = self.axis_on(axis)
            if not was_turned_on:
                self._is_initialized = False
                return (was_turned_on, message)
            # set units to mm, homing value to 0, set max speed, set current speed 
            #command = str(axis) + "SN2;" + str(axis) + "SH0;" + str(axis) + "VU" + str(self._max_speed) + ";" + str(axis) + "VA" + str(self.default_speed) + "\r"
            unit = unit_mappings[self._units_list[axis-1]]
            max_speed = str(self._max_speed_list[axis-1])
            default_speed = str(self._default_speed_list[axis-1])
            command = str(axis) + "SN" + unit + ";" + str(axis) + "SH0;" + str(axis) + "VU" + max_speed + ";" + str(axis) + "VA" + default_speed + "\r"
            self.ser.write(command.encode('ascii'))

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
            was_zeroed, message = self.move_speed_absolute(0.0, speed=None, axis_number=axis) ###
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
            speed = self._default_speed_list[axis_number-1]
            #speed = self._default_speed

        # ensure speed is within bounds
        if speed <= 0.0 or speed > self._max_speed_list[axis_number-1]:
            return (False, "Speed is out of bounds.")

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
            speed = self._default_speed_list[axis_number-1]
            #speed = self._default_speed

        # ensure speed is within bounds
        if speed <= 0.0 or speed > self._max_speed_list[axis_number-1]:
            return (False, "Speed is out of bounds.")

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
        

    def is_axis_num_valid(self, axis_number: int) -> bool:
        if axis_number in self._axis_list:
            return True
        else:
            return False
    

    @check_serial
    @check_initialized
    @check_axis_num
    def change_axis_unit(self, axis_number: int = 1, unit: str = 'millimeter') -> Tuple[bool, str]:
        unit_mappings = {
                    'encoder count': '0', 
                    'motor step': '1',
                    'millimeter': '2',
                    'micrometer': '3',
                    'inches': '4',
                    'milli-inches': '5', 
                    'micro-inches': '6',
                    'degree': '7',
                    'gradian': '8',
                    'radian': '9',
                    'milliradian': '10',
                    'microradian': '11',
                }
        
        if unit.lower() not in unit_mappings:
            return (False, unit + " is not a valid unit type.")
        
        unit_num = unit_mappings[unit.lower()]

        # check if axis is already set to the specified unit
        was_successful, message = self.get_axis_unit(axis_number)
        if not was_successful:
            return (was_successful, message)
        
        if message == unit:
            return (True, 'Axis ' + str(axis_number) + ' was already set to unit: "' + unit +'"')

        command = str(axis_number) + "SN" + str(unit_num) + "\r"
        self.ser.write(command.encode('ascii'))

        was_successful, message = self.check_error()
        if not was_successful:
            return (was_successful, message)
        else:
            self._units_list[axis_number-1] = unit
            return (True, "Successfully set axis " + str(axis_number) + " unit to " + unit + ".")
    
    @check_serial
    @check_initialized
    @check_axis_num
    def change_axis_to_degrees(self, axis_number: int = 1) -> Tuple[bool, str]:
        return self.change_axis_unit(axis_number, 'degree')
    
    @check_serial
    @check_initialized
    @check_axis_num
    def change_axis_to_millimeters(self, axis_number: int = 1) -> Tuple[bool, str]:
        return self.change_axis_unit(axis_number, 'millimeter')
    
    @check_serial
    @check_initialized
    @check_axis_num
    def get_axis_unit(self, axis_number: int = 1) -> Tuple[bool, str]:
        unit_mappings = {
                    '0' : 'encoder count', 
                    '1' : 'motor step',
                    '2' : 'millimeter',
                    '3' : 'micrometer',
                    '4' : 'inches',
                    '5' : 'milli-inches', 
                    '6' : 'micro-inches',
                    '7' : 'degree',
                    '8' : 'gradian',
                    '9' : 'radian',
                    '10' : 'milliradian',
                    '11' : 'microradian',
                }

        command = str(axis_number) + "SN?"
        self.ser.write(command.encode('ascii'))

        response = self.ser.readline().strip().decode('ascii')

        was_successful, message = self.check_error()
        if not was_successful:
            return (was_successful, message)
        return (True, unit_mappings[response])



    # check axis num
    @check_serial
    @check_axis_num
    def is_moving(self, axis_number: int = 1) -> bool:
        # if not self.ser.is_open:
        #     return False
        # else:
        command = str(axis_number) + "MD?\r"
        self.ser.write(command.encode('ascii'))
        response = self.ser.readline()

        if response.strip().decode('ascii') == '0':
            # motion is not done = is moving
            return True
        else:
            # includes timeout case
            return False

    def is_any_moving(self) -> bool:
        is_moving_list = []
        for ndx, axis_number in enumerate(self._axis_list):
            command = str(axis_number) + "MD?\r"
            self.ser.write(command.encode('ascii'))
            response = self.ser.readline()

            if response.strip().decode('ascii') == '0':
                is_moving_list.append(True)
            else:
                is_moving_list.append(False)

        if any(is_moving_list):
            return True
        else: 
            return False

    @check_serial
    def check_error(self) -> Tuple[bool, str]:
        # not needed for queries, but use when instructing to do something
        
        # if not self.ser.is_open:
        #     return (False, "Serial port " + self._port + " is not open. ")

        command = "TB?\r"
        self.ser.write(command.encode('ascii'))
        response = self.ser.readline()

        if response == b'':
            return (False, "Response timed out.")
        
        response = response.strip().decode('ascii')

        if response[0] == '0':
            return (True, "No errors.")
        else:
            # flush the error buffer
            for n in range(10):
                self.ser.write(command.encode('ascii'))
                self.ser.readline()
            # flush the serial input buffer
            time.sleep(0.1)
            self.ser.reset_input_buffer()
            return (False, response)
    
    @check_serial
    @check_axis_num
    def position(self, axis_number: int = 1) -> Tuple[bool, Union[str, float]]:
        # if not self.ser.is_open:
        #     return (False, "Serial port " + self._port + " is not open. ")
        # if not self.is_axis_num_valid(axis_number):
        #     return (False, "Axis number is not valid or not part of passed tuple during construction.")

        command = str(axis_number) + "TP\r"
        self.ser.write(command.encode('ascii'))
        position_str = self.ser.readline()
        if position_str == b'':
            return (False, "Response timed out.")
        else:    
            return (True, float(position_str.strip().decode('ascii')))

    @check_serial
    @check_axis_num
    def axis_on(self, axis_number: int = 1) -> Tuple[bool, str]:
        # if not self.ser.is_open:
        #     return (False, "Serial port " + self._port + " is not open. ")
        # if not self.is_axis_num_valid(axis_number):
        #     return (False, "Axis number is not valid or not part of passed tuple during construction.")

        command = str(axis_number) + "MO\r"
        self.ser.write(command.encode('ascii'))

        was_successful, message = self.check_error()
        if not was_successful:
            return (was_successful, message)

        command = str(axis_number) + "MO?\r"
        self.ser.write(command.encode('ascii'))
        response = self.ser.readline()

        if response.strip().decode('ascii') == '1':
            return (True, "Axis " + str(axis_number) + " motor successfully turned ON.")
        else:
            # also means timeout
            return (False, "Axis " + str(axis_number) + " motor failed to turned ON.")

    @check_serial
    @check_axis_num
    def axis_off(self, axis_number: int = 1) -> Tuple[bool, str]:
        # if not self.ser.is_open:
        #     return (False, "Serial port " + self._port + " is not open. ")
        # if not self.is_axis_num_valid(axis_number):
        #     return (False, "Axis number is not valid or not part of passed tuple during construction.")

        command = str(axis_number) + "MF\r"
        self.ser.write(command.encode('ascii'))

        was_successful, message = self.check_error()
        if not was_successful:
            return (was_successful, message)

        command = str(axis_number) + "MF?\r"
        self.ser.write(command.encode('ascii'))
        response = self.ser.readline()

        if response.strip().decode('ascii') == '0':
            return (True, "Axis " + str(axis_number) + " motor successfully turned OFF.")
        else:
            # also means timeout
            return (False, "Axis " + str(axis_number) + " motor failed to turned OFF.")