import time
from typing import Optional, Tuple, Union
import functools

from .device import SerialDevice, check_initialized, check_serial
# import functools, serial

class ArcLampPowerSupply(SerialDevice):

    # how do i initialize/deinitialize?
        # should i use the decorators?
    # should you be able to switch modes?
        # set limit based on mode?

    def __init__(
            self, 
            name: str,
            port: str,
            baudrate: int = 9600,
            timeout: Optional[float] = 1.0,
            mode: str = "power",
            default_limit: float = 440):
            
        super().__init__(name, port, baudrate, timeout)
        self._mode = mode
        self._default_limit = default_limit

    def initialize(self):
        # ensures port is open
        was_successful, message = self.get_status()
        if not was_successful:
            return (False, message)
        
        # turns off lamp
        was_successful, message = self.turn_off()
        if not was_successful:
            return (False, message)
        
        # sets to power mode
        was_successful, message = self.power_mode()
        if not was_successful:
            return (False, message)
        
        #checks any errors
        was_successful, message = self.check_error()
        if not was_successful:
            return (False, message)
        
        return (True, "Successfully initialized the device")
    

    def deinitialize(self):
        was_successful, message = self.get_status()
        if not was_successful:
            return (False, message)
    
        was_successful, message - self.turn_off()
        if not was_successful:
            return (False, message)
        
        return (True, "Successfully deinitialized the device")
    
    def default_limit(self) -> float:
        return self._default_limit

    def power_mode(self) -> Tuple[bool, str]:
        command = 'MODE=0'
        self.ser.write(command.encode('ascii'))

        was_successful, hex_value = self.get_status()
        if not was_successful:
            return (False, hex_value)

        was_successful, message = self.check_error()
        if not was_successful:
            return (False, message)

        if (hex_value >> 5) & 1:
            return (True, "Lamp is on power mode")
    
    
    def default_limit(self, default_limit: float) -> Tuple[bool, str]:
        # checks if limit is valid
        if default_limit >= 320.0 and default_limit <= 440:
            self._default_limit = default_limit
        else:
            return (False, 'Invalid limit')

        hex_string = hex(self._default_limit)
        hex_string = hex_string[2:].zfill(4)
        # need space after '='?
        command = "P-PRESET=" + hex_string
        self.ser.write(command.encode('ascii'))

        # make sure there are no errors
        was_successful, message = self.check_error()
        if not was_successful:
            return (False, message)

        # ensures limit has been successfully set
        was_successful, message = default_limit()
        if not was_successful:
            return (False, message)
    
        if self._power_limit != message:
            return (False, 'Failed to successfully change the power limit')

        return (True, 'Sucessfully set the new default limit to ' + str(default_limit))
        
    def default_limit(self) -> Tuple[bool, Union[str, float]]:
        command = 'P-LIM?'
        self.ser.write(command.encode('ascii'))

        # checks that no errors have occurred
        was_successful, message = self.check_error()
        if not was_successful:
            return (False, message)
        response = self.ser.readline().strip().decode('ascii')

        integer_value = int(response, 16)
        return (True, integer_value)

    def turn_on(self):
        #checks if serial port is open
        was_successful, hex_value = self.get_status()
        if not was_successful:
            return (False, "Serial port " + self.port + " is not open. ")

        # checks if lamp is already on
        if (hex_value >> 7) & 1:
            return (True, "Lamp was already on.")

        # turns on lamp
        command = "START\r"
        self.ser.write(command.encode('ascii'))

        # checks that the lamp is actually on and no errors have occurred
        was_successful, hex_value = self.get_status()
        if not was_successful:
            return (False, "Serial port " + self.port + " is not open. ")

        was_successful, message = self.check_error()
        if not was_successful:
            return (False, message)

        if (hex_value >> 7) & 1:
            return (True, "Lamp successfully turned on")

        return (False, "Failed to successfully turn on lamp")
    
    def turn_off(self):
        # checks if serial port is open
        was_successful, hex_value = self.get_status()
        if not was_successful:
            return (False, "Serial port " + self.port + " is not open. ")

        #checks if lamp is already off
        if (hex_value >> 7) | 0:
            return (True, "Lamp was already off.")

        command = "STOP\r"
        self.ser.write(command.encode('ascii'))

        # checks that lamp is actually off and no errors have occurred 
        was_successful, hex_value = self.get_status()
        if not was_successful:
            return (False, "Serial port " + self.port + " is not open. ")

        was_successful, message = self.check_error()
        if not was_successful:
            return (False, message)

        if (hex_value >> 7) | 0:
            return (True, "Lamp successfully turned off")

        return (False, "Failed to successfully turn off lamp")

    
    def check_error(self) -> Tuple[bool, str]:
        command = "ESR?\r"
        self.ser.write(command.encode('ascii'))
        response = self.ser.readline().strip().decode('ascii')
        hex_string = response[-2:0]
        decimal_value = int(hex_string, 16)
        
        #identifying possible sources of error
        power_on = (decimal_value & 0x80) >> 7
        command_error = (decimal_value & 0x20) >> 5
        execution_error = (decimal_value & 0x10) >> 4
        device_dependent_error = (decimal_value & 0x08) >> 3
        query_error = (decimal_value & 0x04) >> 2


        if (power_on | 0):
            return (False, "Power off")
        
        if (command_error & 1):
            return (False, "Command Error")
        
        if (execution_error & 1):
            return (False, "Execution Error")
        
        if (device_dependent_error & 1):
            return (False, "Device Dependent Error")
        
        if (query_error & 1):
            return (False, "Query Error")
        return (True, "No errors")

    def get_status(self) -> Tuple[bool, Union[str, int]]:
        if not self.ser.is_open:
            return (False, "Serial port " + self.port + " is not open. ")
        command = "STB?\r"
        self.ser.write(command.encode('ascii'))
        response = self.ser.readline().strip().decode('ascii')
        hex_string = response[-2:0]
        hex_int = int(hex_string, 16)
        return (True, hex_int)

