"""Tests for edl_parse/reverser.py"""

import pytest
from edl_parse.parser import EDL, EDLEvent
from edl_parse.reverser import ReverseError, reverse_events, reverse_edl


def make_event(number, reel="CAM1", src_in="01:00:00:00", src_out="01:00:05:00",
               rec_in="01:00:00:00", rec_out="01:00:05:00"):
    e = EDLEvent(
        event_number=number,
        reel=reel,
        edit_type="V",
        transition="C",
        source_in=src_in,
        source_out=src_out,
        record_in=rec_in,
        record_out=rec_out,
    )
    return e


def make_edl(events=None):
    edl = EDL()
    edl.title = "TEST EDL"
    edl.fcm = "NON-DROP FRAME"
    edl.events = events or [
        make_event("001", reel="CAM1"),
        make_event("002", reel="CAM2"),
        make_event("003", reel="CAM3"),
    ]
    return edl


def test_reverse_events_returns_list():
    events = [make_event("001"), make_event("002"), make_event("003")]
    result = reverse_events(events)
    assert isinstance(result, list)


def test_reverse_events_correct_count():
    events = [make_event("001"), make_event("002"), make_event("003")]
    result = reverse_events(events)
    assert len(result) == 3


def test_reverse_events_order_reversed():
    events = [make_event("001", reel="A"), make_event("002", reel="B"), make_event("003", reel="C")]
    result = reverse_events(events)
    assert result[0].reel == "C"
    assert result[1].reel == "B"
    assert result[2].reel == "A"


def test_reverse_events_renumbers_sequentially():
    events = [make_event("001"), make_event("002"), make_event("003")]
    result = reverse_events(events)
    assert result[0].event_number == "001"
    assert result[1].event_number == "002"
    assert result[2].event_number == "003"


def test_reverse_events_empty_returns_empty():
    result = reverse_events([])
    assert result == []


def test_reverse_events_invalid_type_raises():
    with pytest.raises(ReverseError):
        reverse_events("not a list")


def test_reverse_edl_returns_edl_instance():
    edl = make_edl()
    result = reverse_edl(edl)
    assert isinstance(result, EDL)


def test_reverse_edl_preserves_title():
    edl = make_edl()
    result = reverse_edl(edl)
    assert result.title == "TEST EDL"


def test_reverse_edl_preserves_fcm():
    edl = make_edl()
    result = reverse_edl(edl)
    assert result.fcm == "NON-DROP FRAME"


def test_reverse_edl_events_reversed():
    edl = make_edl()
    result = reverse_edl(edl)
    assert result.events[0].reel == "CAM3"
    assert result.events[-1].reel == "CAM1"


def test_reverse_edl_does_not_mutate_original():
    edl = make_edl()
    original_first_reel = edl.events[0].reel
    reverse_edl(edl)
    assert edl.events[0].reel == original_first_reel


def test_reverse_edl_empty_events_raises():
    edl = make_edl(events=[])
    with pytest.raises(ReverseError):
        reverse_edl(edl)


def test_reverse_edl_invalid_type_raises():
    with pytest.raises(ReverseError):
        reverse_edl("not an edl")
