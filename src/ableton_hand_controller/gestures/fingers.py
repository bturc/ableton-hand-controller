"""Per-finger features computed from hand landmarks."""

import math

from ..landmarks import FINGERS, PINKY_MCP, THUMB_IP, THUMB_TIP, WRIST


def dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def finger_states(points):
    """Return {finger: True if extended} for thumb, index, middle, ring, pinky.

    Works at any hand rotation: a finger is extended when its tip is farther
    from the wrist than its PIP joint.
    """
    wrist = points[WRIST]
    states = {}
    for name, (_mcp, pip, tip) in FINGERS.items():
        states[name] = dist(wrist, points[tip]) > dist(wrist, points[pip]) * 1.1
    # Thumb: tip farther from the pinky base than the thumb's IP joint
    states["thumb"] = (
        dist(points[THUMB_TIP], points[PINKY_MCP])
        > dist(points[THUMB_IP], points[PINKY_MCP]) * 1.05
    )
    return states
