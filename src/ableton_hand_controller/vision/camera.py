"""Webcam capture."""

import cv2


class Camera:
    """Reads BGR frames from a webcam. Use as a context manager."""

    def __init__(self, index=0, mirror=False):
        self.mirror = mirror
        self.cap = cv2.VideoCapture(index)
        if not self.cap.isOpened():
            raise RuntimeError(f"Could not open webcam {index}. Try another camera index.")

    def read(self):
        """Return the next frame, or None if the camera stopped delivering."""
        ok, frame = self.cap.read()
        if not ok:
            return None
        return cv2.flip(frame, 1) if self.mirror else frame

    def close(self):
        self.cap.release()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()
