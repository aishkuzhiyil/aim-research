from .command import Command, CommandResult, CompositeCommand
from devices.ika_cmag import IKAStirrer
from typing import Optional

class IkaStirrerParentCommand(Command):
    """Parent class for all IKAStirrer commands."""
    receiver_cls = IKAStirrer

    def __init__(self, receiver: IKAStirrer, **kwargs):
        super().__init__(receiver, **kwargs)

class IkaStirrerConnect(IkaStirrerParentCommand):
    """Open the serial port to the IKAStirrer."""

    def __init__(self, receiver: IKAStirrer, **kwargs):
        super().__init__(receiver, **kwargs)

    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.start_serial())

class IkaStirrerInitialize(IkaStirrerParentCommand):
    """Initializes the device"""
    
    def __init__(self, receiver: IKAStirrer, **kwargs):
        super().__init__(receiver, **kwargs)

    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.initialize())

class IkaStirrerDeinitialize(IkaStirrerParentCommand):
    """Deinitializes the device"""
    
    def __init__(self, receiver: IKAStirrer, **kwargs):
        super().__init__(receiver, **kwargs)

    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.deinitialize())

class IkaStirrerSetDefaultTemperature(IkaStirrerParentCommand):
    """Sets the default temperature"""

    def __init__(self, receiver: IKAStirrer, temp: Optional[float] = None, **kwargs):
        super().__init__(receiver, **kwargs)
        self._params['temp'] = temp

    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.set_default_temp(self._params['temp']))  


class IkaStirrerSetDefaultStirRate(IkaStirrerParentCommand):
    """Sets the default temperature"""
    
    def __init__(self, receiver: IKAStirrer,  rate: Optional[float] = None, **kwargs):
        super().__init__(receiver, **kwargs)
        self._params['rate'] = rate
    
    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.set_default_stir_rate(self._params['rate']))  

    

class IkaStirrerChangeTemperature(IkaStirrerParentCommand):
    """Sets the temperature to the given temperature but defaults to default temperature if none is givn."""
    
    def __init__(self, receiver: IKAStirrer, temp: Optional[float] = None, **kwargs):
        super().__init__(receiver, **kwargs)
        self._params['temp'] = temp
    
    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.change_temp(self._params['temp']))  

class IkaStirrerChangeStirRate(IkaStirrerParentCommand):
    """Sets the stir rate to given stir rate but defaults to default stir rate if none is give"""
    
    def __init__(self, receiver: IKAStirrer,  rate: Optional[float] = None, **kwargs):
        super().__init__(receiver, **kwargs)
        self._params['rate'] = rate
    
    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.change_stir_rate(self._params['rate']))  

class IkaStirrerStopStirring(IkaStirrerParentCommand):
    """Stops the stirring"""
    
    def __init__(self, receiver: IKAStirrer, **kwargs):
        super().__init__(receiver, **kwargs)

    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.stop_stirring())

class IkaStirrerStopHeating(IkaStirrerParentCommand):
    """Stops the heating"""
    
    def __init__(self, receiver: IKAStirrer, **kwargs):
        super().__init__(receiver, **kwargs)

    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.stop_heating())  



