"""Tests for edl_parse.reorderer."""

import pytest
from edl_parse.parser import EDL, EDLEvent
from edl_parse.reorderer import (
    ReorderError,
    reorder_by_field,
    reorder_by_custom_sequence,
    reorder_edl_events,
)


def make_event(number, reel, rec_in="01:00:00:00", edit_type="C"):
    e = EDLEvent()
    e.event_number = number
    e.reel = reel
    e.edit_type = edit_type
    e.source_in = "00:00:00:00"
    e.source_out = "00:00:01:00"
    e.record_in = rec_in
    e.record_out = "01:00:01:00"
    return e


@pytest.fixture
def sample_events():
    return [
        make_event("003", "REEL_C", rec_in="01:00:20:00"),
        make_event("001", "REEL_A", rec_in="01:00:00:00"),
        make_event("002", "REEL_B", rec_in="01:00:10:00"),
    ]


@pytest.fixture
def sample_edl(sample_events):
    edl = EDL()
    edl.title = "TEST EDL"
    edl.fcm = "NON-DROP FRAME"
    edl.events = sample_events
    return edl


def test_reorder_by_field_event_number(sample_events):
    result = reorder_by_field(sample_events, "event_number")
    assert [e.event_number for e in result] == ["001", "002", "003"]


def test_reorder_by_field_reel(sample_events):
    result = reorder_by_field(sample_events, "reel")
    assert [e.reel for e in result] == ["REEL_A", "REEL_B", "REEL_C"]


def test_reorder_by_field_reverse(sample_events):
    result = reorder_by_field(sample_events, "event_number", reverse=True)
    assert [e.event_number for e in result] == ["003", "002", "001"]


def test_reorder_by_field_invalid_field_raises(sample_events):
    with pytest.raises(ReorderError, match="Unknown sort field"):
        reorder_by_field(sample_events, "nonexistent_field")


def test_reorder_by_custom_sequence(sample_events):
    result = reorder_by_custom_sequence(sample_events, ["REEL_B", "REEL_A", "REEL_C"])
    assert [e.reel for e in result] == ["REEL_B", "REEL_A", "REEL_C"]


def test_reorder_by_custom_sequence_unknown_reels_appended(sample_events):
    result = reorder_by_custom_sequence(sample_events, ["REEL_C"])
    assert result[0].reel == "REEL_C"
    assert {e.reel for e in result[1:]} == {"REEL_A", "REEL_B"}


def test_reorder_by_custom_sequence_empty_raises(sample_events):
    with pytest.raises(ReorderError, match="Sequence list must not be empty"):
        reorder_by_custom_sequence(sample_events, [])


def test_reorder_edl_events_by_field_returns_edl(sample_edl):
    result = reorder_edl_events(sample_edl, field="event_number")
    assert isinstance(result, EDL)
    assert result.title == sample_edl.title
    assert result.fcm == sample_edl.fcm


def test_reorder_edl_events_preserves_event_count(sample_edl):
    result = reorder_edl_events(sample_edl, field="reel")
    assert len(result.events) == len(sample_edl.events)


def test_reorder_edl_events_no_args_raises(sample_edl):
    with pytest.raises(ReorderError, match="Provide either"):
        reorder_edl_events(sample_edl)


def test_reorder_edl_events_both_args_raises(sample_edl):
    with pytest.raises(ReorderError, match="only one"):
        reorder_edl_events(sample_edl, field="reel", sequence=["REEL_A"])


def test_reorder_edl_events_by_sequence(sample_edl):
    result = reorder_edl_events(sample_edl, sequence=["REEL_B", "REEL_C", "REEL_A"])
    assert [e.reel for e in result.events] == ["REEL_B", "REEL_C", "REEL_A"]
