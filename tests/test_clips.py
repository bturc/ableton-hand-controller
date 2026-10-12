import pytest

from ableton_hand_controller.ableton import Track
from ableton_hand_controller.controllers import ClipController
from ableton_hand_controller.gestures import (
    GestureEvent, count_fingers, count_fingers_or_zero, is_zero_sign,
)
from helpers import make_hand, make_zero_sign


@pytest.mark.parametrize("extended, thumb, expected", [
    (set(), False, 0),
    ({"index"}, False, 1),
    ({"index", "middle"}, False, 2),
    ({"index", "middle", "ring"}, False, 3),
    ({"index", "middle", "ring", "pinky"}, False, 4),
    ({"index", "middle", "ring", "pinky"}, True, 5),
])
def test_count_fingers(extended, thumb, expected):
    assert count_fingers(make_hand(extended, thumb)) == expected


def test_zero_sign():
    assert is_zero_sign(make_zero_sign())
    assert not is_zero_sign(make_hand())  # fist
    assert not is_zero_sign(make_hand({"index"}))
    assert count_fingers_or_zero(make_zero_sign()) == "zero"
    assert count_fingers_or_zero(make_hand()) == 0


class FakeOSC:
    """Stands in for AbletonOSC: track 0 is 'Drums' with looping clips in slots 0 and 1."""

    def __init__(self, playing=None):
        self.sent = []
        self.playing = playing
        self.looping = {0: True, 1: True}

    def send(self, address, *args):
        self.sent.append((address, *args))
        if address == "/live/clip/set/looping":
            self.looping[args[1]] = bool(args[2])

    def query(self, address, *args):
        if address == "/live/track/get/name":
            return (args[0], "Drums")
        if address == "/live/clip_slot/get/has_clip":
            return (*args, args[1] in self.looping)
        if address == "/live/track/get/playing_slot_index":
            return (args[0], -2 if self.playing is None else self.playing)
        if address == "/live/clip/get/looping":
            return (*args, self.looping[args[1]])
        raise AssertionError(address)


def test_clip_controller():
    osc = FakeOSC()
    controller = ClipController(Track(osc, 0))
    controller(GestureEvent("Right", 2))
    assert osc.sent == [("/live/clip_slot/fire", 0, 1)]
    controller(GestureEvent("Right", 3))  # empty slot: ignored
    assert len(osc.sent) == 1
    controller(GestureEvent("Right", 0))
    assert osc.sent[-1] == ("/live/track/stop_all_clips", 0)


def test_zero_stops_after_clip_end_and_restores_looping():
    osc = FakeOSC(playing=1)
    with ClipController(Track(osc, 0)) as controller:
        controller(GestureEvent("Right", "zero"))
        assert osc.looping[1] is False
        assert ("/live/track/stop_all_clips", 0) not in osc.sent
        controller(GestureEvent("Right", 1))  # next clip: loop switch restored first
        assert osc.looping[1] is True
        assert osc.sent[-1] == ("/live/clip_slot/fire", 0, 0)
        osc.playing = 0
        controller(GestureEvent("Right", "zero"))
        assert osc.looping[0] is False
    assert osc.looping[0] is True  # restored on exit


def test_zero_with_nothing_playing():
    osc = FakeOSC(playing=None)
    ClipController(Track(osc, 0))(GestureEvent("Right", "zero"))
    assert osc.sent == []
