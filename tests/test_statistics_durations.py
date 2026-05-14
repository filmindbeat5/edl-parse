"""Additional duration-focused tests for edl_parse.statistics."""

import pytest
from edl_parse.parser import EDL, EDLEvent
from edl_parse.statistics import (
    _duration_in_frames,
    _frames_to_timecode,
    total_source_duration,
    total_record_duration,
)


def make_event(src_in, src_out, rec_in, rec_out):
    e = EDLEvent()
    e.event_number = 1
    e.reel = "REEL"
    e.edit_type = "V"
    e.transition = "C"
    e.source_in = src_in
    e.source_out = src_out
    e.record_in = rec_in
    e.record_out = rec_out
    return e


def test_duration_in_frames_same_second():
    assert _duration_in_frames("00:00:01:00", "00:00:02:00", fps=25) == 25


def test_duration_in_frames_zero():
    assert _duration_in_frames("00:00:05:00", "00:00:05:00", fps=25) == 0


def test_duration_in_frames_with_frames():
    # 00:00:01:10 to 00:00:01:20 = 10 frames
    assert _duration_in_frames("00:00:01:10", "00:00:01:20", fps=25) == 10


def test_frames_to_timecode_zero():
    assert _frames_to_timecode(0, fps=25) == "00:00:00:00"


def test_frames_to_timecode_one_second():
    assert _frames_to_timecode(25, fps=25) == "00:00:01:00"


def test_frames_to_timecode_one_hour():
    assert _frames_to_timecode(25 * 3600, fps=25) == "01:00:00:00"


def test_frames_to_timecode_mixed():
    # 1h 2m 3s 4f @ 25fps
    frames = (1 * 3600 + 2 * 60 + 3) * 25 + 4
    assert _frames_to_timecode(frames, fps=25) == "01:02:03:04"


def test_total_source_duration_single_event():
    edl = EDL()
    edl.events = [make_event("00:00:00:00", "00:00:02:00", "01:00:00:00", "01:00:02:00")]
    assert total_source_duration(edl, fps=25) == "00:00:02:00"


def test_total_record_duration_single_event():
    edl = EDL()
    edl.events = [make_event("00:00:00:00", "00:00:03:00", "01:00:00:00", "01:00:03:00")]
    assert total_record_duration(edl, fps=25) == "00:00:03:00"


def test_total_source_duration_multiple_events():
    edl = EDL()
    edl.events = [
        make_event("00:00:00:00", "00:00:01:00", "01:00:00:00", "01:00:01:00"),
        make_event("00:00:05:00", "00:00:06:00", "01:00:01:00", "01:00:02:00"),
        make_event("00:00:10:00", "00:00:11:00", "01:00:02:00", "01:00:03:00"),
    ]
    # 3 events * 1 second each = 3 seconds
    assert total_source_duration(edl, fps=25) == "00:00:03:00"
