"""Tests for edl_parse.merger module."""

import json
import pytest

from edl_parse.parser import EDL, EDLEvent
from edl_parse.merger import merge_edls, MergeError, _renumber_events


def make_event(number: str, reel: str = "AX") -> EDLEvent:
    return EDLEvent(
        event_number=number,
        reel=reel,
        track="V",
        edit_type="C",
        source_in="01:00:00:00",
        source_out="01:00:05:00",
        record_in="01:00:00:00",
        record_out="01:00:05:00",
        clip_name=None,
        comments=[],
    )


def make_edl(title: str, event_numbers) -> EDL:
    edl = EDL(title=title, fcm="NON-DROP FRAME")
    edl.events = [make_event(n) for n in event_numbers]
    return edl


# --- _renumber_events ---

def test_renumber_events_sequential():
    events = [make_event("005"), make_event("010"), make_event("015")]
    result = _renumber_events(events, start=1)
    assert [e.event_number for e in result] == ["001", "002", "003"]


def test_renumber_events_preserves_other_fields():
    events = [make_event("099", reel="BX")]
    result = _renumber_events(events)
    assert result[0].reel == "BX"
    assert result[0].edit_type == "C"


# --- merge_edls ---

def test_merge_empty_list_raises():
    with pytest.raises(MergeError):
        merge_edls([])


def test_merge_single_edl_returns_all_events():
    edl = make_edl("REEL_A", ["001", "002", "003"])
    result = merge_edls([edl])
    assert len(result.events) == 3


def test_merge_two_edls_combines_events():
    edl1 = make_edl("REEL_A", ["001", "002"])
    edl2 = make_edl("REEL_B", ["001", "002", "003"])
    result = merge_edls([edl1, edl2])
    assert len(result.events) == 5


def test_merge_uses_first_title_by_default():
    edl1 = make_edl("FIRST", ["001"])
    edl2 = make_edl("SECOND", ["001"])
    result = merge_edls([edl1, edl2])
    assert result.title == "FIRST"


def test_merge_custom_title_overrides():
    edl1 = make_edl("FIRST", ["001"])
    edl2 = make_edl("SECOND", ["001"])
    result = merge_edls([edl1, edl2], title="MERGED")
    assert result.title == "MERGED"


def test_merge_renumbers_by_default():
    edl1 = make_edl("A", ["010", "020"])
    edl2 = make_edl("B", ["010", "020"])
    result = merge_edls([edl1, edl2])
    numbers = [e.event_number for e in result.events]
    assert numbers == ["001", "002", "003", "004"]


def test_merge_no_renumber_preserves_numbers():
    edl1 = make_edl("A", ["001", "002"])
    edl2 = make_edl("B", ["003", "004"])
    result = merge_edls([edl1, edl2], renumber=False)
    numbers = [e.event_number for e in result.events]
    assert numbers == ["001", "002", "003", "004"]


def test_merge_preserves_fcm_from_first():
    edl1 = make_edl("A", ["001"])
    edl1.fcm = "DROP FRAME"
    edl2 = make_edl("B", ["002"])
    edl2.fcm = "NON-DROP FRAME"
    result = merge_edls([edl1, edl2])
    assert result.fcm == "DROP FRAME"
