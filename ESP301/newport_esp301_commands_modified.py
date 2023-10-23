from .command import Command, CommandResult, CompositeCommand
from devices.newport_esp301 import NewportESP301
from typing import Optional

# Parent class, subclass from Command ABC
class NewportESP301ParentCommand(Command):
    """Parent class for all NewportESP301 commands."""
    receiver_cls = NewportESP301

    def __init__(self, receiver: NewportESP301, **kwargs):
        super().__init__(receiver, **kwargs)

# Recommended command classes
class NewportESP301Connect(NewportESP301ParentCommand):
    """Open the serial port to the ESP301 controller."""

    def __init__(self, receiver: NewportESP301, **kwargs):
        super().__init__(receiver, **kwargs)

    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.start_serial())

class NewportESP301Initialize(NewportESP301ParentCommand):
    """Initialize the axes by homing them."""
    
    def __init__(self, receiver: NewportESP301, **kwargs):
        super().__init__(receiver, **kwargs)

    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.initialize())

class NewportESP301Deinitialize(NewportESP301ParentCommand):
    """Deinitialize the axes by moving them to position zero."""
    
    def __init__(self, receiver: NewportESP301, reset_init_flag: bool = True, **kwargs):
        super().__init__(receiver, **kwargs)
        self._params['reset_init_flag'] = reset_init_flag

    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.deinitialize(self._params['reset_init_flag']))

# Device-related commands classes
class NewportESP301MoveSpeedAbsolute(NewportESP301ParentCommand):
    """Move axis to absolute position at specific speed (No speed uses default speed)."""
    
    def __init__(self, receiver: NewportESP301, axis_number: int = 1, position: Optional[float] = None, speed: Optional[float] = None, **kwargs):
        super().__init__(receiver, **kwargs)
        self._params['position'] = position
        self._params['speed'] = speed
        self._params['axis_number'] = axis_number
    
    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.move_speed_absolute(self._params['axis_number'], self._params['position'], self._params['speed']))

class NewportESP301MoveSpeedRelative(NewportESP301ParentCommand):
    """Move axis by relative distance at specific speed (No speed uses default speed)."""
    
    def __init__(self, receiver: NewportESP301, axis_number: int = 1, distance: Optional[float] = None, speed: Optional[float] = None, **kwargs):
        super().__init__(receiver, **kwargs)
        self._params['distance'] = distance
        self._params['speed'] = speed
        self._params['axis_number'] = axis_number
    
    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.move_speed_relative(self._params['axis_number'], self._params['distance'], self._params['speed']))

# # Example of command with additional logic to determine the returned tuple of (success/fail: bool, success/fail message: str)
# class NewportESP301SetDefaultSpeed(NewportESP301ParentCommand):
#     """Set the default speed of the axes."""
    
#     def __init__(self, receiver: NewportESP301, speed: float, **kwargs):
#         super().__init__(receiver, **kwargs)
#         self._params['speed'] = speed

#     def execute(self) -> None:
#         self._receiver.default_speed = self._params['speed']
#         # receiver's default_speed has a setter than checks the value is > 0 and < max_speed before setting
#         # therefore, we can check if we actually changed the receiver's default speed, if not, it means the speed was out of range
#         if self._receiver.default_speed == self._params['speed']:
#             self._result = CommandResult(True, "Default speed successfully set to " + str(self._params['speed']))
#         else:
#             self._result = CommandResult(False, "Failed to set the default speed to " + str(self._params['speed']) + ". The default speed must be > 0 and < " + str(self._receiver._max_speed))

class NewportESP301SetAxisDefaultSpeed(NewportESP301ParentCommand):
    """Set the default speed of the axes."""
    
    def __init__(self, receiver: NewportESP301, speed: float, axis_number: int = 1, **kwargs):
        super().__init__(receiver, **kwargs)
        self._params['axis_number'] = axis_number
        self._params['speed'] = speed

    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.set_axis_default_speed(self._params['axis_number'], self._params['speed']))

class NewportESP301ChangeAxisUnit(NewportESP301ParentCommand):
    """Change a specific axis' unit"""
    
    def __init__(self, receiver: NewportESP301, axis_number: int = 1, unit: str = 'millimeter', **kwargs):
        super().__init__(receiver, **kwargs)
        self._params['axis_number'] = axis_number
        self._params['unit'] = unit

    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.change_axis_unit(self._params['axis_number'], self._params['unit']))

class NewportESP301ChangeAxisToDegrees(NewportESP301ParentCommand):
    """Change a specific axis' unit to degrees"""
    
    def __init__(self, receiver: NewportESP301, axis_number: int = 1, **kwargs):
        super().__init__(receiver, **kwargs)
        self._params['axis_number'] = axis_number

    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.change_axis_to_degrees(self._params['axis_number']))

class NewportESP301ChangeAxisToMillimeters(NewportESP301ParentCommand):
    """Change a specific axis' unit to millimeters"""
    
    def __init__(self, receiver: NewportESP301, axis_number: int = 1, **kwargs):
        super().__init__(receiver, **kwargs)
        self._params['axis_number'] = axis_number

    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.change_axis_to_millimeters(self._params['axis_number']))

class NewportESP301GetAxisUnit(NewportESP301ParentCommand):
    """Get a specific axis' unit type"""
    
    def __init__(self, receiver: NewportESP301, axis_number: int = 1, **kwargs):
        super().__init__(receiver, **kwargs)
        self._params['axis_number'] = axis_number

    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.get_axis_unit(self._params['axis_number']))

# Derived commands
class NewportESP301HorzMoveSpeedAbsolute(NewportESP301MoveSpeedAbsolute):
    """desc"""
    
    # position no longer can be None here because we dont need axis num in sig
    def __init__(self, receiver: NewportESP301, position: float, speed: Optional[float] = None, **kwargs):
        super().__init__(receiver, 1, position, speed, **kwargs)

# Just for testing composite commands
class NewportESP301Dance(CompositeCommand):
    def __init__(self, receiver, speed, distance, **kwargs):
        super().__init__(**kwargs)
        self.add_command(NewportESP301MoveSpeedRelative(receiver, -distance, speed))
        self.add_command(NewportESP301MoveSpeedRelative(receiver, distance, speed))