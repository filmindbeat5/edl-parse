"""Tests for edl_parse.grouper module."""

import pytest
from edl_parse.parser import EDL, EDLEvent
from edl_parse.grouper import (
    GroupError,
    group_events_by_field,
    group_edl_events,
    VALID_FIELDS,
)


def make_event(number="001", reel="A001", edit_type="C"):
    e = EDLEvent()
    e.event_number = number
    e.reel = reel
    e.edit_type = edit_type
    e.source_in = "01:00:00:00"
    e.source_out = "01:00:05:00"
    e.record_in = "00:00:00:00"
    e.record_out = "00:00:05:00"
    return e


@pytest.fixture
def sample_events():
    return [
        make_event("001", "A001", "C"),
        make_event("002", "A002", "D"),
        make_event("003", "A001", "C"),
        make_event("004", "B001", "D"),
    ]


@pytest.fixture
def sample_edl(sample_events):
    edl = EDL()
    edl.title = "TEST EDL"
    edl.fcm = "NON-DROP FRAME"
    edl.events = sample_events
    return edl


def test_group_events_by_reel_returns_dict(sample_events):
    result = group_events_by_field(sample_events, "reel")
    assert isinstance(result, dict)


def test_group_events_by_reel_keys(sample_events):
    result = group_events_by_field(sample_events, "reel")
    assert set(result.keys()) == {"A001", "A002", "B001"}


def test_group_events_by_reel_counts(sample_events):
    result = group_events_by_field(sample_events, "reel")
    assert len(result["A001"]) == 2
    assert len(result["A002"]) == 1
    assert len(result["B001"]) == 1


def test_group_events_by_edit_type(sample_events):
    result = group_events_by_field(sample_events, "edit_type")
    assert set(result.keys()) == {"C", "D"}
    assert len(result["C"]) == 2
    assert len(result["D"]) == 2


def test_group_events_invalid_field_raises(sample_events):
    with pytest.raises(GroupError):
        group_events_by_field(sample_events, "nonexistent_field")


def test_group_events_not_list_raises():
    with pytest.raises(GroupError):
        group_events_by_field("not a list", "reel")


def test_group_events_empty_list():
    result = group_events_by_field([], "reel")
    assert result == {}


def test_group_edl_events_returns_dict(sample_edl):
    result = group_edl_events(sample_edl, "reel")
    assert isinstance(result, dict)


def test_group_edl_events_sub_edl_title(sample_edl):
    result = group_edl_events(sample_edl, "reel")
    for sub_edl in result.values():
        assert sub_edl.title == "TEST EDL"


def test_group_edl_events_sub_edl_fcm(sample_edl):
    result = group_edl_events(sample_edl, "reel")
    for sub_edl in result.values():
        assert sub_edl.fcm == "NON-DROP FRAME"


def test_group_edl_events_sub_edl_events_are_edlevent(sample_edl):
    result = group_edl_events(sample_edl, "reel")
    for sub_edl in result.values():
        for event in sub_edl.events:
            assert isinstance(event, EDLEvent)


def test_group_error_str():
    err = GroupError("bad field")
    assert "GroupError" in str(err)
    assert "bad field" in str(err)


def test_valid_fields_set():
    assert "reel" in VALID_FIELDS
    assert "edit_type" in VALID_FIELDS
    assert "event_number" in VALID_FIELDS
