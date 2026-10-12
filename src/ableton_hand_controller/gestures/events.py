"""Events emitted when a gesture is recognized."""

from dataclasses import dataclass


@dataclass(frozen=True)
class GestureEvent:
    hand: str     # "Left" or "Right"
    gesture: object  # what the pipeline's classifier returned, e.g. "peace" or 3
