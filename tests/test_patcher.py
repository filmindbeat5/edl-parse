"""Tests for edl_parse.patcher module."""

import pytest
from edl_parse.parser import EDL, EDLEvent
from edl_parse.patcher import (
    PatchError,
    patch_event_by_number,
    patch_events_by_reel,
    patch_edl,
)


def make_event(number="001", reel="CAM_A", edit_type="C",
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


def make_edl(events=None):
    edl = EDL()
    edl.title = "TEST EDL"
    edl.fcm = "NON-DROP FRAME"
    edl.events = events or []
    return edl


@pytest.fixture
def sample_events():
    return [
        make_event("001", "CAM_A"),
        make_event("002", "CAM_B"),
        make_event("003", "CAM_A"),
    ]


@pytest.fixture
def sample_edl(sample_events):
    return make_edl(sample_events)


def test_patch_event_by_number_changes_reel(sample_events):
    patch_event_by_number(sample_events, "001", {"reel": "CAM_X"})
    assert sample_events[0].reel == "CAM_X"


def test_patch_event_by_number_does_not_affect_others(sample_events):
    patch_event_by_number(sample_events, "001", {"reel": "CAM_X"})
    assert sample_events[1].reel == "CAM_B"
    assert sample_events[2].reel == "CAM_A"


def test_patch_event_by_number_unknown_raises(sample_events):
    with pytest.raises(PatchError, match="No event found"):
        patch_event_by_number(sample_events, "999", {"reel": "CAM_X"})


def test_patch_event_by_number_bad_field_raises(sample_events):
    with pytest.raises(PatchError, match="no field"):
        patch_event_by_number(sample_events, "001", {"nonexistent_field": "val"})


def test_patch_event_by_number_empty_fields_raises(sample_events):
    with pytest.raises(PatchError, match="No fields"):
        patch_event_by_number(sample_events, "001", {})


def test_patch_events_by_reel_updates_all_matching(sample_events):
    patch_events_by_reel(sample_events, "CAM_A", {"edit_type": "D"})
    assert sample_events[0].edit_type == "D"
    assert sample_events[2].edit_type == "D"


def test_patch_events_by_reel_case_insensitive(sample_events):
    patch_events_by_reel(sample_events, "cam_a", {"edit_type": "D"})
    assert sample_events[0].edit_type == "D"


def test_patch_events_by_reel_no_match_unchanged(sample_events):
    patch_events_by_reel(sample_events, "CAM_Z", {"edit_type": "D"})
    for e in sample_events:
        assert e.edit_type == "C"


def test_patch_edl_by_event_number(sample_edl):
    result = patch_edl(sample_edl, event_number="002", fields={"reel": "NEW_REEL"})
    assert result.events[1].reel == "NEW_REEL"


def test_patch_edl_by_reel(sample_edl):
    result = patch_edl(sample_edl, reel="CAM_A", fields={"edit_type": "W"})
    assert result.events[0].edit_type == "W"
    assert result.events[2].edit_type == "W"


def test_patch_edl_both_args_raises(sample_edl):
    with pytest.raises(PatchError, match="not both"):
        patch_edl(sample_edl, event_number="001", reel="CAM_A", fields={"edit_type": "D"})


def test_patch_edl_no_target_raises(sample_edl):
    with pytest.raises(PatchError, match="Must specify"):
        patch_edl(sample_edl, fields={"edit_type": "D"})


def test_patch_edl_no_fields_raises(sample_edl):
    with pytest.raises(PatchError, match="No fields"):
        patch_edl(sample_edl, event_number="001", fields={})
