"""Debouncing: turn per-frame gesture guesses into discrete events."""


class GestureTracker:
    """Fires once when a gesture has been held for hold_seconds.

    It won't fire the same gesture again until that gesture has been gone for
    release_seconds, so a few misdetected frames while holding a pose don't
    re-trigger it. A different gesture can fire at any time.
    """

    def __init__(self, hold_seconds=0.3, release_seconds=0.2):
        self.hold_seconds = hold_seconds
        self.release_seconds = release_seconds
        self.reset()

    def reset(self):
        self.candidate = None
        self.since = 0.0
        self.fired = None
        self.fired_seen = 0.0

    def update(self, gesture, now):
        """Feed the current frame's gesture; return it if it just fired, else None."""
        if self.fired is not None:
            if gesture == self.fired:
                self.fired_seen = now
            elif now - self.fired_seen >= self.release_seconds:
                self.fired = None  # released: may fire again

        if gesture != self.candidate:
            self.candidate = gesture
            self.since = now
            return None
        if (
            gesture is not None
            and gesture != self.fired
            and now - self.since >= self.hold_seconds
        ):
            self.fired = gesture
            self.fired_seen = now
            return gesture
        return None
