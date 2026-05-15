"""Tests for edl_parse.summarizer."""

import pytest
from edl_parse.parser import EDL, EDLEvent
from edl_parse.summarizer import (
    SummaryError,
    summarize_event,
    summarize_edl,
    summarize_edl_brief,
)


def make_event(num="001", reel="CAM_A", edit_type="C",
               src_in="01:00:00:00", src_out="01:00:05:00",
               rec_in="00:00:00:00", rec_out="00:00:05:00", note=None):
    e = EDLEvent()
    e.event_number = num
    e.reel = reel
    e.edit_type = edit_type
    e.source_in = src_in
    e.source_out = src_out
    e.record_in = rec_in
    e.record_out = rec_out
    e.note = note
    return e


def make_edl(title="Test EDL", fcm="NON-DROP FRAME"):
    edl = EDL()
    edl.title = title
    edl.fcm = fcm
    edl.events = [
        make_event("001", "CAM_A"),
        make_event("002", "CAM_B", edit_type="D"),
        make_event("003", "CAM_A"),
    ]
    return edl


# --- summarize_event ---

def test_summarize_event_contains_event_number():
    e = make_event("042")
    result = summarize_event(e)
    assert "042" in result


def test_summarize_event_contains_reel():
    e = make_event(reel="TAPE_01")
    assert "TAPE_01" in summarize_event(e)


def test_summarize_event_contains_timecodes():
    e = make_event(src_in="01:00:10:00", rec_out="00:00:20:00")
    result = summarize_event(e)
    assert "01:00:10:00" in result
    assert "00:00:20:00" in result


def test_summarize_event_includes_note_when_present():
    e = make_event(note="VFX shot")
    assert "VFX shot" in summarize_event(e)


def test_summarize_event_no_note_field_omitted():
    e = make_event(note=None)
    assert "Note" not in summarize_event(e)


def test_summarize_event_missing_number_raises():
    e = make_event()
    e.event_number = None
    with pytest.raises(SummaryError):
        summarize_event(e)


# --- summarize_edl ---

def test_summarize_edl_contains_title():
    edl = make_edl(title="My Cut")
    assert "My Cut" in summarize_edl(edl)


def test_summarize_edl_contains_fcm():
    edl = make_edl(fcm="DROP FRAME")
    assert "DROP FRAME" in summarize_edl(edl)


def test_summarize_edl_contains_event_count():
    edl = make_edl()
    result = summarize_edl(edl)
    assert "3" in result


def test_summarize_edl_lists_all_reels():
    edl = make_edl()
    result = summarize_edl(edl)
    assert "CAM_A" in result
    assert "CAM_B" in result


def test_summarize_edl_empty_raises():
    edl = EDL()
    edl.title = "Empty"
    edl.fcm = "NON-DROP FRAME"
    edl.events = []
    with pytest.raises(SummaryError):
        summarize_edl(edl)


# --- summarize_edl_brief ---

def test_summarize_edl_brief_is_single_line():
    edl = make_edl()
    result = summarize_edl_brief(edl)
    assert "\n" not in result


def test_summarize_edl_brief_contains_title_and_count():
    edl = make_edl(title="Quick Cut")
    result = summarize_edl_brief(edl)
    assert "Quick Cut" in result
    assert "3" in result


def test_summarize_edl_brief_empty_raises():
    edl = EDL()
    edl.title = "Empty"
    edl.fcm = "NON-DROP FRAME"
    edl.events = []
    with pytest.raises(SummaryError):
        summarize_edl_brief(edl)
