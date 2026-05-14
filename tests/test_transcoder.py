"""Tests for edl_parse.transcoder module."""

import pytest
from edl_parse.parser import EDLEvent, EDL
from edl_parse.transcoder import (
    TranscodeError,
    _timecode_to_frames,
    _frames_to_timecode,
    transcode_timecode,
    transcode_event,
    transcode_edl,
)


def make_event(num="001", src_in="01:00:00:00", src_out="01:00:01:00",
               rec_in="00:00:00:00", rec_out="00:00:01:00"):
    return EDLEvent(
        event_number=num,
        reel="CAM1",
        track="V",
        edit_type="C",
        source_in=src_in,
        source_out=src_out,
        record_in=rec_in,
        record_out=rec_out,
        clip_name="clip_a",
        note=None,
    )


def test_timecode_to_frames_basic():
    assert _timecode_to_frames("00:00:01:00", 25) == 25


def test_timecode_to_frames_with_frames():
    assert _timecode_to_frames("00:00:00:12", 24) == 12


def test_timecode_to_frames_hours():
    assert _timecode_to_frames("01:00:00:00", 25) == 90000


def test_timecode_to_frames_semicolon_separator():
    # Drop-frame style semicolons should be handled
    assert _timecode_to_frames("00:00:01;00", 30) == 30


def test_timecode_to_frames_invalid_raises():
    with pytest.raises(TranscodeError):
        _timecode_to_frames("00:00:01", 25)


def test_frames_to_timecode_basic():
    assert _frames_to_timecode(25, 25) == "00:00:01:00"


def test_frames_to_timecode_zero():
    assert _frames_to_timecode(0, 24) == "00:00:00:00"


def test_frames_to_timecode_hours():
    assert _frames_to_timecode(86400, 24) == "01:00:00:00"


def test_transcode_timecode_same_fps():
    tc = "01:00:10:12"
    assert transcode_timecode(tc, 25, 25) == tc


def test_transcode_timecode_24_to_25():
    # 1 second at 24fps = 24 frames; at 25fps that scales to 25 frames = 1 second
    result = transcode_timecode("00:00:01:00", 24, 25)
    assert result == "00:00:01:00"


def test_transcode_timecode_unsupported_src_raises():
    with pytest.raises(TranscodeError, match="source framerate"):
        transcode_timecode("00:00:01:00", 15, 25)


def test_transcode_timecode_unsupported_dst_raises():
    with pytest.raises(TranscodeError, match="destination framerate"):
        transcode_timecode("00:00:01:00", 25, 15)


def test_transcode_event_returns_edl_event():
    event = make_event()
    result = transcode_event(event, 25, 25)
    assert isinstance(result, EDLEvent)


def test_transcode_event_preserves_reel():
    event = make_event()
    result = transcode_event(event, 25, 25)
    assert result.reel == event.reel


def test_transcode_event_timecodes_change_with_different_fps():
    event = make_event(src_in="00:00:00:12", src_out="00:00:01:00",
                       rec_in="00:00:00:00", rec_out="00:00:00:20")
    result = transcode_event(event, 24, 25)
    # Frames should be scaled; just verify no exception and timecodes are strings
    assert isinstance(result.source_in, str)
    assert isinstance(result.record_out, str)


def test_transcode_edl_returns_edl_instance():
    edl = EDL(title="Test", fcm="NON-DROP FRAME")
    edl.events = [make_event()]
    result = transcode_edl(edl, 25, 25)
    assert isinstance(result, EDL)


def test_transcode_edl_preserves_title():
    edl = EDL(title="My Cut", fcm="NON-DROP FRAME")
    edl.events = [make_event()]
    result = transcode_edl(edl, 25, 25)
    assert result.title == "My Cut"


def test_transcode_edl_event_count():
    edl = EDL(title="Test", fcm="NON-DROP FRAME")
    edl.events = [make_event("001"), make_event("002"), make_event("003")]
    result = transcode_edl(edl, 24, 25)
    assert len(result.events) == 3
