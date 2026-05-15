"""Tests for edl_parse.deduplicator."""

import pytest
from edl_parse.parser import EDL, EDLEvent
from edl_parse.deduplicator import (
    find_duplicates,
    remove_duplicates,
    deduplicate_edl,
)


def make_event(number, reel, src_in, src_out, rec_in, rec_out, edit_type="C"):
    e = EDLEvent()
    e.event_number = number
    e.reel = reel
    e.edit_type = edit_type
    e.source_in = src_in
    e.source_out = src_out
    e.record_in = rec_in
    e.record_out = rec_out
    return e


@pytest.fixture
def events():
    return [
        make_event("001", "A001", "01:00:00:00", "01:00:05:00", "00:00:00:00", "00:00:05:00"),
        make_event("002", "A002", "01:00:10:00", "01:00:15:00", "00:00:05:00", "00:00:10:00"),
        make_event("003", "A001", "01:00:00:00", "01:00:05:00", "00:00:00:00", "00:00:05:00"),  # dup of 001
        make_event("004", "A003", "01:00:20:00", "01:00:25:00", "00:00:10:00", "00:00:15:00"),
    ]


def test_find_duplicates_returns_groups(events):
    groups = find_duplicates(events)
    assert len(groups) == 1
    assert len(groups[0]) == 2


def test_find_duplicates_no_duplicates():
    e1 = make_event("001", "A001", "01:00:00:00", "01:00:05:00", "00:00:00:00", "00:00:05:00")
    e2 = make_event("002", "A002", "01:00:10:00", "01:00:15:00", "00:00:05:00", "00:00:10:00")
    assert find_duplicates([e1, e2]) == []


def test_find_duplicates_empty_list():
    """find_duplicates should return an empty list when given no events."""
    assert find_duplicates([]) == []


def test_remove_duplicates_keep_first(events):
    result = remove_duplicates(events, keep="first")
    assert len(result) == 3
    assert result[0].event_number == "001"


def test_remove_duplicates_keep_last(events):
    result = remove_duplicates(events, keep="last")
    assert len(result) == 3
    # The last occurrence of the duplicate pair is event 003
    numbers = [e.event_number for e in result]
    assert "003" in numbers
    assert "001" not in numbers


def test_remove_duplicates_invalid_keep(events):
    with pytest.raises(ValueError, match="keep must be"):
        remove_duplicates(events, keep="middle")


def test_remove_duplicates_preserves_order(events):
    result = remove_duplicates(events, keep="first")
    numbers = [e.event_number for e in result]
    assert numbers == sorted(numbers)


def test_remove_duplicates_empty_list():
    """remove_duplicates should return an empty list when given no events."""
    assert remove_duplicates([], keep="first") == []


def test_deduplicate_edl_returns_edl(events):
    edl = EDL(title="TEST EDL", fcm="NON-DROP FRAME")
    edl.events = events
    result = deduplicate_edl(edl)
    assert isinstance(result, EDL)


def test_deduplicate_edl_preserves_metadata(events):
    edl = EDL(title="MY SHOW", fcm="DROP FRAME")
    edl.events = events
    result = deduplicate_edl(edl)
    assert result.title == "MY SHOW"
    assert result.fcm == "DROP FRAME"


def test_deduplicate_edl_renumbers_events(events):
    edl = EDL(title="TEST", fcm="NON-DROP FRAME")
    edl.events = events
    result = deduplicate_edl(edl)
    for idx, event in enumerate(result.events, start=1):
        assert event.event_number == str(idx).zfill(3)


def test_deduplicate_edl_correct_count(events):
    edl = EDL(title="TEST", fcm="NON-DROP FRAME")
    edl.events = events
    result = deduplicate_edl(edl)
    assert len(result.events) == 3
