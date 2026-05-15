"""Tests for edl_parse.mapper."""

import pytest
from edl_parse.parser import EDLEvent, EDL
from edl_parse.mapper import (
    MapError,
    map_event_fields,
    map_events,
    map_edl_events,
)


def make_event(
    number="001",
    reel="CAM_A",
    edit_type="V",
    transition="C",
    source_in="01:00:00:00",
    source_out="01:00:05:00",
    record_in="00:00:00:00",
    record_out="00:00:05:00",
) -> EDLEvent:
    e = EDLEvent()
    e.event_number = number
    e.reel = reel
    e.edit_type = edit_type
    e.transition = transition
    e.source_in = source_in
    e.source_out = source_out
    e.record_in = record_in
    e.record_out = record_out
    return e


@pytest.fixture
def sample_events():
    return [
        make_event(number="001", reel="CAM_A"),
        make_event(number="002", reel="CAM_B"),
    ]


@pytest.fixture
def sample_edl(sample_events):
    edl = EDL()
    edl.title = "TEST EDL"
    edl.fcm = "NON-DROP FRAME"
    edl.events = sample_events
    return edl


def test_map_event_fields_renames_reel():
    event = make_event(reel="CAM_A")
    result = map_event_fields(event, {"reel": "tape_name"})
    assert "tape_name" in result
    assert result["tape_name"] == "CAM_A"
    assert "reel" not in result


def test_map_event_fields_renames_multiple():
    event = make_event(reel="CAM_A", edit_type="V")
    result = map_event_fields(event, {"reel": "tape", "edit_type": "track_type"})
    assert result["tape"] == "CAM_A"
    assert result["track_type"] == "V"


def test_map_event_fields_drop_unmapped():
    event = make_event(reel="CAM_A")
    result = map_event_fields(event, {"reel": "tape"}, drop_unmapped=True)
    assert list(result.keys()) == ["tape"]


def test_map_event_fields_keeps_unmapped_by_default():
    event = make_event(reel="CAM_A")
    result = map_event_fields(event, {"reel": "tape"})
    assert "event_number" in result
    assert "source_in" in result


def test_map_event_fields_empty_map_raises():
    event = make_event()
    with pytest.raises(MapError):
        map_event_fields(event, {})


def test_map_events_returns_list(sample_events):
    result = map_events(sample_events, {"reel": "tape"})
    assert isinstance(result, list)
    assert len(result) == 2


def test_map_events_all_renamed(sample_events):
    result = map_events(sample_events, {"reel": "tape"}, drop_unmapped=True)
    for row in result:
        assert "tape" in row
        assert "reel" not in row


def test_map_edl_events_returns_list(sample_edl):
    result = map_edl_events(sample_edl, {"reel": "tape"})
    assert isinstance(result, list)
    assert len(result) == len(sample_edl.events)


def test_map_edl_events_empty_edl_raises():
    edl = EDL()
    edl.title = "EMPTY"
    edl.fcm = "NON-DROP FRAME"
    edl.events = []
    with pytest.raises(MapError):
        map_edl_events(edl, {"reel": "tape"})


def test_map_error_str():
    err = MapError("something went wrong")
    assert "MapError" in str(err)
    assert "something went wrong" in str(err)
