"""Launch clips on the first track of Ableton Live by counting fingers.

    N fingers up -> play clip N (top to bottom)
    O sign ("0") -> stop once the playing clip reaches its end
    fist         -> stop the track now

Requires Ableton Live running with the AbletonOSC control surface enabled.
Press 'q' in the webcam window to quit.

Same as `ableton-hand-controller clips`; kept as a minimal example of wiring
the library together.
"""

from ableton_hand_controller.ableton import AbletonOSC, Track
from ableton_hand_controller.controllers import ClipController
from ableton_hand_controller.gestures import count_fingers_or_zero
from ableton_hand_controller.pipeline import run


def main():
    with AbletonOSC() as osc:
        track = Track(osc, 0)
        print(f"Connected to Ableton Live. Controlling track 1: {track.name}")
        with ClipController(track) as controller:
            run(on_gesture=controller, classifier=count_fingers_or_zero)


if __name__ == "__main__":
    main()
