"""Detect simple hand gestures from landmarks and print when one is recognized.

Press 'q' to quit. Add your own gestures in GESTURES at the bottom of the
"gesture definitions" section.
"""

import math
import time
import urllib.request
from pathlib import Path

import cv2
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision

MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/hand_landmarker/"
    "hand_landmarker/float16/1/hand_landmarker.task"
)
MODEL_PATH = Path("models/hand_landmarker.task")
CAMERA_INDEX = 0
HOLD_SECONDS = 0.3  # a pose must be held this long before it counts

HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4), (0, 5), (5, 6), (6, 7), (7, 8),
    (5, 9), (9, 10), (10, 11), (11, 12), (9, 13), (13, 14), (14, 15),
    (15, 16), (13, 17), (17, 18), (18, 19), (19, 20), (0, 17),
]

# Landmark indices: (MCP, PIP, TIP) for each non-thumb finger
FINGERS = {
    "index": (5, 6, 8),
    "middle": (9, 10, 12),
    "ring": (13, 14, 16),
    "pinky": (17, 18, 20),
}


# ---------------------------------------------------------------- features
def dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def finger_states(pts):
    """Return {finger: True if extended}. Works at any hand rotation:
    a finger is extended when its tip is farther from the wrist than its PIP joint."""
    wrist = pts[0]
    states = {}
    for name, (_mcp, pip, tip) in FINGERS.items():
        states[name] = dist(wrist, pts[tip]) > dist(wrist, pts[pip]) * 1.1
    # Thumb: tip farther from the pinky base than the thumb's IP joint
    states["thumb"] = dist(pts[4], pts[17]) > dist(pts[3], pts[17]) * 1.05
    return states


# ------------------------------------------------------ gesture definitions
# Each gesture is a function: finger_states dict -> bool.
# The thumb is ignored unless a gesture specifically cares about it.
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


# name -> (detector, text to print). Order matters: first match wins.
GESTURES = {
    "metal": (is_metal, r"\m/"),
    "peace": (is_peace, "peace"),
    "point": (is_point, "point"),
    "open_palm": (is_open_palm, "open palm"),
    "fist": (is_fist, "fist"),
}


def classify(states):
    for name, (detector, _text) in GESTURES.items():
        if detector(states):
            return name
    return None


# ------------------------------------------------------------- debouncing
class GestureTracker:
    """Fires once when a gesture has been held for HOLD_SECONDS.
    It won't fire again until the hand changes to a different gesture."""

    def __init__(self):
        self.candidate = None
        self.since = 0.0
        self.fired = None

    def update(self, gesture, now):
        if gesture != self.candidate:
            self.candidate = gesture
            self.since = now
            if gesture != self.fired:
                self.fired = None  # allow re-trigger after changing pose
            return None
        if (
            gesture is not None
            and gesture != self.fired
            and now - self.since >= HOLD_SECONDS
        ):
            self.fired = gesture
            return gesture
        return None


# ------------------------------------------------------------------- main
def ensure_model():
    if not MODEL_PATH.exists():
        MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
        print(f"Downloading model to {MODEL_PATH} ...")
        urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)


def main():
    ensure_model()
    options = vision.HandLandmarkerOptions(
        base_options=mp_python.BaseOptions(model_asset_path=str(MODEL_PATH)),
        running_mode=vision.RunningMode.VIDEO,
        num_hands=2,
    )
    landmarker = vision.HandLandmarker.create_from_options(options)

    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        raise RuntimeError("Could not open webcam. Try another CAMERA_INDEX.")

    trackers = {}  # one tracker per hand label ("Left"/"Right")
    start = time.monotonic()

    while True:
        ok, frame = cap.read()
        if not ok:
            break
        # frame = cv2.flip(frame, 1)
        h, w = frame.shape[:2]
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        now = time.monotonic()
        result = landmarker.detect_for_video(mp_image, int((now - start) * 1000))

        seen = set()
        for i, hand in enumerate(result.hand_landmarks):
            label = result.handedness[i][0].category_name
            seen.add(label)
            pts = [(lm.x * w, lm.y * h) for lm in hand]  # pixel coords

            states = finger_states(pts)
            gesture = classify(states)

            tracker = trackers.setdefault(label, GestureTracker())
            fired = tracker.update(gesture, now)
            if fired:
                print(f"[{label}] {GESTURES[fired][1]}")

            # drawing
            ipts = [(int(x), int(y)) for x, y in pts]
            for a, b in HAND_CONNECTIONS:
                cv2.line(frame, ipts[a], ipts[b], (0, 255, 0), 2)
            for p in ipts:
                cv2.circle(frame, p, 4, (0, 0, 255), -1)
            cv2.putText(frame, f"{label}: {gesture or '-'}",
                        (ipts[0][0], ipts[0][1] + 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)

        # a hand that left the frame loses its state
        for label in list(trackers):
            if label not in seen:
                del trackers[label]

        cv2.imshow("Gestures (q to quit)", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
    landmarker.close()


if __name__ == "__main__":
    main()