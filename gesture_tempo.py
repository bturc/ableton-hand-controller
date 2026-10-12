"""Control Ableton Live's tempo with hand gestures via AbletonOSC.

    metal (\\m/) -> tempo - 10 BPM
    peace        -> tempo + 10 BPM

Requires Ableton Live running with the AbletonOSC control surface enabled.
Press 'q' in the webcam window to quit.
"""

import threading

from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import ThreadingOSCUDPServer
from pythonosc.udp_client import SimpleUDPClient

import hand_gestures

ABLETON_HOST = "127.0.0.1"
SEND_PORT = 11000     # AbletonOSC listens here
RECEIVE_PORT = 11001  # AbletonOSC replies here
TEMPO_MIN, TEMPO_MAX = 20.0, 999.0  # Live's allowed tempo range

# gesture name -> BPM change
TEMPO_STEPS = {
    "metal": -10,
    "peace": +10,
}


class TempoController:
    """Keeps track of Live's current tempo and nudges it up/down."""

    def __init__(self):
        self.client = SimpleUDPClient(ABLETON_HOST, SEND_PORT)
        self.tempo = None
        self.tempo_known = threading.Event()

        dispatcher = Dispatcher()
        dispatcher.map("/live/song/get/tempo", self._on_tempo)
        self.server = ThreadingOSCUDPServer((ABLETON_HOST, RECEIVE_PORT), dispatcher)
        threading.Thread(target=self.server.serve_forever, daemon=True).start()

        # Get the current tempo, then get notified whenever it changes
        # (including changes made by hand inside Live).
        self.client.send_message("/live/song/get/tempo", [])
        self.client.send_message("/live/song/start_listen/tempo", [])
        if not self.tempo_known.wait(timeout=3):
            raise RuntimeError(
                "No reply from AbletonOSC. Is Live running with AbletonOSC "
                "selected as a Control Surface?"
            )
        print(f"Connected to Ableton Live. Current tempo: {self.tempo:.1f} BPM")

    def _on_tempo(self, _address, *args):
        self.tempo = float(args[0])
        self.tempo_known.set()

    def change(self, delta):
        new_tempo = min(max(self.tempo + delta, TEMPO_MIN), TEMPO_MAX)
        self.client.send_message("/live/song/set/tempo", [new_tempo])
        self.tempo = new_tempo  # assume success; the listener corrects us if not
        print(f"Tempo -> {new_tempo:.1f} BPM")

    def close(self):
        self.client.send_message("/live/song/stop_listen/tempo", [])
        self.server.shutdown()
        self.server.server_close()


def main():
    tempo = TempoController()

    def on_gesture(_hand, gesture):
        if gesture in TEMPO_STEPS:
            tempo.change(TEMPO_STEPS[gesture])

    try:
        hand_gestures.main(on_gesture=on_gesture)
    finally:
        tempo.close()


if __name__ == "__main__":
    main()
