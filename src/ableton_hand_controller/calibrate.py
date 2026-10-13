"""Interactive drawing of the neck zone used by gate.NeckZoneGate."""

import time

import cv2

from .gate import DEFAULT_ZONE_PATH, Zone
from .vision import Camera, HandDetector
from .vision.camera import DEFAULT_RESOLUTION
from .vision.drawing import draw_hand, draw_status, draw_zone

YELLOW = (0, 255, 255)


def calibrate(camera_index=0, mirror=False, resolution=DEFAULT_RESOLUTION,
              path=DEFAULT_ZONE_PATH):
    """Live preview -> SPACE freezes a frame -> drag a box over the neck.
    Returns the saved Zone, or None if cancelled."""
    try:
        previous = Zone.load(path).for_mirror(mirror)
    except FileNotFoundError:
        previous = None

    start = time.monotonic()
    with Camera(camera_index, mirror, resolution) as camera, HandDetector(mirrored=mirror) as detector:
        try:
            while True:
                frame = camera.read()
                if frame is None:
                    return None
                hands = detector.detect(frame, int((time.monotonic() - start) * 1000))
                for hand in hands:
                    draw_hand(frame, hand.points, hand.label)
                preview = frame.copy()
                if previous:
                    draw_zone(preview, previous, YELLOW)
                draw_status(preview, "Get in playing position, then press SPACE")
                draw_status(preview, "(q to cancel)", 1)
                cv2.imshow("Calibrate neck zone", preview)
                key = cv2.waitKey(1) & 0xFF
                if key == ord("q"):
                    return None
                if key == ord(" "):
                    break
            cv2.destroyAllWindows()

            print("Drag a box over the area your fretting hand covers while playing, "
                  "then press ENTER (c to cancel).")
            x, y, bw, bh = cv2.selectROI("Draw the neck zone", frame, showCrosshair=False)
        finally:
            cv2.destroyAllWindows()

    if bw == 0 or bh == 0:
        return None
    h, w = frame.shape[:2]
    zone = Zone(x / w, y / h, (x + bw) / w, (y + bh) / h, mirrored=mirror)
    zone.save(path)
    return zone
