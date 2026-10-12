"""Control Ableton Live with hand gestures seen by a webcam.

Modules:
    landmarks    MediaPipe hand landmark indices
    vision       webcam capture, hand landmark detection, drawing
    gestures     gesture recognition from landmarks
    ableton      AbletonOSC connection and Live object wrappers
    controllers  map gesture events to actions in Live
    pipeline     the main loop tying them together
    cli          the `ableton-hand-controller` command
"""
