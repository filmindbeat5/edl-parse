"""Tests for edl_parse.offsetter."""

import pytest
from edl_parse.parser import EDL, EDLEvent
from edl_parse.offsetter import (
    OffsetError,
    _timecode_to_frames,
    _frames_to_timecode,
    offset_event_record,
    offset_edl_record,
)


def make_event(rec_in="01:00:00:00", rec_out="01:00:05:00", src_in="00:00:00:00", src_out="00:00:05:00"):
    return EDLEvent(
        event_number="001",
        reel="A001",
        track="V",
        edit_type="C",
        src_in=src_in,
        src_out=src_out,
        rec_in=rec_in,
        rec_out=rec_out,
    )


def test_timecode_to_frames_basic():
    assert _timecode_to_frames("00:00:01:00", fps=25) == 25


def test_timecode_to_frames_hours():
    assert _timecode_to_frames("01:00:00:00", fps=25) == 90000


def test_timecode_to_frames_mixed():
    assert _timecode_to_frames("00:01:01:10", fps=25) == 1535


def test_timecode_to_frames_invalid_raises():
    with pytest.raises(OffsetError):
        _timecode_to_frames("00:00:00", fps=25)


def test_frames_to_timecode_basic():
    assert _frames_to_timecode(25, fps=25) == "00:00:01:00"


def test_frames_to_timecode_hours():
    assert _frames_to_timecode(90000, fps=25) == "01:00:00:00"


def test_frames_to_timecode_negative_raises():
    with pytest.raises(OffsetError):
        _frames_to_timecode(-1, fps=25)


def test_offset_event_record_positive():
    event = make_event(rec_in="01:00:00:00", rec_out="01:00:05:00")
    result = offset_event_record(event, offset_frames=25, fps=25)
    assert result.rec_in == "01:00:01:00"
    assert result.rec_out == "01:00:06:00"


def test_offset_event_record_negative():
    event = make_event(rec_in="01:00:05:00", rec_out="01:00:10:00")
    result = offset_event_record(event, offset_frames=-25, fps=25)
    assert result.rec_in == "01:00:04:00"
    assert result.rec_out == "01:00:09:00"


def test_offset_event_preserves_src_timecodes():
    event = make_event(src_in="00:10:00:00", src_out="00:10:05:00")
    result = offset_event_record(event, offset_frames=50, fps=25)
    assert result.src_in == "00:10:00:00"
    assert result.src_out == "00:10:05:00"


def test_offset_event_preserves_reel_and_type():
    event = make_event()
    result = offset_event_record(event, offset_frames=0, fps=25)
    assert result.reel == event.reel
    assert result.edit_type == event.edit_type


def test_offset_edl_record_shifts_all_events():
    edl = EDL(title="Test", fcm="NON-DROP FRAME")
    edl.events = [
        make_event(rec_in="01:00:00:00", rec_out="01:00:05:00"),
        make_event(rec_in="01:00:05:00", rec_out="01:00:10:00"),
    ]
    result = offset_edl_record(edl, offset_frames=25, fps=25)
    assert result.events[0].rec_in == "01:00:01:00"
    assert result.events[1].rec_in == "01:00:06:00"


def test_offset_edl_preserves_metadata():
    edl = EDL(title="MyEDL", fcm="DROP FRAME")
    edl.events = [make_event()]
    result = offset_edl_record(edl, offset_frames=0, fps=25)
    assert result.title == "MyEDL"
    assert result.fcm == "DROP FRAME"
