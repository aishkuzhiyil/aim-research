import time
from typing import List, Optional, Tuple, Union
import functools

from .device import SerialDevice # change the from
from ika.magnetic_stirrer import MagneticStirrer # change the from

class IKAStirrer(SerialDevice):
    def __init__(
            self, 
            name: str,
            port: str,
            baudrate: int = 9600,
            timeout: Optional[float] = 1.0,
            default_temp: float = 50.0, # in celsius
            default_stir_rate: float = 200.0): # rpm

        super().__init__(name, port, baudrate, timeout)
        self.default_temp_ = default_temp
        self.default_stir_rate_ = default_stir_rate
        self.plate_ = MagneticStirrer(device_port = port)

    def initialize(self) -> Tuple[bool, str]:
        self.plate_.connect()

        '''
        This is how they started stirring/heating in the example code provided in the library.
        However, I traced the code and I can't seem to find where and how they use target values as a sort of limit
        '''
        self.plate_.start_stirring()
        self.plate_.target_stir_rate = self.default_stir_rate_
        time.sleep(10)

        self.plate_.target_temperature = 20
        self.plate_.start_heating()
        self.plate_.target_temperature = self.default_temp_

        return [True, 'Successfully initialized hot plate']
    
    def deinitialize(self) -> Tuple[bool, str]:
        self.stop_heating()
        self.stop_stirring()
        self.plate_.disconnect()

        return [True, 'Successfully deinitialized hot plate']

    def set_default_temp(self, temp: float) -> Tuple[bool, str]:
        if temp < 0 or temp > 500:
            return [False, "Invalid temperature"]
        self.default_temp_ = temp
        return [True, "Succesfully set default temperatre to " + str(temp)]
    
    def set_default_stir_rate(self, rate: float) -> Tuple[bool, str]:
        if rate < 50 or rate > 1500:
            return [False, "Invalid stir rate"]
        self.default_stir_rate_ = rate
        return [True, "Succesfully set default temperatre to " + str(rate)]
    
    def change_temp(self, temp:  Optional[float] = None) -> Tuple[bool, str]:
        if temp is None:
            temp = self.default_temp_
        if temp < 0 or temp > 500:
            return [False, "Invalid temperature"] 
        
        self.plate_.start_heating()
        self.plate_.target_temperature = temp
        time.sleep(10)

        if self.plate_.read_actual_hotplate_sensor_value() == temp:
            return [True, "Succesfully set temperature to " + str(temp)]
        return [False, 'Failed to set temperature to ' + str(temp)]
    
    def change_stir_rate(self, rate:  Optional[float] = None) -> Tuple[bool, str]:
        if rate is None:
            rate = self.default_stir_rate_
        if rate < 50 or rate > 1500:
            return [False, "Invalid stir rate"] 
        
        self.plate_.start_stirring()
        self.plate_.target_stir_rate = rate
        time.sleep(10)

        if self.plate_.read_stirring_speed_value() == rate:
            return [True, "Succesfully set stir rate to " + str(rate)]
        return [False, 'Failed to set stir rate to ' + str(rate)]
    
    def stop_stirring(self) -> Tuple[bool, str]:
        self.plate_.stop_stirring()
        return [True, "Sucessfully stopped stirring"]

    def stop_heating(self):
        self.plate_.stop_heating()
        return [True, "Sucessfully stopped heating"]


    

