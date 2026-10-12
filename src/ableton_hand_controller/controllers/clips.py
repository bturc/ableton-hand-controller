"""Launch a track's clips by counting fingers."""


class ClipController:
    """Gesture callback for pipeline.run(classifier=count_fingers_or_zero).

    N fingers -> fire clip slot N of the track (1-based, top to bottom).
    "zero" (O sign) -> stop once the playing clip reaches its end.
    A fist (0 fingers) stops the track now. Empty slots are ignored.

    "Stop at the end" works by turning off the playing clip's loop switch so
    Live stops it at its end marker. The loop switch is turned back on before
    the next action and on close(), so use this as a context manager.
    """

    def __init__(self, track):
        self.track = track
        self._unlooped = None  # slot whose loop switch we turned off

    def __call__(self, event):
        if event.gesture == "zero":
            self._stop_at_end()
            return
        self._restore_looping()
        count = event.gesture
        if count == 0:
            self.track.stop_clips()
            print(f"{self.track.name}: stop")
        elif self.track.has_clip(count - 1):
            self.track.fire_clip(count - 1)
            print(f"{self.track.name}: clip {count}")
        else:
            print(f"{self.track.name}: slot {count} is empty")

    def _stop_at_end(self):
        slot = self.track.playing_slot()
        if slot is None:
            print(f"{self.track.name}: nothing playing")
            return
        if slot != self._unlooped:
            self._restore_looping()
            if self.track.is_looping(slot):
                self.track.set_looping(slot, False)
                self._unlooped = slot
        print(f"{self.track.name}: stopping after clip {slot + 1} ends")

    def _restore_looping(self):
        if self._unlooped is not None:
            self.track.set_looping(self._unlooped, True)
            self._unlooped = None

    def close(self):
        self._restore_looping()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()
