"""The main loop: webcam -> hands -> gestures -> your callback."""

import time

import cv2

from .gestures import GestureEvent, GestureTracker, classify
from .vision import Camera, HandDetector
from .vision.camera import DEFAULT_RESOLUTION
from .vision.drawing import draw_hand, draw_status, draw_zone

GREEN, RED = (0, 200, 0), (0, 0, 255)


def run(on_gesture=None, classifier=classify, camera_index=0, mirror=False,
        resolution=DEFAULT_RESOLUTION, hold_seconds=0.3, gesture_hands=None, gate=None,
        window_title="Ableton Hand Controller (q to quit)"):
    """Show the webcam with hand overlays until 'q' is pressed.

    classifier(points) turns a hand's landmarks into a gesture (anything
    hashable, None for no gesture), e.g. gestures.classify or
    gestures.count_fingers.

    on_gesture(GestureEvent) is called each time a gesture has been held for
    hold_seconds. It fires once per pose; change pose to fire again.

    gesture_hands: hand labels allowed to make gestures, e.g. {"Left"};
    None = any hand.
    gate: optional NeckZoneGate; while it's closed, no gesture fires.
    """
    trackers = {}  # one tracker per hand label ("Left"/"Right")
    start = prev = time.monotonic()

    with Camera(camera_index, mirror, resolution) as camera, HandDetector(mirrored=mirror) as detector:
        try:
            while (frame := camera.read()) is not None:
                now = time.monotonic()
                h, w = frame.shape[:2]
                hands = detector.detect(frame, int((now - start) * 1000))

                listening = gate is None or gate.update(hands, now, w, h)
                if not listening:
                    trackers.clear()  # forget half-held poses while playing

                for hand in hands:
                    gesture = classifier(hand.points)
                    active = gesture_hands is None or hand.label in gesture_hands
                    if listening and active:
                        tracker = trackers.setdefault(hand.label, GestureTracker(hold_seconds))
                        if (fired := tracker.update(gesture, now)) is not None:
                            event = GestureEvent(hand.label, fired)
                            print(f"[{event.hand}] {event.gesture}")
                            if on_gesture:
                                on_gesture(event)
                    shown = "-" if gesture is None else gesture
                    draw_hand(frame, hand.points, f"{hand.label}: {shown}")

                # a hand that left the frame loses its state
                seen = {hand.label for hand in hands}
                for label in list(trackers):
                    if label not in seen:
                        del trackers[label]

                fps = 1.0 / max(now - prev, 1e-6)
                prev = now
                draw_status(frame, f"{fps:.0f} FPS | hands: {len(hands)}")
                if gate is not None:
                    color = GREEN if listening else RED
                    draw_zone(frame, gate.zone, color)
                    draw_status(frame, "LISTENING" if listening else "PLAYING", 1, color)

                cv2.imshow(window_title, frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
        finally:
            cv2.destroyAllWindows()
