from dataclasses import astuple

import pytest

from ableton_hand_controller.gate import NeckZoneGate, Zone
from ableton_hand_controller.vision.hands import Hand

W, H = 1000, 500
ZONE = Zone(0.0, 0.0, 0.5, 1.0)  # left half of the image


def hand(label, x):
    """A hand with all 21 landmarks clustered around pixel x."""
    return Hand(label, [(x + i, 250.0) for i in range(21)])


ON_NECK = hand("Left", 100)
LEFT_OFF = hand("Left", 800)
RIGHT_OFF = hand("Right", 800)


def test_zone_roundtrip_and_mirror(tmp_path):
    path = tmp_path / "zone.json"
    zone = Zone(0.1, 0.2, 0.3, 0.4)
    zone.save(path)
    assert Zone.load(path) == zone
    flipped = zone.for_mirror(True)
    assert flipped.mirrored
    assert astuple(flipped)[:4] == pytest.approx((0.7, 0.2, 0.9, 0.4))
    back = flipped.for_mirror(False)
    assert not back.mirrored
    assert astuple(back)[:4] == pytest.approx(astuple(zone)[:4])


def test_starts_closed_and_opens_after_hand_seen_off_neck():
    gate = NeckZoneGate(ZONE, {"Left"}, reopen_seconds=0.5)
    assert not gate.update([LEFT_OFF], 0.0, W, H)
    assert not gate.update([LEFT_OFF], 0.4, W, H)
    assert gate.update([LEFT_OFF], 0.5, W, H)


def test_closes_immediately_when_hand_on_neck():
    gate = NeckZoneGate(ZONE, {"Left"}, reopen_seconds=0.5)
    gate.update([LEFT_OFF], 0.0, W, H)
    gate.update([LEFT_OFF], 0.5, W, H)
    assert not gate.update([ON_NECK, RIGHT_OFF], 0.6, W, H)


def test_lost_fretting_hand_does_not_open():
    gate = NeckZoneGate(ZONE, {"Left"}, reopen_seconds=0.5)
    gate.update([ON_NECK, RIGHT_OFF], 0.0, W, H)
    # fretting hand hidden behind the neck: only the picking hand is seen
    assert not gate.update([RIGHT_OFF], 0.1, W, H)
    assert not gate.update([RIGHT_OFF], 5.0, W, H)


def test_brief_lift_does_not_open():
    gate = NeckZoneGate(ZONE, {"Left"}, reopen_seconds=0.5)
    gate.update([ON_NECK], 0.0, W, H)
    gate.update([LEFT_OFF], 0.1, W, H)
    assert not gate.update([ON_NECK], 0.3, W, H)
    assert not gate.update([LEFT_OFF], 0.4, W, H)
    assert not gate.update([LEFT_OFF], 0.8, W, H)
    assert gate.update([LEFT_OFF], 0.9, W, H)


def test_few_points_in_zone_is_not_on_neck():
    gate = NeckZoneGate(ZONE, None, min_points=5)
    edge = Hand("Left", [(498.0 + i, 250.0) for i in range(21)])  # 3 points inside
    assert not gate.on_neck(edge, W, H)
    assert gate.on_neck(ON_NECK, W, H)
