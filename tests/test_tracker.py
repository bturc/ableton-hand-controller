from ableton_hand_controller.gestures import GestureTracker


def test_fires_once_after_hold():
    t = GestureTracker(hold_seconds=0.3)
    assert t.update("peace", 0.0) is None
    assert t.update("peace", 0.2) is None
    assert t.update("peace", 0.3) == "peace"
    assert t.update("peace", 1.0) is None  # still held: no repeat


def test_refires_after_release():
    t = GestureTracker(hold_seconds=0.3, release_seconds=0.2)
    t.update("peace", 0.0)
    t.update("peace", 0.3)
    t.update(None, 0.4)
    t.update(None, 0.7)  # gone for 0.4s: released
    t.update("peace", 0.8)
    assert t.update("peace", 1.1) == "peace"


def test_brief_flicker_does_not_refire():
    t = GestureTracker(hold_seconds=0.3, release_seconds=0.2)
    t.update("peace", 0.0)
    t.update("peace", 0.3)
    t.update("fist", 0.35)  # one-frame misdetection
    assert t.update("peace", 0.4) is None
    assert t.update("peace", 1.0) is None


def test_other_gesture_fires_without_waiting_for_release():
    t = GestureTracker(hold_seconds=0.3, release_seconds=0.2)
    t.update("peace", 0.0)
    t.update("peace", 0.3)
    t.update("fist", 0.35)
    assert t.update("fist", 0.65) == "fist"


def test_reset_forgets_pose():
    t = GestureTracker(hold_seconds=0.3)
    t.update("peace", 0.0)
    t.reset()
    assert t.update("peace", 0.3) is None  # hold timer restarted


def test_none_never_fires():
    t = GestureTracker(hold_seconds=0.3)
    t.update(None, 0.0)
    assert t.update(None, 1.0) is None
