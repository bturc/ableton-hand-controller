"""Song-level controls (the Live Set as a whole)."""

TEMPO_MIN, TEMPO_MAX = 20.0, 999.0  # Live's allowed tempo range


class Song:
    """Live's song, with a locally cached tempo that stays in sync with Live
    (including changes made by hand inside Live). Use as a context manager."""

    def __init__(self, osc):
        self.osc = osc
        self._tempo = float(osc.query("/live/song/get/tempo")[0])
        osc.on("/live/song/get/tempo", self._on_tempo)
        osc.send("/live/song/start_listen/tempo")

    def _on_tempo(self, tempo):
        self._tempo = float(tempo)

    @property
    def tempo(self):
        return self._tempo

    @tempo.setter
    def tempo(self, bpm):
        bpm = min(max(float(bpm), TEMPO_MIN), TEMPO_MAX)
        self.osc.send("/live/song/set/tempo", bpm)
        self._tempo = bpm  # assume success; the listener corrects us if not

    def close(self):
        self.osc.send("/live/song/stop_listen/tempo")
        self.osc.off("/live/song/get/tempo", self._on_tempo)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()
