"""Debouncing: turn per-frame gesture guesses into discrete events."""


class GestureTracker:
    """Fires once when a gesture has been held for hold_seconds.
    It won't fire again until the hand changes to a different gesture."""

    def __init__(self, hold_seconds=0.3):
        self.hold_seconds = hold_seconds
        self.candidate = None
        self.since = 0.0
        self.fired = None

    def update(self, gesture, now):
        """Feed the current frame's gesture; return it if it just fired, else None."""
        if gesture != self.candidate:
            self.candidate = gesture
            self.since = now
            if gesture != self.fired:
                self.fired = None  # allow re-trigger after changing pose
            return None
        if (
            gesture is not None
            and gesture != self.fired
            and now - self.since >= self.hold_seconds
        ):
            self.fired = gesture
            return gesture
        return None
