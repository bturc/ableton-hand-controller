import pytest

from ableton_hand_controller.gestures import classify, finger_states
from helpers import make_hand


def test_finger_states():
    states = finger_states(make_hand(extended={"index", "pinky"}, thumb=True))
    assert states == {
        "thumb": True, "index": True, "middle": False, "ring": False, "pinky": True,
    }


@pytest.mark.parametrize("extended, expected", [
    ({"index", "pinky"}, "metal"),
    ({"index", "middle"}, "peace"),
    ({"index"}, "point"),
    ({"index", "middle", "ring", "pinky"}, "open_palm"),
    (set(), "fist"),
    ({"middle", "ring"}, None),
])
def test_classify(extended, expected):
    assert classify(make_hand(extended)) == expected
