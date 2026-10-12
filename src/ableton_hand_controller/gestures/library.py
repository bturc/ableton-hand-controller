"""Static hand gesture definitions.

Each gesture is a function: finger_states dict -> bool. The thumb is ignored
unless a gesture specifically cares about it. Add new gestures to GESTURES.
"""

from ..landmarks import FINGERS
from .fingers import finger_states


def is_metal(f):
    return f["index"] and f["pinky"] and not f["middle"] and not f["ring"]


def is_fist(f):
    return not any(f[k] for k in FINGERS)


def is_open_palm(f):
    return all(f[k] for k in FINGERS)


def is_point(f):
    return f["index"] and not f["middle"] and not f["ring"] and not f["pinky"]


def is_peace(f):
    return f["index"] and f["middle"] and not f["ring"] and not f["pinky"]


# name -> detector. Order matters: first match wins.
GESTURES = {
    "metal": is_metal,
    "peace": is_peace,
    "point": is_point,
    "open_palm": is_open_palm,
    "fist": is_fist,
}


def classify(points):
    """Return the name of the gesture shown by a hand's landmarks, or None."""
    states = finger_states(points)
    for name, detector in GESTURES.items():
        if detector(states):
            return name
    return None
