"""Finger counting: an alternative classifier to gestures.classify."""

from ..landmarks import FINGERS, THUMB_TIP, WRIST
from .fingers import dist, finger_states

INDEX_MCP, _, INDEX_TIP = FINGERS["index"]
MIDDLE_MCP = FINGERS["middle"][0]

# Tunable, as fractions of palm length (wrist to middle finger base)
ZERO_TOUCH = 0.35  # thumb and index tips closer than this are touching
ZERO_ROUND = 0.5   # index tip farther than this from its base: curved, not in a fist


def count_fingers(points):
    """Return how many fingers (thumb included) are extended, 0 to 5."""
    return sum(finger_states(points).values())


def is_zero_sign(points):
    """An "O" made with the hand: thumb tip touching the index tip, with the
    index curved (not tucked into a fist) and the other fingers curled."""
    states = finger_states(points)
    if any(states[f] for f in FINGERS):
        return False
    palm = dist(points[WRIST], points[MIDDLE_MCP])
    return (
        dist(points[THUMB_TIP], points[INDEX_TIP]) < ZERO_TOUCH * palm
        and dist(points[INDEX_TIP], points[INDEX_MCP]) > ZERO_ROUND * palm
    )


def count_fingers_or_zero(points):
    """Return "zero" for the O sign, otherwise the number of extended fingers."""
    return "zero" if is_zero_sign(points) else count_fingers(points)
