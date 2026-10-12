"""Control Ableton Live's tempo with hand gestures via AbletonOSC.

    metal (\\m/) -> tempo - 10 BPM
    peace        -> tempo + 10 BPM

Requires Ableton Live running with the AbletonOSC control surface enabled.
Press 'q' in the webcam window to quit.

Same as `ableton-hand-controller tempo`; kept as a minimal example of wiring
the library together.
"""

from ableton_hand_controller.ableton import AbletonOSC, Song
from ableton_hand_controller.controllers import TempoController
from ableton_hand_controller.pipeline import run


def main():
    with AbletonOSC() as osc, Song(osc) as song:
        print(f"Connected to Ableton Live. Current tempo: {song.tempo:.1f} BPM")
        run(on_gesture=TempoController(song))


if __name__ == "__main__":
    main()
