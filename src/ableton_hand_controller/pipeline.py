"""The main loop: webcam -> hands -> gestures -> your callback."""

import time

import cv2

from .gestures import GestureEvent, GestureTracker, classify
from .vision import Camera, HandDetector
from .vision.drawing import draw_hand, draw_status


def run(on_gesture=None, camera_index=0, mirror=False, hold_seconds=0.3,
        window_title="Ableton Hand Controller (q to quit)"):
    """Show the webcam with hand overlays until 'q' is pressed.

    on_gesture(GestureEvent) is called each time a gesture has been held for
    hold_seconds. It fires once per pose; change pose to fire again.
    """
    trackers = {}  # one tracker per hand label ("Left"/"Right")
    start = prev = time.monotonic()

    with Camera(camera_index, mirror) as camera, HandDetector() as detector:
        try:
            while (frame := camera.read()) is not None:
                now = time.monotonic()
                hands = detector.detect(frame, int((now - start) * 1000))

                for hand in hands:
                    gesture = classify(hand.points)
                    tracker = trackers.setdefault(hand.label, GestureTracker(hold_seconds))
                    if fired := tracker.update(gesture, now):
                        event = GestureEvent(hand.label, fired)
                        print(f"[{event.hand}] {event.gesture}")
                        if on_gesture:
                            on_gesture(event)
                    draw_hand(frame, hand.points, f"{hand.label}: {gesture or '-'}")

                # a hand that left the frame loses its state
                seen = {hand.label for hand in hands}
                for label in list(trackers):
                    if label not in seen:
                        del trackers[label]

                fps = 1.0 / max(now - prev, 1e-6)
                prev = now
                draw_status(frame, f"{fps:.0f} FPS | hands: {len(hands)}")

                cv2.imshow(window_title, frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
        finally:
            cv2.destroyAllWindows()
