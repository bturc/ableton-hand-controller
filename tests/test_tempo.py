from ableton_hand_controller.ableton import Song
from ableton_hand_controller.controllers import TempoController
from ableton_hand_controller.gestures import GestureEvent


class FakeOSC:
    """Stands in for AbletonOSC: records sent messages, answers tempo queries."""

    def __init__(self, tempo=120.0):
        self.tempo = tempo
        self.sent = []
        self.handlers = {}

    def send(self, address, *args):
        self.sent.append((address, *args))

    def query(self, address, *args):
        assert address == "/live/song/get/tempo"
        return (self.tempo,)

    def on(self, address, handler):
        self.handlers[address] = handler

    def off(self, address, handler):
        del self.handlers[address]


def test_song_reads_and_follows_tempo():
    osc = FakeOSC(tempo=128.0)
    song = Song(osc)
    assert song.tempo == 128.0
    assert ("/live/song/start_listen/tempo",) in osc.sent
    osc.handlers["/live/song/get/tempo"](100.0)  # tempo changed in Live
    assert song.tempo == 100.0


def test_song_clamps_tempo():
    song = Song(FakeOSC())
    song.tempo = 5
    assert song.tempo == 20.0
    song.tempo = 5000
    assert song.tempo == 999.0


def test_tempo_controller():
    osc = FakeOSC(tempo=120.0)
    controller = TempoController(Song(osc))
    controller(GestureEvent("Right", "peace"))
    assert osc.sent[-1] == ("/live/song/set/tempo", 130.0)
    controller(GestureEvent("Left", "metal"))
    assert osc.sent[-1] == ("/live/song/set/tempo", 120.0)
    n = len(osc.sent)
    controller(GestureEvent("Left", "fist"))  # unmapped gesture: no-op
    assert len(osc.sent) == n
