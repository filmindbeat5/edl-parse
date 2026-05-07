"""Tests for edl_parse.renamer module."""

import pytest
from edl_parse.parser import EDL, EDLEvent
from edl_parse.renamer import (
    RenameError,
    rename_reel,
    rename_reels_in_edl,
    build_reel_map_from_prefix,
)


def make_event(reel="CAM_A", event_number="001"):
    return EDLEvent(
        event_number=event_number,
        reel=reel,
        edit_type="V",
        transition="C",
        source_in="01:00:00:00",
        source_out="01:00:05:00",
        record_in="00:00:00:00",
        record_out="00:00:05:00",
    )


def make_edl(events=None):
    edl = EDL(title="TEST EDL", fcm="NON-DROP FRAME")
    edl.events = events or [make_event()]
    return edl


def test_rename_reel_replaces_known_reel():
    event = make_event(reel="CAM_A")
    result = rename_reel(event, {"CAM_A": "REEL_001"})
    assert result.reel == "REEL_001"


def test_rename_reel_preserves_unknown_reel():
    event = make_event(reel="CAM_B")
    result = rename_reel(event, {"CAM_A": "REEL_001"})
    assert result.reel == "CAM_B"


def test_rename_reel_preserves_other_fields():
    event = make_event(reel="CAM_A")
    result = rename_reel(event, {"CAM_A": "REEL_001"})
    assert result.event_number == event.event_number
    assert result.source_in == event.source_in
    assert result.record_out == event.record_out


def test_rename_reels_in_edl_returns_new_edl():
    edl = make_edl([make_event(reel="CAM_A"), make_event(reel="CAM_B", event_number="002")])
    result = rename_reels_in_edl(edl, {"CAM_A": "REEL_001", "CAM_B": "REEL_002"})
    assert isinstance(result, EDL)
    assert result is not edl


def test_rename_reels_in_edl_renames_all_events():
    edl = make_edl([make_event(reel="CAM_A"), make_event(reel="CAM_A", event_number="002")])
    result = rename_reels_in_edl(edl, {"CAM_A": "REEL_001"})
    assert all(e.reel == "REEL_001" for e in result.events)


def test_rename_reels_in_edl_preserves_title_and_fcm():
    edl = make_edl()
    result = rename_reels_in_edl(edl, {"CAM_A": "REEL_001"})
    assert result.title == edl.title
    assert result.fcm == edl.fcm


def test_rename_reels_in_edl_empty_map_raises():
    edl = make_edl()
    with pytest.raises(RenameError):
        rename_reels_in_edl(edl, {})


def test_build_reel_map_from_prefix():
    events = [make_event(reel="A"), make_event(reel="B"), make_event(reel="A")]
    reel_map = build_reel_map_from_prefix(events, "PRJ_")
    assert reel_map["A"] == "PRJ_A"
    assert reel_map["B"] == "PRJ_B"
    assert len(reel_map) == 2


def test_build_reel_map_from_prefix_empty_events():
    result = build_reel_map_from_prefix([], "PRJ_")
    assert result == {}
