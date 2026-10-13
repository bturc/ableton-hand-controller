"""Webcam capture."""

import cv2

DEFAULT_RESOLUTION = (1280, 720)


class Camera:
    """Reads BGR frames from a webcam. Use as a context manager.

    OpenCV opens webcams at 640x480 by default, which crops the sides of
    16:9 sensors; asking for a 16:9 resolution gives the full field of view.
    """

    def __init__(self, index=0, mirror=False, resolution=DEFAULT_RESOLUTION):
        self.mirror = mirror
        self.cap = cv2.VideoCapture(index)
        if not self.cap.isOpened():
            raise RuntimeError(f"Could not open webcam {index}. Try another camera index.")
        if resolution:
            # Many Windows webcams only deliver HD frames as MJPG
            self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[0])
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[1])
        self.resolution = (int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                           int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))

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
