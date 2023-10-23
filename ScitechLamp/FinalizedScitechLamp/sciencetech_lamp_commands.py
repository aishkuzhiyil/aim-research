from .command import Command, CommandResult, CompositeCommand
from devices.scitech_lamp import ScitechLamp
from typing import Optional

class ScitechLampParentCommand(Command):
    """Parent class for all ScitechLamp commands."""
    receiver_cls = ScitechLamp

    def __init__(self, receiver: ScitechLamp, **kwargs):
        super().__init__(receiver, **kwargs)

class ScitechLampConnect(ScitechLampParentCommand):
    """Open the serial port to the ScitechLamp."""

    def __init__(self, receiver: ScitechLamp, **kwargs):
        super().__init__(receiver, **kwargs)

    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.start_serial())

class ScitechLampInitialize(ScitechLampParentCommand):
    """Initializes the device"""
    
    def __init__(self, receiver: ScitechLamp, **kwargs):
        super().__init__(receiver, **kwargs)

    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.initialize())

class ScitechLampDeinitialize(ScitechLampParentCommand):
    """Deinitializes the device"""
    
    def __init__(self, receiver: ScitechLamp, reset_init_flag: bool = True, **kwargs):
        super().__init__(receiver, **kwargs)
        self._params['reset_init_flag'] = reset_init_flag

    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.deinitialize())


class ScitechLampCloseShutter(ScitechLampParentCommand):
    """Closes (enables) the shutter"""
    def __init__(self, receiver: ScitechLamp, **kwargs):
        super().__init__(receiver, **kwargs)

    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.close_shutter())  

class ScitechLampOpenShutter(ScitechLampParentCommand):
    """Opens (disables) the shutter"""
    def __init__(self, receiver: ScitechLamp, **kwargs):
        super().__init__(receiver, **kwargs)

    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.open_shutter())  


class ScitechLampEnableCooling(ScitechLampParentCommand):
    """Turns cooling on"""
    def __init__(self, receiver: ScitechLamp, **kwargs):
        super().__init__(receiver, **kwargs)

    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.enable_cooling())  

class ScitechLampDisableCooling(ScitechLampParentCommand):
    """Turns cooling off"""
    def __init__(self, receiver: ScitechLamp, **kwargs):
        super().__init__(receiver, **kwargs)

    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.disable_cooling())  

class ScitechLampEnableArcLamp(ScitechLampParentCommand):
    """Turns Arc Lamp on"""
    def __init__(self, receiver: ScitechLamp, **kwargs):
        super().__init__(receiver, **kwargs)

    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.enable_arc_lamp())  

class ScitechLampDisableArcLamp(ScitechLampParentCommand):
    """Turns Arc Lamp off"""
    def __init__(self, receiver: ScitechLamp, **kwargs):
        super().__init__(receiver, **kwargs)

    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.disable_arc_lamp())  


class ScitechLampOpenAttenuator(ScitechLampParentCommand):
    """Sets attenuator to max opening"""
    def __init__(self, receiver: ScitechLamp, **kwargs):
        super().__init__(receiver, **kwargs)

    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.open_attenuator())  

class ScitechLampSetAttenuator(ScitechLampParentCommand):
    """Sets attenuator to given percent"""
    def __init__(self, receiver: ScitechLamp, percent: int = 100, **kwargs):
        super().__init__(receiver, **kwargs)
        self._params['percent'] = percent

    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.set_attenuator(self._params['percent']))  

class ScitechLampSetCurrent(ScitechLampParentCommand):
    """Sets current to given percent"""
    def __init__(self, receiver: ScitechLamp, percent: float = 85, **kwargs):
        super().__init__(receiver, **kwargs)
        self._params['percent'] = percent

    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.set_current(self._params['percent']))  

class ScitechLampGetStatus(ScitechLampParentCommand):
    """Gets feedback status"""
    def __init__(self, receiver: ScitechLamp, **kwargs):
        super().__init__(receiver, **kwargs)

    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.get_status())

class ScitechLampGetFeedback(ScitechLampParentCommand):
    """Gets specific feedback status"""
    def __init__(self, receiver: ScitechLamp, type:str, **kwargs):
        super().__init__(receiver, **kwargs)
        self._params['type'] = type

    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.get_feedback(self._params['type']))