"""Tests for edl_parse.statistics module."""

import pytest
from edl_parse.parser import EDL, EDLEvent
from edl_parse.statistics import (
    StatisticsError,
    event_count,
    reel_counts,
    edit_type_counts,
    total_source_duration,
    total_record_duration,
    edl_statistics,
)


def make_event(num, reel, edit_type, src_in, src_out, rec_in, rec_out):
    e = EDLEvent()
    e.event_number = num
    e.reel = reel
    e.edit_type = edit_type
    e.transition = "C"
    e.source_in = src_in
    e.source_out = src_out
    e.record_in = rec_in
    e.record_out = rec_out
    return e


@pytest.fixture
def sample_edl():
    edl = EDL()
    edl.title = "TEST EDL"
    edl.fcm = "NON-DROP FRAME"
    edl.events = [
        make_event(1, "REEL_A", "V", "00:00:01:00", "00:00:05:00", "01:00:00:00", "01:00:04:00"),
        make_event(2, "REEL_B", "V", "00:00:10:00", "00:00:15:00", "01:00:04:00", "01:00:09:00"),
        make_event(3, "REEL_A", "A", "00:00:20:00", "00:00:22:00", "01:00:09:00", "01:00:11:00"),
    ]
    return edl


def test_event_count(sample_edl):
    assert event_count(sample_edl) == 3


def test_reel_counts(sample_edl):
    counts = reel_counts(sample_edl)
    assert counts["REEL_A"] == 2
    assert counts["REEL_B"] == 1


def test_edit_type_counts(sample_edl):
    counts = edit_type_counts(sample_edl)
    assert counts["V"] == 2
    assert counts["A"] == 1


def test_total_source_duration(sample_edl):
    # Event 1: 4s, Event 2: 5s, Event 3: 2s => 11s @ 25fps = 275 frames = 00:00:11:00
    result = total_source_duration(sample_edl, fps=25)
    assert result == "00:00:11:00"


def test_total_record_duration(sample_edl):
    # Event 1: 4s, Event 2: 5s, Event 3: 2s => 11s @ 25fps = 00:00:11:00
    result = total_record_duration(sample_edl, fps=25)
    assert result == "00:00:11:00"


def test_total_source_duration_empty_raises():
    edl = EDL()
    edl.events = []
    with pytest.raises(StatisticsError):
        total_source_duration(edl)


def test_total_record_duration_empty_raises():
    edl = EDL()
    edl.events = []
    with pytest.raises(StatisticsError):
        total_record_duration(edl)


def test_edl_statistics_keys(sample_edl):
    stats = edl_statistics(sample_edl)
    expected_keys = {
        "title", "fcm", "event_count",
        "reel_counts", "edit_type_counts",
        "total_source_duration", "total_record_duration",
    }
    assert set(stats.keys()) == expected_keys


def test_edl_statistics_title(sample_edl):
    stats = edl_statistics(sample_edl)
    assert stats["title"] == "TEST EDL"


def test_edl_statistics_empty_raises():
    edl = EDL()
    edl.events = []
    with pytest.raises(StatisticsError):
        edl_statistics(edl)
