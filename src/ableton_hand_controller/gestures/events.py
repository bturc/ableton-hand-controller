"""Events emitted when a gesture is recognized."""

from dataclasses import dataclass


@dataclass(frozen=True)
class GestureEvent:
    hand: str     # "Left" or "Right"
    gesture: str  # a key of gestures.GESTURES
