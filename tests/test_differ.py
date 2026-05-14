"""Tests for edl_parse.differ."""

import pytest
from edl_parse.parser import EDL, EDLEvent
from edl_parse.differ import EDLDiff, DiffError, diff_edls, diff_summary


def make_event(number, reel="A001", edit_type="C",
               src_in="01:00:00:00", src_out="01:00:05:00",
               rec_in="01:00:00:00", rec_out="01:00:05:00"):
    e = EDLEvent()
    e.event_number = number
    e.reel = reel
    e.edit_type = edit_type
    e.source_in = src_in
    e.source_out = src_out
    e.record_in = rec_in
    e.record_out = rec_out
    return e


def make_edl(events):
    edl = EDL()
    edl.title = "TEST"
    edl.fcm = "NON-DROP FRAME"
    edl.events = events
    return edl


@pytest.fixture
def base_edl():
    return make_edl([
        make_event(1, reel="A001"),
        make_event(2, reel="A002"),
        make_event(3, reel="A003"),
    ])


@pytest.fixture
def identical_edl():
    return make_edl([
        make_event(1, reel="A001"),
        make_event(2, reel="A002"),
        make_event(3, reel="A003"),
    ])


def test_diff_identical_edls_no_differences(base_edl, identical_edl):
    result = diff_edls(base_edl, identical_edl)
    assert not result.has_differences


def test_diff_added_event(base_edl):
    updated = make_edl([
        make_event(1, reel="A001"),
        make_event(2, reel="A002"),
        make_event(3, reel="A003"),
        make_event(4, reel="A004"),
    ])
    result = diff_edls(base_edl, updated)
    assert len(result.added) == 1
    assert result.added[0].event_number == 4


def test_diff_removed_event(base_edl):
    updated = make_edl([
        make_event(1, reel="A001"),
        make_event(3, reel="A003"),
    ])
    result = diff_edls(base_edl, updated)
    assert len(result.removed) == 1
    assert result.removed[0].event_number == 2


def test_diff_changed_event(base_edl):
    updated = make_edl([
        make_event(1, reel="A001"),
        make_event(2, reel="CHANGED"),
        make_event(3, reel="A003"),
    ])
    result = diff_edls(base_edl, updated)
    assert len(result.changed) == 1
    old, new = result.changed[0]
    assert old.reel == "A002"
    assert new.reel == "CHANGED"


def test_diff_raises_on_non_edl():
    edl = make_edl([])
    with pytest.raises(DiffError):
        diff_edls(edl, "not an edl")


def test_diff_summary_no_differences(base_edl, identical_edl):
    result = diff_edls(base_edl, identical_edl)
    summary = diff_summary(result)
    assert "No differences found." in summary


def test_diff_summary_counts(base_edl):
    updated = make_edl([
        make_event(1, reel="CHANGED"),
        make_event(4, reel="NEW"),
    ])
    result = diff_edls(base_edl, updated)
    summary = diff_summary(result)
    assert "Added:   1" in summary
    assert "Removed: 2" in summary
    assert "Changed: 1" in summary


def test_diff_empty_edls():
    result = diff_edls(make_edl([]), make_edl([]))
    assert not result.has_differences


def test_diff_all_added():
    result = diff_edls(make_edl([]), make_edl([make_event(1), make_event(2)]))
    assert len(result.added) == 2
    assert len(result.removed) == 0
