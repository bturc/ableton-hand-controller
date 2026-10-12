"""Synthetic hand landmarks for tests."""

from ableton_hand_controller.landmarks import FINGERS


def make_hand(extended=(), thumb=False):
    """21 pixel-space landmarks for an upright hand with the wrist at (0, 0).

    Fingers in `extended` point straight up; the others are curled.
    """
    points = [(0.0, 0.0)] * 21
    # thumb runs out to the left; pinky base is at x=45
    points[1] = (-20.0, -10.0)
    points[2] = (-40.0, -20.0)
    points[3] = (-60.0, -30.0)
    points[4] = (-90.0, -40.0) if thumb else (-30.0, -40.0)
    for i, (name, (mcp, pip, tip)) in enumerate(FINGERS.items()):
        x = -15.0 + 20.0 * i
        points[mcp] = (x, -50.0)
        points[pip] = (x, -80.0)
        points[pip + 1] = (x, -100.0) if name in extended else (x, -70.0)
        points[tip] = (x, -120.0) if name in extended else (x, -60.0)
    return points
