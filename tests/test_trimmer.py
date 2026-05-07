"""Tests for edl_parse.trimmer module."""

import pytest
from edl_parse.parser import EDL, EDLEvent
from edl_parse.trimmer import TrimError, trim_events, trim_edl


def make_event(num, rec_in, rec_out, reel="CAM1", edit_type="C"):
    e = EDLEvent()
    e.event_number = num
    e.reel = reel
    e.track = "V"
    e.edit_type = edit_type
    e.src_in = "00:00:00:00"
    e.src_out = "00:00:01:00"
    e.rec_in = rec_in
    e.rec_out = rec_out
    return e


@pytest.fixture
def sample_events():
    return [
        make_event(1, "01:00:00:00", "01:00:10:00"),
        make_event(2, "01:00:10:00", "01:00:20:00"),
        make_event(3, "01:00:20:00", "01:00:30:00"),
        make_event(4, "01:00:30:00", "01:00:40:00"),
    ]


@pytest.fixture
def sample_edl(sample_events):
    edl = EDL(title="TRIM TEST", fcm="NON-DROP FRAME")
    edl.events = sample_events
    return edl


def test_trim_events_no_args_raises(sample_events):
    with pytest.raises(TrimError):
        trim_events(sample_events)


def test_trim_events_start_only(sample_events):
    result = trim_events(sample_events, start_tc="01:00:15:00")
    assert len(result) == 3
    assert result[0].event_number == 2


def test_trim_events_end_only(sample_events):
    result = trim_events(sample_events, end_tc="01:00:25:00")
    assert len(result) == 3
    assert result[-1].event_number == 3


def test_trim_events_start_and_end(sample_events):
    result = trim_events(
        sample_events, start_tc="01:00:10:00", end_tc="01:00:30:00"
    )
    assert len(result) == 2
    assert result[0].event_number == 2
    assert result[1].event_number == 3


def test_trim_events_end_before_start_raises(sample_events):
    with pytest.raises(TrimError, match="must be after"):
        trim_events(sample_events, start_tc="01:00:30:00", end_tc="01:00:10:00")


def test_trim_events_equal_start_end_raises(sample_events):
    with pytest.raises(TrimError):
        trim_events(sample_events, start_tc="01:00:10:00", end_tc="01:00:10:00")


def test_trim_events_returns_empty_when_out_of_range(sample_events):
    result = trim_events(sample_events, start_tc="02:00:00:00")
    assert result == []


def test_trim_edl_preserves_title(sample_edl):
    result = trim_edl(sample_edl, start_tc="01:00:10:00")
    assert result.title == "TRIM TEST"


def test_trim_edl_preserves_fcm(sample_edl):
    result = trim_edl(sample_edl, end_tc="01:00:25:00")
    assert result.fcm == "NON-DROP FRAME"


def test_trim_edl_returns_edl_instance(sample_edl):
    result = trim_edl(sample_edl, start_tc="01:00:00:00", end_tc="01:00:20:00")
    assert isinstance(result, EDL)


def test_trim_edl_event_count(sample_edl):
    result = trim_edl(sample_edl, start_tc="01:00:10:00", end_tc="01:00:30:00")
    assert len(result.events) == 2
