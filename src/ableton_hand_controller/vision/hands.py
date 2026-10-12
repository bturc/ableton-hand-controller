"""Hand landmark detection with MediaPipe."""

import urllib.request
from dataclasses import dataclass
from pathlib import Path

import cv2
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision

MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/hand_landmarker/"
    "hand_landmarker/float16/1/hand_landmarker.task"
)
DEFAULT_MODEL_PATH = Path("models/hand_landmarker.task")


@dataclass(frozen=True)
class Hand:
    label: str  # "Left" or "Right", as reported by MediaPipe
    points: list[tuple[float, float]]  # 21 landmarks in pixel coordinates


def ensure_model(path=DEFAULT_MODEL_PATH):
    path = Path(path)
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        print(f"Downloading model to {path} ...")
        urllib.request.urlretrieve(MODEL_URL, path)
    return path


class HandDetector:
    """Finds hands in video frames. Use as a context manager."""

    def __init__(self, model_path=DEFAULT_MODEL_PATH, num_hands=2):
        options = vision.HandLandmarkerOptions(
            base_options=mp_python.BaseOptions(model_asset_path=str(ensure_model(model_path))),
            running_mode=vision.RunningMode.VIDEO,
            num_hands=num_hands,
        )
        self.landmarker = vision.HandLandmarker.create_from_options(options)

    def detect(self, frame, timestamp_ms):
        """Return the hands found in a BGR frame. timestamp_ms must increase."""
        h, w = frame.shape[:2]
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        result = self.landmarker.detect_for_video(image, timestamp_ms)
        return [
            Hand(
                label=result.handedness[i][0].category_name,
                points=[(lm.x * w, lm.y * h) for lm in landmarks],
            )
            for i, landmarks in enumerate(result.hand_landmarks)
        ]

    def close(self):
        self.landmarker.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()
