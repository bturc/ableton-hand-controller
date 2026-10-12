"""Nudge Live's tempo with gestures."""

# gesture name -> BPM change
DEFAULT_STEPS = {
    "metal": -10,
    "peace": +10,
}


class TempoController:
    """Gesture callback for pipeline.run(): changes song.tempo by steps[gesture]."""

    def __init__(self, song, steps=DEFAULT_STEPS):
        self.song = song
        self.steps = steps

    def __call__(self, event):
        if event.gesture in self.steps:
            self.song.tempo += self.steps[event.gesture]
            print(f"Tempo -> {self.song.tempo:.1f} BPM")
