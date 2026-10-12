"""Command line entry point: `ableton-hand-controller <command>`."""

import argparse

from .ableton import AbletonOSC, Song
from .controllers import TempoController
from .pipeline import run


def cmd_gestures(args):
    run(camera_index=args.camera, mirror=args.mirror)


def cmd_tempo(args):
    with AbletonOSC() as osc, Song(osc) as song:
        print(f"Connected to Ableton Live. Current tempo: {song.tempo:.1f} BPM")
        run(TempoController(song), camera_index=args.camera, mirror=args.mirror)


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

    sub.add_parser("gestures", parents=[camera_opts],
                   help="show the webcam and print detected gestures").set_defaults(func=cmd_gestures)
    sub.add_parser("tempo", parents=[camera_opts],
                   help="metal = -10 BPM, peace = +10 BPM").set_defaults(func=cmd_tempo)
    sub.add_parser("check",
                   help="check the connection to Ableton Live").set_defaults(func=cmd_check)

    args = parser.parse_args(argv)
    args.func(args)
