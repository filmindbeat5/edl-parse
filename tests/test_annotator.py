"""Tests for edl_parse.annotator module."""

import pytest
from edl_parse.parser import EDL, EDLEvent
from edl_parse.annotator import (
    AnnotationError,
    annotate_event,
    annotate_events,
    annotate_edl,
    get_annotations,
    remove_annotation,
)


def make_event(number: int = 1, notes=None) -> EDLEvent:
    return EDLEvent(
        event_number=number,
        reel="CAM001",
        edit_type="V",
        transition="C",
        source_in="01:00:00:00",
        source_out="01:00:05:00",
        record_in="01:00:00:00",
        record_out="01:00:05:00",
        notes=notes or [],
    )


def make_edl(num_events: int = 3) -> EDL:
    edl = EDL(title="Test EDL", fcm="NON-DROP FRAME")
    edl.events = [make_event(i + 1) for i in range(num_events)]
    return edl


# --- annotate_event ---

def test_annotate_event_adds_note():
    event = make_event()
    annotate_event(event, "scene", "42")
    assert "scene=42" in event.notes


def test_annotate_event_updates_existing_key():
    event = make_event(notes=["scene=10"])
    annotate_event(event, "scene", "99")
    assert "scene=99" in event.notes
    assert "scene=10" not in event.notes


def test_annotate_event_empty_key_raises():
    event = make_event()
    with pytest.raises(AnnotationError):
        annotate_event(event, "", "value")


def test_annotate_event_multiple_keys():
    event = make_event()
    annotate_event(event, "scene", "1")
    annotate_event(event, "take", "3")
    assert "scene=1" in event.notes
    assert "take=3" in event.notes


# --- annotate_events ---

def test_annotate_events_all():
    events = [make_event(i + 1) for i in range(3)]
    result = annotate_events(events, "status", "ok")
    assert all("status=ok" in e.notes for e in result)


def test_annotate_events_selective():
    events = [make_event(i + 1) for i in range(3)]
    annotate_events(events, "flag", "yes", event_numbers=[1, 3])
    assert "flag=yes" in events[0].notes
    assert "flag=yes" not in events[1].notes
    assert "flag=yes" in events[2].notes


def test_annotate_events_empty_key_raises():
    events = [make_event()]
    with pytest.raises(AnnotationError):
        annotate_events(events, "  ", "value")


# --- annotate_edl ---

def test_annotate_edl_returns_edl():
    edl = make_edl()
    result = annotate_edl(edl, "project", "alpha")
    assert isinstance(result, EDL)


def test_annotate_edl_all_events_annotated():
    edl = make_edl(3)
    annotate_edl(edl, "project", "alpha")
    assert all("project=alpha" in e.notes for e in edl.events)


# --- get_annotations ---

def test_get_annotations_returns_dict():
    event = make_event(notes=["scene=5", "take=2"])
    result = get_annotations(event)
    assert result == {"scene": "5", "take": "2"}


def test_get_annotations_ignores_non_kv_notes():
    event = make_event(notes=["just a comment", "key=val"])
    result = get_annotations(event)
    assert "key" in result
    assert len(result) == 1


# --- remove_annotation ---

def test_remove_annotation_removes_key():
    event = make_event(notes=["scene=3", "take=1"])
    remove_annotation(event, "scene")
    assert "scene=3" not in event.notes
    assert "take=1" in event.notes


def test_remove_annotation_no_op_if_missing():
    event = make_event(notes=["take=1"])
    remove_annotation(event, "scene")
    assert event.notes == ["take=1"]
