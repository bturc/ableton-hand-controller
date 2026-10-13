"""Command line entry point: `ableton-hand-controller <command>`."""

import argparse

from .ableton import AbletonOSC, Song, Track
from .calibrate import calibrate
from .controllers import ClipController, TempoController
from .gate import NeckZoneGate, Zone
from .gestures import count_fingers_or_zero
from .pipeline import run
from .vision.camera import DEFAULT_RESOLUTION

HANDS = {"left": {"Left"}, "right": {"Right"}, "any": None}


def parse_resolution(text):
    try:
        width, height = (int(n) for n in text.lower().split("x"))
    except ValueError:
        raise argparse.ArgumentTypeError(f"expected WIDTHxHEIGHT, e.g. 1280x720, got {text!r}")
    return width, height


def pipeline_options(args):
    """run() keyword arguments from the shared camera/gesture options."""
    hand = args.hand or ("left" if args.guitar else "any")
    gesture_hands = HANDS[hand]
    gate = None
    if args.guitar:
        try:
            zone = Zone.load()
        except FileNotFoundError as e:
            raise SystemExit(e)
        gate = NeckZoneGate(zone.for_mirror(args.mirror), gesture_hands)
    return dict(camera_index=args.camera, mirror=args.mirror, resolution=args.resolution,
                gesture_hands=gesture_hands, gate=gate)


def cmd_gestures(args):
    run(**pipeline_options(args))


def cmd_tempo(args):
    options = pipeline_options(args)
    with AbletonOSC() as osc, Song(osc) as song:
        print(f"Connected to Ableton Live. Current tempo: {song.tempo:.1f} BPM")
        run(TempoController(song), **options)


def cmd_clips(args):
    options = pipeline_options(args)
    with AbletonOSC() as osc:
        track = Track(osc, args.track - 1)
        print(f"Connected to Ableton Live. Controlling track {args.track}: {track.name}")
        with ClipController(track) as controller:
            run(controller, classifier=count_fingers_or_zero, **options)


def cmd_calibrate(args):
    zone = calibrate(camera_index=args.camera, mirror=args.mirror, resolution=args.resolution)
    print("Neck zone saved." if zone else "Calibration cancelled.")


def cmd_check(_args):
    with AbletonOSC() as osc:
        tempo = osc.query("/live/song/get/tempo")[0]
        print(f"Connected to Ableton Live. Current tempo: {tempo:.1f} BPM")


def main(argv=None):
    parser = argparse.ArgumentParser(prog="ableton-hand-controller")
    sub = parser.add_subparsers(dest="command", required=True)

    camera_opts = argparse.ArgumentParser(add_help=False)
    camera_opts.add_argument("--camera", type=int, default=0, help="webcam index")
    camera_opts.add_argument("--mirror", action="store_true", help="flip the image horizontally")
    camera_opts.add_argument("--resolution", type=parse_resolution, default=DEFAULT_RESOLUTION,
                             metavar="WxH", help="camera resolution (default: 1280x720)")

    gesture_opts = argparse.ArgumentParser(add_help=False, parents=[camera_opts])
    gesture_opts.add_argument("--guitar", action="store_true",
                              help="ignore gestures while a hand is in the neck zone "
                                   "(see `calibrate`)")
    gesture_opts.add_argument("--hand", choices=HANDS,
                              help="hand that makes gestures (default: left with --guitar, "
                                   "otherwise any)")

    sub.add_parser("gestures", parents=[gesture_opts],
                   help="show the webcam and print detected gestures").set_defaults(func=cmd_gestures)
    sub.add_parser("tempo", parents=[gesture_opts],
                   help="metal = -10 BPM, peace = +10 BPM").set_defaults(func=cmd_tempo)
    clips = sub.add_parser("clips", parents=[gesture_opts],
                           help="N fingers = play clip N of a track, "
                                "O sign = stop after the clip ends, fist = stop now")
    clips.add_argument("--track", type=int, default=1, help="track number, starting at 1")
    clips.set_defaults(func=cmd_clips)
    sub.add_parser("calibrate", parents=[camera_opts],
                   help="draw the guitar neck zone used by --guitar").set_defaults(func=cmd_calibrate)
    sub.add_parser("check",
                   help="check the connection to Ableton Live").set_defaults(func=cmd_check)

    args = parser.parse_args(argv)
    args.func(args)
