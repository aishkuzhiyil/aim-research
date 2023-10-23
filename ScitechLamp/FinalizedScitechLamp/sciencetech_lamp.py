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
            timeout: Optional[float] = 1.0,
            attenuator: int = 100,
            current: float = 85):
            
        super().__init__(name, port, baudrate, timeout)
        self._attenuator = attenuator
        self._current = current


    
    def initialize(self) -> Tuple[bool, str]:
        if not self.ser.is_open:
            return (False, "Serial port " + self.port + " is not open. ")

        # turns cooling on
        was_successful, message = self.enable_cooling()
        if not was_successful:
            return (False, message)

        # opens attenuator to 100%
        was_successful, message = self.open_attenuator()
        self._attenuator = 100
        if not was_successful:
            return (False, message)
        
        # sets current to default val (85%)
        self._current = 85
        was_successful, message = self.set_current(self._current)
        if not was_successful:
            return (False, message)

        return (True, "Successfully initialized the device")
    

    def deinitialize(self)-> Tuple[bool, str]:
        if not self.ser.is_open:
            return (False, "Serial port " + self.port + " is not open. ")
        
        return (True, "Successfully deinitialized the device")
    
    # this is the same as enabling the shutter
    def close_shutter(self) -> Tuple[bool,str]: 

        # checks if shutter was already closed
        was_successful, message = self.get_feedback('shutter')
        if not was_successful:
            return (False, message) # error message would be "Invalid Type"

        bit = int(message[-1:])
        if (bit == 1):
            return (True, "Shutter was already closed (enabled).")

        # enables shutter
        command = 'S1\r'
        self.ser.write(command.encode('ascii'))

        time.sleep(5)

        #checks if command has been executed properly
        was_successful, message = self.get_feedback('shutter')

        if not was_successful:
            return (False, message) # error message would be "Invalid Type"
        
        bit = int(message[-1:])

        if (bit == 1):
            return (True, "Successfully closed (enabled) the shutter.")
        return (False, "Failed to close (enable) the shutter.")

    # same as disabling shutter
    def open_shutter(self) -> Tuple[bool, str]:

        # checks if shutter was already open
        was_successful, message = self.get_feedback('shutter')
        if not was_successful:
            return (False, message) # error message would be "Invalid Type"
        
        bit = int(message[-1:])
        if (bit == 0):
            return (True, "Shutter was already open (disabled).")
        
        # disables shutter
        command = 'S0\r'
        self.ser.write(command.encode('ascii'))

        time.sleep(5)

        #checks if command has been executed properly
        was_successful, message = self.get_feedback('shutter')
        if not was_successful:
            return (False, message) # error message would be "Invalid Type"
        
        bit = int(message[-1:])
        if (bit == 0):
            return (True, "Successfully opened (disabled) the shutter.")
        return (False, "Failed to open (disable) the shutter.")


    def enable_cooling(self) -> Tuple[bool, str]:
        # checks if cooling was already enabled
        was_successful, message = self.get_feedback('cool')
        if not was_successful:
            return (False, message) # error message would be "Invalid Type"
        
        bit = int(message[-1:])
        if (bit == 1):
            return (True, "Cooling was already on.")
        
        # enables cooling
        command = 'C1\r'
        self.ser.write(command.encode('ascii'))

        time.sleep(5)


        #checks if command has been executed properly
        was_successful, message = self.get_feedback('cool')
        if not was_successful:
            return (False, message) # error message would be "Invalid Type"
        
        bit = int(message[-1:])
        if (bit == 1):
            return (True, "Successfully enabled cooling.")
        return (False, "Failed to enable cooling")

    def disable_cooling(self) -> Tuple[bool, str]:
        # checks if cooling was already disabled
        was_successful, message = self.get_feedback('cool')
        if not was_successful:
            return (False, message) # error message would be "Invalid Type"
        
        bit = int(message[-1:])
        if (bit == 0):
            return (True, "Cooling was already disabled")
        
        # disables shutter
        command = 'C0\r'
        self.ser.write(command.encode('ascii'))

        time.sleep(5)

        #checks if command has been executed properly
        was_successful, message = self.get_feedback('cool')
        if not was_successful:
            return (False, message) # error message would be "Invalid Type"
        
        bit = int(message[-1:])
        if (bit == 0):
            return (True, "Successfully disabled cooling.")
        return (False, "Failed to disable cooling.")

    def enable_arc_lamp(self) -> Tuple[bool, str]:
        # checks if arc lamp was already enabled
        was_successful, message = self.get_feedback('lamp')
        if not was_successful:
            return (False, message) # error message would be "Invalid Type"
        
        bit = int(message[-1:])
        if (bit == 1):
            return (True, "Arc lamp was already enabled.")
        
        # enables lamp
        command = 'L1\r'
        self.ser.write(command.encode('ascii'))

        time.sleep(5)

        #checks if command has been executed properly
        was_successful, message = self.get_feedback('lamp')
        if not was_successful:
            return (False, message) # error message would be "Invalid Type"
        
        bit = int(message[-1:])
        if (bit == 1):
            return (True, "Successfully enabled arc lamp.")
        return (False, "Failed to enable arc lamp")


    def disable_arc_lamp(self) -> Tuple[bool, str]:
        # checks if arc lamp was already disabled
        was_successful, message = self.get_feedback('lamp')
        if not was_successful:
            return (False, message) # error message would be "Invalid Type"
        
        bit = int(message[-1:])
        if (bit == 0):
            return (True, "Arc lamp was already disabled.")
        
        # disable lamp
        command = 'L0\r'
        self.ser.write(command.encode('ascii'))
        time.sleep(5)

        #checks if command has been executed properly
        was_successful, message = self.get_feedback('lamp')
        if not was_successful:
            return (False, message) # error message would be "Invalid Type"
        
        bit = int(message[-1:])
        if (bit == 0):
            return (True, "Successfully disabled arc lamp.")
        return (False, "Failed to disable arc lamp")

    def open_attenuator(self) -> Tuple[bool, str]:
        # opens attenuator to max opening
        command = 'A1xxxx\r'
        self.ser.write(command.encode('ascii'))
        time.sleep(5)

        #checks if command has been executed properly
        was_successful, message = self.get_feedback('attenuator')
        if not was_successful:
            return (False, message) # error message would be "Invalid Type"
        
        percent_read = int(message[-3:0])
        if percent_read == 100:
            self._attenuator = 100
            return (True, "Successfully opened attenuator to max opening")
        return (False, "Failed to open attenuator to max opening")

    # should percentage
    def set_attenuator(self, percent: int) -> Tuple[bool, str]:
        # checks if percent is a valid percentage
        if (percent > 100 or percent < 0):
            return (False, 'Invalid percentage')
        
        # sets transmission percentage
        if (percent == 100):
            command = 'A=100x\r'
        elif percent < 10:
            command = 'A=00' + str(percent) + 'x\r'
        else:
            command = 'A=0' + str(percent) + 'x\r'
        self.ser.write(command.encode('ascii'))

        time.sleep(5)

        #checks if command has been executed properly
        was_successful, message = self.get_feedback('attenuator')
        if not was_successful:
            return (False, message) # error message would be "Invalid Type"
        
        percent_read = int(message[-3:0])
        if percent_read == percent:
            self._attenuator = percent
            return (True, "Successfully set attenuator transmission percentage to " + str(percent) + ' percent')
        return (True, "Failed to set attenuator transmission percentage to " + str(percent) + ' percent')


    # float?
    def set_current(self, percent: float) -> Tuple[bool, str]:
        # checks if percent is a valid percentage
        if (percent > 100 or percent < 0):
            return (False, 'Invalid percentage')
        
        # sets current percentage
        command = ''
        if (percent == 100):
            command = 'P=1000\r'
        elif percent == 0:
            command = 'P=0000\r'
        elif percent < 10:
            scaled = (int) (percent * 10)
            command = 'P=00' + str(scaled) + '\r'
        else:
            scaled = (int) (percent * 10)
            command = 'P=0' + str(scaled) + '\r'
        self.ser.write(command.encode('ascii'))
        time.sleep(5)

        #checks if command has been executed properly
        was_successful, message = self.get_feedback('current')
        if not was_successful:
            return (False, message) # error message would be "Invalid Type"
        
        percent_read = float(message[-5:])/10

        if percent_read - percent <= 0.2:
            return (True, "Successfully set output current percentage to " + str(percent) + ' percent')
        return (False, "Failed to set output current percentage to " + str(percent) + ' percent')

    def get_status(self) :
        self.ser.reset_input_buffer()  # flush the serial input buffer
        command = 'FS\r'
        self.ser.write(command.encode('ascii'))
        answer = []
        line = None
        while True:
            line = self.ser.readline().decode('ascii').strip()
            if line == 'END':
                break
            answer.append(line)
        return answer
    
    def get_feedback(self, type: str) -> Tuple[bool, str]:
        mappings = {
                    'current': 3, 
                    'voltage': 4,
                    'power': 5,
                    'po': 6,
                    'cool': 7,
                    'lamp': 8, 
                    'starts': 9,
                    'runtime': 10,
                    'output': 11,
                    'hours': 12,
                    'lamp minutes': 13,
                    'shutter': 14,
                    'attenuator': 15,
                }
        type_lower = type.lower()
        if type_lower not in mappings:
            return (False, "Invalid type")
        
        answer = self.get_status()
        return (True, answer[mappings[type_lower]])

        