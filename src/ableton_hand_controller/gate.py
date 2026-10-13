"""Gating: ignore gestures while playing guitar.

The neck zone is a rectangle of the camera image covering where the fretting
hand sits while playing. It's drawn once with `ableton-hand-controller
calibrate` and saved to DEFAULT_ZONE_PATH.
"""

import json
from dataclasses import asdict, dataclass
from pathlib import Path

DEFAULT_ZONE_PATH = Path("config/neck_zone.json")


@dataclass(frozen=True)
class Zone:
    """A rectangle in normalized image coordinates (0..1), so it doesn't
    depend on the camera resolution."""
    x0: float
    y0: float
    x1: float
    y1: float
    mirrored: bool = False  # whether it was drawn on a mirrored image

    def for_mirror(self, mirrored):
        """The same zone, as seen with the image mirrored or not."""
        if mirrored == self.mirrored:
            return self
        return Zone(1 - self.x1, self.y0, 1 - self.x0, self.y1, mirrored)

    def contains(self, x, y, width, height):
        return self.x0 <= x / width <= self.x1 and self.y0 <= y / height <= self.y1

    def to_pixels(self, width, height):
        return (int(self.x0 * width), int(self.y0 * height),
                int(self.x1 * width), int(self.y1 * height))

    def save(self, path=DEFAULT_ZONE_PATH):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(asdict(self), indent=2))

    @classmethod
    def load(cls, path=DEFAULT_ZONE_PATH):
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(
                f"No neck zone saved at {path}. Run `ableton-hand-controller calibrate` first."
            )
        return cls(**json.loads(path.read_text()))


class NeckZoneGate:
    """Decides each frame whether gestures are accepted ("open").

    - Closes as soon as any hand has at least min_points landmarks in the zone.
    - Reopens once a gesture hand has been seen outside the zone, with no hand
      in it, for reopen_seconds.
    - Not seeing any gesture hand changes nothing: MediaPipe often loses the
      fretting hand behind the neck, which must not count as "hand removed".

    gesture_hands: labels allowed to make gestures, e.g. {"Left"}; None = any.
    """

    def __init__(self, zone, gesture_hands=None, reopen_seconds=0.5, min_points=5):
        self.zone = zone
        self.gesture_hands = gesture_hands
        self.reopen_seconds = reopen_seconds
        self.min_points = min_points
        self.is_open = False  # opens once a gesture hand is seen off the neck
        self._clear_since = None

    def on_neck(self, hand, width, height):
        inside = sum(self.zone.contains(x, y, width, height) for x, y in hand.points)
        return inside >= self.min_points

    def update(self, hands, now, width, height):
        """Feed the current frame's hands; return True if gestures are accepted."""
        if any(self.on_neck(hand, width, height) for hand in hands):
            self.is_open = False
            self._clear_since = None
        elif any(self.gesture_hands is None or hand.label in self.gesture_hands
                 for hand in hands):
            if self._clear_since is None:
                self._clear_since = now
            if now - self._clear_since >= self.reopen_seconds:
                self.is_open = True
        else:
            self._clear_since = None
        return self.is_open
