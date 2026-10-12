"""Track-level controls."""


class Track:
    """One track of the Live Set. index and slots are 0-based, as in AbletonOSC."""

    def __init__(self, osc, index):
        self.osc = osc
        self.index = index
        self.name = osc.query("/live/track/get/name", index)[1]

    def has_clip(self, slot):
        return bool(self.osc.query("/live/clip_slot/get/has_clip", self.index, slot)[2])

    def playing_slot(self):
        """Slot of the clip currently playing, or None."""
        slot = self.osc.query("/live/track/get/playing_slot_index", self.index)[1]
        return slot if slot >= 0 else None

    def fire_clip(self, slot):
        self.osc.send("/live/clip_slot/fire", self.index, slot)

    def stop_clips(self):
        self.osc.send("/live/track/stop_all_clips", self.index)

    def is_looping(self, slot):
        return bool(self.osc.query("/live/clip/get/looping", self.index, slot)[2])

    def set_looping(self, slot, looping):
        self.osc.send("/live/clip/set/looping", self.index, slot, int(looping))
