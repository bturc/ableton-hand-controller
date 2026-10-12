"""Controllers map gesture events to actions in Live.

A controller is any callable taking a gestures.GestureEvent.
"""

from .clips import ClipController
from .tempo import TempoController

__all__ = ["ClipController", "TempoController"]
