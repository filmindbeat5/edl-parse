"""Tests for edl_parse.replacer."""

import pytest
from edl_parse.parser import EDL, EDLEvent
from edl_parse.replacer import (
    ReplaceError,
    replace_field_value,
    replace_in_edl,
    ALLOWED_FIELDS,
)


def make_event(number="001", reel="CAM_A", edit_type="C",
               src_in="01:00:00:00", src_out="01:00:05:00",
               rec_in="01:00:00:00", rec_out="01:00:05:00"):
    e = EDLEvent(
        event_number=number,
        reel=reel,
        edit_type=edit_type,
        source_in=src_in,
        source_out=src_out,
        record_in=rec_in,
        record_out=rec_out,
    )
    return e


def make_edl(events=None):
    edl = EDL(title="TEST EDL", fcm="NON-DROP FRAME")
    edl.events = events or []
    return edl


def test_replace_field_value_reel():
    events = [make_event(reel="CAM_A"), make_event(number="002", reel="CAM_B")]
    result = replace_field_value(events, "reel", "CAM_A", "CAM_X")
    assert result[0].reel == "CAM_X"
    assert result[1].reel == "CAM_B"


def test_replace_field_value_no_match_unchanged():
    events = [make_event(reel="CAM_A")]
    result = replace_field_value(events, "reel", "CAM_Z", "CAM_X")
    assert result[0].reel == "CAM_A"


def test_replace_field_value_case_insensitive():
    events = [make_event(reel="cam_a")]
    result = replace_field_value(events, "reel", "CAM_A", "CAM_X", case_sensitive=False)
    assert result[0].reel == "CAM_X"


def test_replace_field_value_case_sensitive_no_match():
    events = [make_event(reel="cam_a")]
    result = replace_field_value(events, "reel", "CAM_A", "CAM_X", case_sensitive=True)
    assert result[0].reel == "cam_a"


def test_replace_field_value_invalid_field_raises():
    events = [make_event()]
    with pytest.raises(ReplaceError):
        replace_field_value(events, "nonexistent_field", "old", "new")


def test_replace_field_value_empty_old_value_raises():
    events = [make_event()]
    with pytest.raises(ReplaceError):
        replace_field_value(events, "reel", "", "new")


def test_replace_field_value_edit_type():
    events = [make_event(edit_type="C"), make_event(number="002", edit_type="D")]
    result = replace_field_value(events, "edit_type", "C", "W")
    assert result[0].edit_type == "W"
    assert result[1].edit_type == "D"


def test_replace_field_value_preserves_other_fields():
    events = [make_event(reel="CAM_A", edit_type="C")]
    result = replace_field_value(events, "reel", "CAM_A", "CAM_X")
    assert result[0].edit_type == "C"
    assert result[0].source_in == "01:00:00:00"


def test_replace_in_edl_returns_edl():
    edl = make_edl([make_event(reel="CAM_A")])
    result = replace_in_edl(edl, "reel", "CAM_A", "CAM_X")
    assert isinstance(result, EDL)


def test_replace_in_edl_preserves_title():
    edl = make_edl([make_event()])
    result = replace_in_edl(edl, "reel", "CAM_A", "CAM_X")
    assert result.title == "TEST EDL"


def test_replace_in_edl_updates_events():
    edl = make_edl([make_event(reel="CAM_A"), make_event(number="002", reel="CAM_A")])
    result = replace_in_edl(edl, "reel", "CAM_A", "CAM_NEW")
    assert all(e.reel == "CAM_NEW" for e in result.events)


def test_replace_in_edl_does_not_mutate_original():
    edl = make_edl([make_event(reel="CAM_A")])
    replace_in_edl(edl, "reel", "CAM_A", "CAM_X")
    assert edl.events[0].reel == "CAM_A"
