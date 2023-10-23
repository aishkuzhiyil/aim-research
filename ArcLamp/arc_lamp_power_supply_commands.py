from .command import Command, CommandResult, CompositeCommand
from devices.py import ArcLampPowerSupply
from typing import Optional

class ArcLampPowerSupplyParentCommand(Command):
    """Parent class for all ArcLampPowerSupply commands."""
    receiver_cls = ArcLampPowerSupply

    def __init__(self, receiver: ArcLampPowerSupply, **kwargs):
        super().__init__(receiver, **kwargs)

class ArcLampPowerSupplyConnect(ArcLampPowerSupplyParentCommand):
    """Open the serial port to the Arc Lamp Power Supply."""

    def __init__(self, receiver: ArcLampPowerSupply, **kwargs):
        super().__init__(receiver, **kwargs)

    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.start_serial())

class ArcLampPowerSupplyInitialize(ArcLampPowerSupplyParentCommand):
    """Initializes the device by turning it on and setting to power mode"""
    
    def __init__(self, receiver: ArcLampPowerSupply, **kwargs):
        super().__init__(receiver, **kwargs)

    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.initialize())

class ArcLampPowerSupplyDeinitialize(ArcLampPowerSupplyParentCommand):
    """Deinitializes the device by turning it off"""
    
    def __init__(self, receiver: ArcLampPowerSupply, reset_init_flag: bool = True, **kwargs):
        super().__init__(receiver, **kwargs)
        self._params['reset_init_flag'] = reset_init_flag

    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.deinitialize())

class ArcLampPowerSupplyDefaultLimit(ArcLampPowerSupplyParentCommand):
    def __init__(self, receiver: ArcLampPowerSupply, default_limit: float, **kwargs):
        super().__init__(receiver, **kwargs)
        self._params['default_limit'] = default_limit

    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.default_limit(self._params[default_limit]))


class ArcLampPowerSupplyTurnOn(ArcLampPowerSupplyParentCommand):
    def __init__(self, receiver: ArcLampPowerSupply, **kwargs):
        super().__init__(receiver, **kwargs)

    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.turn_on())  

class ArcLampPowerSupplyTurnOff(ArcLampPowerSupplyParentCommand):
    def __init__(self, receiver: ArcLampPowerSupply, **kwargs):
        super().__init__(receiver, **kwargs)

    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.turn_on())  




