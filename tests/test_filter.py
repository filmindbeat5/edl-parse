"""Tests for edl_parse.filter module."""

import pytest
from edl_parse.parser import EDL, EDLEvent
from edl_parse.filter import (
    filter_by_reel,
    filter_by_edit_type,
    filter_by_event_number_range,
    filter_events,
    filter_edl_events,
)


def make_event(number, reel, edit_type="C"):
    e = EDLEvent()
    e.event_number = str(number)
    e.reel = reel
    e.edit_type = edit_type
    e.track = "V"
    e.source_in = "01:00:00:00"
    e.source_out = "01:00:05:00"
    e.record_in = "01:00:00:00"
    e.record_out = "01:00:05:00"
    return e


@pytest.fixture
def sample_events():
    return [
        make_event(1, "REEL_A", "C"),
        make_event(2, "REEL_B", "D"),
        make_event(3, "REEL_A", "C"),
        make_event(4, "REEL_C", "C"),
        make_event(5, "REEL_B", "C"),
    ]


@pytest.fixture
def sample_edl(sample_events):
    edl = EDL()
    edl.title = "TEST EDL"
    edl.fcm = "NON-DROP FRAME"
    edl.events = sample_events
    return edl


def test_filter_by_reel(sample_events):
    result = filter_by_reel(sample_events, "REEL_A")
    assert len(result) == 2
    assert all(e.reel == "REEL_A" for e in result)


def test_filter_by_reel_case_insensitive(sample_events):
    result = filter_by_reel(sample_events, "reel_a")
    assert len(result) == 2


def test_filter_by_reel_no_match(sample_events):
    result = filter_by_reel(sample_events, "REEL_Z")
    assert result == []


def test_filter_by_edit_type(sample_events):
    result = filter_by_edit_type(sample_events, "D")
    assert len(result) == 1
    assert result[0].event_number == "2"


def test_filter_by_edit_type_case_insensitive(sample_events):
    result = filter_by_edit_type(sample_events, "c")
    assert len(result) == 4


def test_filter_by_event_number_range(sample_events):
    result = filter_by_event_number_range(sample_events, start=2, end=4)
    assert len(result) == 3
    assert [e.event_number for e in result] == ["2", "3", "4"]


def test_filter_by_event_number_range_open_end(sample_events):
    result = filter_by_event_number_range(sample_events, start=3)
    assert len(result) == 3


def test_filter_events_combined(sample_events):
    result = filter_events(sample_events, reel="REEL_A", edit_type="C")
    assert len(result) == 2


def test_filter_events_custom(sample_events):
    result = filter_events(sample_events, custom=lambda e: int(e.event_number) % 2 == 0)
    assert len(result) == 2
    assert all(int(e.event_number) % 2 == 0 for e in result)


def test_filter_edl_events_preserves_metadata(sample_edl):
    new_edl = filter_edl_events(sample_edl, reel="REEL_B")
    assert new_edl.title == "TEST EDL"
    assert new_edl.fcm == "NON-DROP FRAME"
    assert len(new_edl.events) == 2


def test_filter_edl_events_returns_new_instance(sample_edl):
    new_edl = filter_edl_events(sample_edl, reel="REEL_A")
    assert new_edl is not sample_edl
    assert len(sample_edl.events) == 5
