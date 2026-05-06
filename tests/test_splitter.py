"""Tests for edl_parse.splitter module."""

import pytest
from edl_parse.parser import EDL, EDLEvent
from edl_parse.splitter import (
    SplitError,
    split_by_reel,
    split_by_edit_type,
    split_into_chunks,
)


def make_event(number, reel, edit_type="C", src_in="01:00:00:00",
               src_out="01:00:05:00", rec_in="01:00:00:00", rec_out="01:00:05:00"):
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
def sample_edl():
    edl = EDL()
    edl.title = "TEST EDL"
    edl.fcm = "NON-DROP FRAME"
    edl.events = [
        make_event(1, "REEL_A", "C"),
        make_event(2, "REEL_B", "D"),
        make_event(3, "REEL_A", "C"),
        make_event(4, "REEL_C", "W"),
        make_event(5, "REEL_B", "C"),
    ]
    return edl


# --- split_by_reel ---

def test_split_by_reel_returns_dict(sample_edl):
    result = split_by_reel(sample_edl)
    assert isinstance(result, dict)


def test_split_by_reel_keys(sample_edl):
    result = split_by_reel(sample_edl)
    assert set(result.keys()) == {"REEL_A", "REEL_B", "REEL_C"}


def test_split_by_reel_event_counts(sample_edl):
    result = split_by_reel(sample_edl)
    assert len(result["REEL_A"].events) == 2
    assert len(result["REEL_B"].events) == 2
    assert len(result["REEL_C"].events) == 1


def test_split_by_reel_preserves_title(sample_edl):
    result = split_by_reel(sample_edl)
    for child in result.values():
        assert child.title == "TEST EDL"


def test_split_by_reel_empty_raises():
    edl = EDL()
    edl.events = []
    with pytest.raises(SplitError):
        split_by_reel(edl)


# --- split_by_edit_type ---

def test_split_by_edit_type_keys(sample_edl):
    result = split_by_edit_type(sample_edl)
    assert set(result.keys()) == {"C", "D", "W"}


def test_split_by_edit_type_counts(sample_edl):
    result = split_by_edit_type(sample_edl)
    assert len(result["C"].events) == 3
    assert len(result["D"].events) == 1
    assert len(result["W"].events) == 1


def test_split_by_edit_type_empty_raises():
    edl = EDL()
    edl.events = []
    with pytest.raises(SplitError):
        split_by_edit_type(edl)


# --- split_into_chunks ---

def test_split_into_chunks_count(sample_edl):
    chunks = split_into_chunks(sample_edl, 2)
    assert len(chunks) == 3


def test_split_into_chunks_sizes(sample_edl):
    chunks = split_into_chunks(sample_edl, 2)
    assert len(chunks[0].events) == 2
    assert len(chunks[1].events) == 2
    assert len(chunks[2].events) == 1


def test_split_into_chunks_single_chunk(sample_edl):
    chunks = split_into_chunks(sample_edl, 10)
    assert len(chunks) == 1
    assert len(chunks[0].events) == 5


def test_split_into_chunks_invalid_size_raises(sample_edl):
    with pytest.raises(SplitError):
        split_into_chunks(sample_edl, 0)


def test_split_into_chunks_empty_raises():
    edl = EDL()
    edl.events = []
    with pytest.raises(SplitError):
        split_into_chunks(edl, 2)
