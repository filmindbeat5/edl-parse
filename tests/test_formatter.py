"""Tests for edl_parse.formatter module."""

import pytest
from edl_parse.parser import EDL, EDLEvent
from edl_parse.formatter import (
    format_timecode_row,
    format_event_block,
    format_edl_table,
    format_edl_summary,
)


@pytest.fixture
def sample_event():
    event = EDLEvent()
    event.number = 1
    event.reel = "AX"
    event.track = "V"
    event.edit_type = "C"
    event.source_in = "01:00:00:00"
    event.source_out = "01:00:05:00"
    event.record_in = "00:00:00:00"
    event.record_out = "00:00:05:00"
    event.clip_name = "my_clip"
    event.comments = ["* FROM CLIP NAME: my_clip"]
    return event


@pytest.fixture
def sample_edl(sample_event):
    edl = EDL()
    edl.title = "TEST EDL"
    edl.fcm = "NON-DROP FRAME"
    edl.events = [sample_event]
    return edl


def test_format_timecode_row_contains_reel(sample_event):
    row = format_timecode_row(sample_event)
    assert "AX" in row


def test_format_timecode_row_contains_timecodes(sample_event):
    row = format_timecode_row(sample_event)
    assert "01:00:00:00" in row
    assert "00:00:05:00" in row


def test_format_timecode_row_contains_edit_type(sample_event):
    row = format_timecode_row(sample_event)
    assert "C" in row


def test_format_event_block_contains_all_fields(sample_event):
    block = format_event_block(sample_event)
    assert "AX" in block
    assert "my_clip" in block
    assert "01:00:00:00" in block
    assert "FROM CLIP NAME" in block


def test_format_event_block_no_clip_name():
    event = EDLEvent()
    event.number = 2
    event.reel = "BX"
    event.track = "V"
    event.edit_type = "C"
    event.source_in = "00:00:00:00"
    event.source_out = "00:00:01:00"
    event.record_in = "00:00:00:00"
    event.record_out = "00:00:01:00"
    event.clip_name = None
    event.comments = []
    block = format_event_block(event)
    assert "Clip" not in block
    assert "Comment" not in block


def test_format_edl_table_contains_title(sample_edl):
    table = format_edl_table(sample_edl)
    assert "TEST EDL" in table


def test_format_edl_table_contains_fcm(sample_edl):
    table = format_edl_table(sample_edl)
    assert "NON-DROP FRAME" in table


def test_format_edl_table_contains_event_row(sample_edl):
    table = format_edl_table(sample_edl)
    assert "AX" in table


def test_format_edl_summary_event_count(sample_edl):
    summary = format_edl_summary(sample_edl)
    assert "Events    : 1" in summary


def test_format_edl_summary_reel_list(sample_edl):
    summary = format_edl_summary(sample_edl)
    assert "AX" in summary


def test_format_edl_summary_no_title():
    edl = EDL()
    edl.title = None
    edl.fcm = None
    edl.events = []
    summary = format_edl_summary(edl)
    assert "(none)" in summary
