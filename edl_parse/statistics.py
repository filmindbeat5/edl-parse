"""Statistics and summary reporting for EDL objects."""

from collections import Counter
from typing import Dict, Any

from edl_parse.parser import EDL
from edl_parse.sorter import _timecode_to_frames


class StatisticsError(Exception):
    def __str__(self):
        return f"StatisticsError: {self.args[0]}"


def _duration_in_frames(tc_in: str, tc_out: str, fps: int = 25) -> int:
    """Return the number of frames between two timecodes."""
    return _timecode_to_frames(tc_out, fps) - _timecode_to_frames(tc_in, fps)


def _frames_to_timecode(frames: int, fps: int = 25) -> str:
    """Convert a frame count back to HH:MM:SS:FF string."""
    ff = frames % fps
    total_seconds = frames // fps
    ss = total_seconds % 60
    mm = (total_seconds // 60) % 60
    hh = total_seconds // 3600
    return f"{hh:02d}:{mm:02d}:{ss:02d}:{ff:02d}"


def event_count(edl: EDL) -> int:
    """Return the total number of events in the EDL."""
    return len(edl.events)


def reel_counts(edl: EDL) -> Dict[str, int]:
    """Return a mapping of reel name to number of events using that reel."""
    return dict(Counter(e.reel for e in edl.events))


def edit_type_counts(edl: EDL) -> Dict[str, int]:
    """Return a mapping of edit type to number of events with that type."""
    return dict(Counter(e.edit_type for e in edl.events))


def total_source_duration(edl: EDL, fps: int = 25) -> str:
    """Return the sum of all source clip durations as a timecode string."""
    if not edl.events:
        raise StatisticsError("EDL contains no events.")
    total = sum(
        _duration_in_frames(e.source_in, e.source_out, fps)
        for e in edl.events
    )
    return _frames_to_timecode(total, fps)


def total_record_duration(edl: EDL, fps: int = 25) -> str:
    """Return the sum of all record timeline durations as a timecode string."""
    if not edl.events:
        raise StatisticsError("EDL contains no events.")
    total = sum(
        _duration_in_frames(e.record_in, e.record_out, fps)
        for e in edl.events
    )
    return _frames_to_timecode(total, fps)


def edl_statistics(edl: EDL, fps: int = 25) -> Dict[str, Any]:
    """Return a dict of all statistics for the given EDL."""
    if not edl.events:
        raise StatisticsError("EDL contains no events.")
    return {
        "title": edl.title,
        "fcm": edl.fcm,
        "event_count": event_count(edl),
        "reel_counts": reel_counts(edl),
        "edit_type_counts": edit_type_counts(edl),
        "total_source_duration": total_source_duration(edl, fps),
        "total_record_duration": total_record_duration(edl, fps),
    }
