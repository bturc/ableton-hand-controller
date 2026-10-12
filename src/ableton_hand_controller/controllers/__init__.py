"""Controllers map gesture events to actions in Live.

A controller is any callable taking a gestures.GestureEvent.
"""

from .tempo import TempoController

__all__ = ["TempoController"]
