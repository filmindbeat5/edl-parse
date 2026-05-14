"""Tests for edl_parse.duplicator."""

import pytest
from edl_parse.parser import EDLEvent, EDL
from edl_parse.duplicator import (
    DuplicateError,
    duplicate_event,
    duplicate_events,
    duplicate_edl_events,
)


def make_event(number="001", reel="A001", edit_type="V", src_in="01:00:00:00",
               src_out="01:00:05:00", rec_in="00:00:00:00", rec_out="00:00:05:00"):
    ev = EDLEvent()
    ev.event_number = number
    ev.reel = reel
    ev.edit_type = edit_type
    ev.transition = "C"
    ev.source_in = src_in
    ev.source_out = src_out
    ev.record_in = rec_in
    ev.record_out = rec_out
    ev.clip_name = "clip"
    ev.note = ""
    return ev


def make_edl(n=3):
    edl = EDL()
    edl.title = "TEST"
    edl.fcm = "NON-DROP FRAME"
    edl.events = [make_event(number=str(i).zfill(3), reel=f"R{i:03d}") for i in range(1, n + 1)]
    return edl


# --- duplicate_event ---

def test_duplicate_event_returns_list():
    ev = make_event()
    result = duplicate_event(ev, count=2)
    assert isinstance(result, list)


def test_duplicate_event_correct_count():
    ev = make_event()
    result = duplicate_event(ev, count=3)
    assert len(result) == 3


def test_duplicate_event_copies_are_independent():
    ev = make_event()
    copies = duplicate_event(ev, count=2)
    copies[0].reel = "CHANGED"
    assert copies[1].reel == ev.reel


def test_duplicate_event_preserves_fields():
    ev = make_event(reel="ORIG", src_in="01:00:10:00")
    copy = duplicate_event(ev, count=1)[0]
    assert copy.reel == "ORIG"
    assert copy.source_in == "01:00:10:00"


def test_duplicate_event_count_zero_raises():
    ev = make_event()
    with pytest.raises(DuplicateError):
        duplicate_event(ev, count=0)


def test_duplicate_event_negative_count_raises():
    ev = make_event()
    with pytest.raises(DuplicateError):
        duplicate_event(ev, count=-1)


# --- duplicate_events ---

def test_duplicate_events_expands_list():
    events = [make_event(number="001"), make_event(number="002")]
    result = duplicate_events(events, count=1)
    # each of 2 originals + 1 copy => 4 total
    assert len(result) == 4


def test_duplicate_events_original_first():
    ev = make_event(reel="ORIG")
    result = duplicate_events([ev], count=2)
    assert result[0].reel == "ORIG"


def test_duplicate_events_count_zero_raises():
    with pytest.raises(DuplicateError):
        duplicate_events([make_event()], count=0)


# --- duplicate_edl_events ---

def test_duplicate_edl_events_returns_edl():
    edl = make_edl(2)
    result = duplicate_edl_events(edl, count=1)
    assert isinstance(result, EDL)


def test_duplicate_edl_events_event_count():
    edl = make_edl(3)
    result = duplicate_edl_events(edl, count=2)
    # 3 originals, each followed by 2 copies => 9
    assert len(result.events) == 9


def test_duplicate_edl_events_renumbers_sequentially():
    edl = make_edl(2)
    result = duplicate_edl_events(edl, count=1)
    numbers = [ev.event_number for ev in result.events]
    assert numbers == ["001", "002", "003", "004"]


def test_duplicate_edl_events_preserves_title():
    edl = make_edl(2)
    result = duplicate_edl_events(edl, count=1)
    assert result.title == edl.title


def test_duplicate_edl_events_preserves_fcm():
    edl = make_edl(2)
    result = duplicate_edl_events(edl, count=1)
    assert result.fcm == edl.fcm


def test_duplicate_edl_events_does_not_mutate_original():
    edl = make_edl(2)
    duplicate_edl_events(edl, count=3)
    assert len(edl.events) == 2
