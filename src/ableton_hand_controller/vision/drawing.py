"""Overlay drawing helpers for the preview window."""

import cv2

from ..landmarks import HAND_CONNECTIONS, WRIST


def draw_hand(frame, points, text=None):
    ipts = [(int(x), int(y)) for x, y in points]
    for a, b in HAND_CONNECTIONS:
        cv2.line(frame, ipts[a], ipts[b], (0, 255, 0), 2)
    for p in ipts:
        cv2.circle(frame, p, 4, (0, 0, 255), -1)
    if text:
        x, y = ipts[WRIST]
        cv2.putText(frame, text, (x, y + 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)


def draw_status(frame, text, line=0, color=(255, 255, 255)):
    cv2.putText(frame, text, (10, 30 + 30 * line),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)


def draw_zone(frame, zone, color):
    h, w = frame.shape[:2]
    x0, y0, x1, y1 = zone.to_pixels(w, h)
    cv2.rectangle(frame, (x0, y0), (x1, y1), color, 2)
