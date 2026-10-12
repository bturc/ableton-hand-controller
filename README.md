# Ableton Hand Controller

Control Ableton Live with hand gestures seen by a webcam, using MediaPipe for
hand tracking and [AbletonOSC](https://github.com/ideoforms/AbletonOSC) to talk
to Live.

## Setup

1. Install [uv](https://docs.astral.sh/uv/), then `uv sync`.
2. Install AbletonOSC in Live and select it as a Control Surface
   (Preferences > Link, Tempo & MIDI).
3. The MediaPipe hand model is downloaded to `models/` on first run.

## Usage

```
uv run ableton-hand-controller check      # test the connection to Live
uv run ableton-hand-controller gestures   # webcam preview, prints detected gestures
uv run ableton-hand-controller tempo      # metal = -10 BPM, peace = +10 BPM
```

`gestures` and `tempo` accept `--camera N` and `--mirror`. Press `q` in the
webcam window to quit.

## Project layout

```
src/ableton_hand_controller/
  landmarks.py    MediaPipe hand landmark indices
  vision/         webcam capture, hand detection, overlay drawing
  gestures/       finger features, gesture definitions, hold/debounce tracker
  ableton/        AbletonOSC client (send / query / listen) and Live wrappers (Song)
  controllers/    gesture event -> action in Live (e.g. TempoController)
  pipeline.py     main loop: webcam -> hands -> gestures -> controller
  cli.py          the `ableton-hand-controller` command
scripts/          small standalone examples using the library
tests/            unit tests (no webcam or Live needed): `uv run pytest`
```

## Extending

- **New gesture:** add a detector function in `gestures/library.py` and register it in `GESTURES`.
- **New Live control:** add a wrapper in `ableton/` (see `Song`), using the
  [AbletonOSC API](https://github.com/ideoforms/AbletonOSC#documentation).
- **New mapping:** write a controller (any callable taking a `GestureEvent`)
  in `controllers/`, and pass it to `pipeline.run()` or add a CLI command.
