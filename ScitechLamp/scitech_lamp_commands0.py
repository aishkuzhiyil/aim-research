from .command import Command, CommandResult, CompositeCommand
from devices.py import ScitechLamp
from typing import Optional

class ScitechLampParentCommand(Command):
    """Parent class for all ArcLampPowerSupply commands."""
    receiver_cls = ScitechLamp

    def __init__(self, receiver: ScitechLamp, **kwargs):
        super().__init__(receiver, **kwargs)

class ScitechLampConnect(ScitechLampParentCommand):
    """Open the serial port to the Arc Lamp Power Supply."""

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
    def __init__(self, receiver: ScitechLamp, **kwargs):
        super().__init__(receiver, **kwargs)

    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.enable_shutter())  

class ScitechLampOpenShutter(ScitechLampParentCommand):
    def __init__(self, receiver: ScitechLamp, **kwargs):
        super().__init__(receiver, **kwargs)

    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.disable_shutter())  


class ScitechLampEnableCooling(ScitechLampParentCommand):
    def __init__(self, receiver: ScitechLamp, **kwargs):
        super().__init__(receiver, **kwargs)

    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.enable_cooling())  

class ScitechLampDisableCooling(ScitechLampParentCommand):
    def __init__(self, receiver: ScitechLamp, **kwargs):
        super().__init__(receiver, **kwargs)

    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.disable_cooling())  

class ScitechLampEnableArcLamp(ScitechLampParentCommand):
    def __init__(self, receiver: ScitechLamp, **kwargs):
        super().__init__(receiver, **kwargs)

    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.enable_arc_lamp())  

class ScitechLampDisableArcLamp(ScitechLampParentCommand):
    def __init__(self, receiver: ScitechLamp, **kwargs):
        super().__init__(receiver, **kwargs)

    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.disable_arc_lamp())  


class ScitechLampOpenAttenuator(ScitechLampParentCommand):
    def __init__(self, receiver: ScitechLamp, **kwargs):
        super().__init__(receiver, **kwargs)

    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.open_attenuator())  

class ScitechLampSetAttenuator(ScitechLampParentCommand):
    def __init__(self, receiver: ScitechLamp, percent: int = 100, **kwargs):
        super().__init__(receiver, **kwargs)
        self._params['percent'] = percent

    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.set_attenuator(self._params['percent']))  

class ScitechLampSetCurrent(ScitechLampParentCommand):
    def __init__(self, receiver: ScitechLamp, percent: int = 100, **kwargs):
        super().__init__(receiver, **kwargs)
        self._params['percent'] = percent

    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.set_current(self._params['percent']))  

class ScitechLampGetFeedback(ScitechLampParentCommand):
    def __init__(self, receiver: ScitechLamp, **kwargs):
        super().__init__(receiver, **kwargs)

    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.get_feedback())  