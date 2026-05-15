"""Tests for edl_parse.tagger module."""

import pytest
from edl_parse.parser import EDL, EDLEvent
from edl_parse.tagger import TagError, tag_event, tag_events, tag_edl_events


def make_event(
    number="001",
    reel="CAM_A",
    edit_type="V",
    src_in="01:00:00:00",
    src_out="01:00:05:00",
    rec_in="01:00:00:00",
    rec_out="01:00:05:00",
) -> EDLEvent:
    e = EDLEvent()
    e.number = number
    e.reel = reel
    e.edit_type = edit_type
    e.src_in = src_in
    e.src_out = src_out
    e.rec_in = rec_in
    e.rec_out = rec_out
    return e


@pytest.fixture
def sample_events():
    return [
        make_event(number="001", reel="CAM_A", edit_type="V"),
        make_event(number="002", reel="CAM_B", edit_type="V"),
        make_event(number="003", reel="CAM_A", edit_type="A"),
        make_event(number="004", reel="CAM_C", edit_type="V"),
    ]


@pytest.fixture
def sample_edl(sample_events):
    edl = EDL()
    edl.title = "TEST EDL"
    edl.fcm = "NON-DROP FRAME"
    edl.events = sample_events
    return edl


def test_tag_event_known_reel():
    event = make_event(reel="CAM_A")
    tag_event(event, {"CAM_A": "primary", "CAM_B": "secondary"})
    assert event.tag == "primary"


def test_tag_event_unknown_reel_sets_none():
    event = make_event(reel="CAM_Z")
    tag_event(event, {"CAM_A": "primary"})
    assert event.tag is None


def test_tag_event_case_insensitive():
    event = make_event(reel="cam_a")
    tag_event(event, {"CAM_A": "primary"})
    assert event.tag == "primary"


def test_tag_event_by_edit_type():
    event = make_event(edit_type="A")
    tag_event(event, {"A": "audio", "V": "video"}, field="edit_type")
    assert event.tag == "audio"


def test_tag_event_invalid_field_raises():
    event = make_event()
    with pytest.raises(TagError):
        tag_event(event, {"CAM_A": "primary"}, field="nonexistent_field")


def test_tag_event_none_reel_sets_none():
    event = make_event(reel=None)
    tag_event(event, {"CAM_A": "primary"})
    assert event.tag is None


def test_tag_events_all_tagged(sample_events):
    tags = {"CAM_A": "primary", "CAM_B": "secondary"}
    result = tag_events(sample_events, tags)
    assert result[0].tag == "primary"
    assert result[1].tag == "secondary"
    assert result[2].tag == "primary"
    assert result[3].tag is None


def test_tag_events_returns_same_list(sample_events):
    tags = {"CAM_A": "primary"}
    result = tag_events(sample_events, tags)
    assert result is sample_events


def test_tag_edl_events_tags_all(sample_edl):
    tags = {"CAM_A": "primary", "CAM_B": "secondary", "CAM_C": "tertiary"}
    result = tag_edl_events(sample_edl, tags)
    assert all(hasattr(e, "tag") for e in result.events)
    assert result.events[0].tag == "primary"
    assert result.events[3].tag == "tertiary"


def test_tag_edl_events_returns_same_edl(sample_edl):
    result = tag_edl_events(sample_edl, {"CAM_A": "primary"})
    assert result is sample_edl
