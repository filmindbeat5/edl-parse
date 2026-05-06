"""Tests for edl_parse.sorter module."""

import pytest
from edl_parse.parser import EDL, EDLEvent
from edl_parse.sorter import (
    _timecode_to_frames,
    sort_events_by_record_in,
    sort_events_by_source_in,
    sort_edl_events,
)


def make_event(num, reel, source_in, source_out, record_in, record_out):
    e = EDLEvent()
    e.num = num
    e.reel = reel
    e.track = "V"
    e.edit_type = "C"
    e.source_in = source_in
    e.source_out = source_out
    e.record_in = record_in
    e.record_out = record_out
    return e


@pytest.fixture
def sample_events():
    return [
        make_event("001", "REEL1", "01:00:00:00", "01:00:05:00", "01:00:10:00", "01:00:15:00"),
        make_event("002", "REEL2", "00:30:00:00", "00:30:05:00", "00:59:00:00", "00:59:05:00"),
        make_event("003", "REEL3", "02:00:00:00", "02:00:05:00", "01:30:00:00", "01:30:05:00"),
    ]


@pytest.fixture
def sample_edl(sample_events):
    edl = EDL()
    edl.title = "TEST EDL"
    edl.fcm = "NON-DROP FRAME"
    edl.events = sample_events
    return edl


def test_timecode_to_frames_basic():
    assert _timecode_to_frames("00:00:01:00", fps=25) == 25


def test_timecode_to_frames_hours():
    assert _timecode_to_frames("01:00:00:00", fps=25) == 3600 * 25


def test_timecode_to_frames_semicolon_separator():
    assert _timecode_to_frames("00:00:01;10", fps=25) == 35


def test_timecode_to_frames_invalid():
    with pytest.raises(ValueError):
        _timecode_to_frames("bad_timecode")


def test_sort_events_by_record_in_ascending(sample_events):
    result = sort_events_by_record_in(sample_events, fps=25)
    record_ins = [e.record_in for e in result]
    assert record_ins == ["00:59:00:00", "01:00:10:00", "01:30:00:00"]


def test_sort_events_by_record_in_descending(sample_events):
    result = sort_events_by_record_in(sample_events, fps=25, reverse=True)
    assert result[0].record_in == "01:30:00:00"


def test_sort_events_by_source_in_ascending(sample_events):
    result = sort_events_by_source_in(sample_events, fps=25)
    source_ins = [e.source_in for e in result]
    assert source_ins == ["00:30:00:00", "01:00:00:00", "02:00:00:00"]


def test_sort_edl_events_returns_new_edl(sample_edl):
    result = sort_edl_events(sample_edl, key="record_in")
    assert isinstance(result, EDL)
    assert result is not sample_edl


def test_sort_edl_events_preserves_metadata(sample_edl):
    result = sort_edl_events(sample_edl, key="record_in")
    assert result.title == sample_edl.title
    assert result.fcm == sample_edl.fcm


def test_sort_edl_events_invalid_key(sample_edl):
    with pytest.raises(ValueError, match="Unsupported sort key"):
        sort_edl_events(sample_edl, key="invalid_key")


def test_sort_edl_events_does_not_mutate_original(sample_edl):
    original_order = [e.record_in for e in sample_edl.events]
    sort_edl_events(sample_edl, key="record_in")
    assert [e.record_in for e in sample_edl.events] == original_order
