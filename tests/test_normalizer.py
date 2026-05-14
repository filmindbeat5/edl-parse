"""Tests for edl_parse.normalizer."""

import pytest
from edl_parse.parser import EDL, EDLEvent
from edl_parse.normalizer import (
    NormalizeError,
    _normalize_timecode,
    normalize_event,
    normalize_edl,
)


def make_event(reel="cam_a", tc_in="01:00:00:00", tc_out="01:00:05:00"):
    e = EDLEvent()
    e.event_number = "001"
    e.reel = reel
    e.edit_type = "V"
    e.transition = "C"
    e.source_in = tc_in
    e.source_out = tc_out
    e.record_in = tc_in
    e.record_out = tc_out
    return e


def make_edl(events=None):
    edl = EDL()
    edl.title = "TEST EDL"
    edl.fcm = "NON-DROP FRAME"
    edl.events = events or [make_event()]
    return edl


# --- _normalize_timecode ---

def test_normalize_timecode_already_valid():
    assert _normalize_timecode("01:02:03:04") == "01:02:03:04"


def test_normalize_timecode_pads_single_digits():
    assert _normalize_timecode("1:2:3:4") == "01:02:03:04"


def test_normalize_timecode_semicolon_separator():
    assert _normalize_timecode("01;00;00;00") == "01:00:00:00"


def test_normalize_timecode_dot_separator():
    assert _normalize_timecode("01.00.10.05") == "01:00:10:05"


def test_normalize_timecode_invalid_parts_raises():
    with pytest.raises(NormalizeError):
        _normalize_timecode("01:00:00")


def test_normalize_timecode_non_integer_raises():
    with pytest.raises(NormalizeError):
        _normalize_timecode("01:00:xx:00")


def test_normalize_timecode_empty_raises():
    with pytest.raises(NormalizeError):
        _normalize_timecode("")


# --- normalize_event ---

def test_normalize_event_reel_upper():
    event = make_event(reel="cam_a")
    result = normalize_event(event, reel_case="upper")
    assert result.reel == "CAM_A"


def test_normalize_event_reel_lower():
    event = make_event(reel="CAM_A")
    result = normalize_event(event, reel_case="lower")
    assert result.reel == "cam_a"


def test_normalize_event_reel_preserve():
    event = make_event(reel="CaM_A")
    result = normalize_event(event, reel_case="preserve")
    assert result.reel == "CaM_A"


def test_normalize_event_invalid_reel_case_raises():
    event = make_event()
    with pytest.raises(NormalizeError):
        normalize_event(event, reel_case="title")


def test_normalize_event_timecodes_normalized():
    event = make_event(tc_in="1:0:0:0", tc_out="1:0:5:0")
    result = normalize_event(event, normalize_timecodes=True)
    assert result.source_in == "01:00:00:00"
    assert result.record_out == "01:00:05:00"


def test_normalize_event_preserves_other_fields():
    event = make_event()
    result = normalize_event(event)
    assert result.event_number == event.event_number
    assert result.edit_type == event.edit_type
    assert result.transition == event.transition


# --- normalize_edl ---

def test_normalize_edl_returns_edl_instance():
    edl = make_edl()
    result = normalize_edl(edl)
    assert isinstance(result, EDL)


def test_normalize_edl_preserves_title_and_fcm():
    edl = make_edl()
    result = normalize_edl(edl)
    assert result.title == edl.title
    assert result.fcm == edl.fcm


def test_normalize_edl_all_reels_uppercased():
    events = [make_event(reel="cam_a"), make_event(reel="cam_b")]
    edl = make_edl(events=events)
    result = normalize_edl(edl, reel_case="upper")
    assert all(e.reel == e.reel.upper() for e in result.events)


def test_normalize_edl_event_count_unchanged():
    events = [make_event(), make_event(), make_event()]
    edl = make_edl(events=events)
    result = normalize_edl(edl)
    assert len(result.events) == 3
