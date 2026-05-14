"""Tests for edl_parse.exporter."""

import pytest

from edl_parse.parser import EDL, EDLEvent
from edl_parse.exporter import (
    ExportError,
    events_to_csv,
    edl_to_csv,
    edl_to_tsv,
    EVENT_FIELDS,
)


def make_event(n, reel="A001", edit_type="C"):
    e = EDLEvent()
    e.event_number = str(n).zfill(3)
    e.reel = reel
    e.track = "V"
    e.edit_type = edit_type
    e.source_in = "01:00:00:00"
    e.source_out = "01:00:05:00"
    e.record_in = "00:00:10:00"
    e.record_out = "00:00:15:00"
    return e


@pytest.fixture
def sample_events():
    return [make_event(1), make_event(2, reel="B002"), make_event(3, edit_type="D")]


@pytest.fixture
def sample_edl(sample_events):
    edl = EDL()
    edl.title = "TEST EDL"
    edl.fcm = "NON-DROP FRAME"
    edl.events = sample_events
    return edl


def test_events_to_csv_returns_string(sample_events):
    result = events_to_csv(sample_events)
    assert isinstance(result, str)


def test_events_to_csv_header_present(sample_events):
    result = events_to_csv(sample_events, include_header=True)
    first_line = result.splitlines()[0]
    for field in EVENT_FIELDS:
        assert field in first_line


def test_events_to_csv_no_header(sample_events):
    result = events_to_csv(sample_events, include_header=False)
    first_line = result.splitlines()[0]
    assert "event_number" not in first_line


def test_events_to_csv_row_count(sample_events):
    result = events_to_csv(sample_events, include_header=True)
    lines = [l for l in result.splitlines() if l]
    # 1 header + 3 data rows
    assert len(lines) == 4


def test_events_to_csv_reel_in_output(sample_events):
    result = events_to_csv(sample_events)
    assert "A001" in result
    assert "B002" in result


def test_events_to_csv_empty_raises():
    with pytest.raises(ExportError, match="empty"):
        events_to_csv([])


def test_events_to_csv_bad_delimiter(sample_events):
    with pytest.raises(ExportError, match="Unsupported delimiter"):
        events_to_csv(sample_events, delimiter="@")


def test_edl_to_csv_uses_all_events(sample_edl):
    result = edl_to_csv(sample_edl)
    lines = [l for l in result.splitlines() if l]
    assert len(lines) == 4  # header + 3 events


def test_edl_to_tsv_tab_delimited(sample_edl):
    result = edl_to_tsv(sample_edl)
    first_line = result.splitlines()[0]
    assert "\t" in first_line


def test_edl_to_tsv_no_header(sample_edl):
    result = edl_to_tsv(sample_edl, include_header=False)
    lines = [l for l in result.splitlines() if l]
    assert len(lines) == 3
