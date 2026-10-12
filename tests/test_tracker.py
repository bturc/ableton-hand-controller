from ableton_hand_controller.gestures import GestureTracker


def test_fires_once_after_hold():
    t = GestureTracker(hold_seconds=0.3)
    assert t.update("peace", 0.0) is None
    assert t.update("peace", 0.2) is None
    assert t.update("peace", 0.3) == "peace"
    assert t.update("peace", 1.0) is None  # still held: no repeat


def test_refires_after_pose_change():
    t = GestureTracker(hold_seconds=0.3)
    t.update("peace", 0.0)
    t.update("peace", 0.3)
    t.update(None, 0.4)
    t.update("peace", 0.5)
    assert t.update("peace", 0.8) == "peace"


def test_none_never_fires():
    t = GestureTracker(hold_seconds=0.3)
    t.update(None, 0.0)
    assert t.update(None, 1.0) is None
