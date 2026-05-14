"""Tests for edl_parse.importer."""

import textwrap
import pytest

from edl_parse.importer import csv_to_events, csv_to_edl, tsv_to_edl, ImportError
from edl_parse.parser import EDL, EDLEvent


CSV_DATA = textwrap.dedent("""\
    event_number,reel,edit_type,source_in,source_out,record_in,record_out
    001,REEL01,C,01:00:00:00,01:00:05:00,00:00:00:00,00:00:05:00
    002,REEL02,C,02:00:00:00,02:00:10:00,00:00:05:00,00:00:15:00
""")

TSV_DATA = CSV_DATA.replace(",", "\t")

CSV_WITH_NOTE = textwrap.dedent("""\
    event_number,reel,edit_type,source_in,source_out,record_in,record_out,note
    001,REEL01,C,01:00:00:00,01:00:05:00,00:00:00:00,00:00:05:00,my note
""")


def test_csv_to_events_returns_list():
    events = csv_to_events(CSV_DATA)
    assert isinstance(events, list)


def test_csv_to_events_count():
    events = csv_to_events(CSV_DATA)
    assert len(events) == 2


def test_csv_to_events_fields():
    events = csv_to_events(CSV_DATA)
    e = events[0]
    assert e.event_number == "001"
    assert e.reel == "REEL01"
    assert e.edit_type == "C"
    assert e.source_in == "01:00:00:00"
    assert e.record_out == "00:00:05:00"


def test_csv_to_events_note_field():
    events = csv_to_events(CSV_WITH_NOTE)
    assert events[0].note == "my note"


def test_csv_to_events_missing_field_raises():
    bad_csv = "event_number,reel\n001,REEL01\n"
    with pytest.raises(ImportError):
        csv_to_events(bad_csv)


def test_csv_to_events_empty_raises():
    header_only = "event_number,reel,edit_type,source_in,source_out,record_in,record_out\n"
    with pytest.raises(ImportError, match="No events found"):
        csv_to_events(header_only)


def test_csv_to_edl_returns_edl():
    edl = csv_to_edl(CSV_DATA)
    assert isinstance(edl, EDL)


def test_csv_to_edl_title():
    edl = csv_to_edl(CSV_DATA, title="MY_EDIT")
    assert edl.title == "MY_EDIT"


def test_csv_to_edl_fcm():
    edl = csv_to_edl(CSV_DATA, fcm="DROP FRAME")
    assert edl.fcm == "DROP FRAME"


def test_csv_to_edl_event_count():
    edl = csv_to_edl(CSV_DATA)
    assert len(edl.events) == 2


def test_tsv_to_edl_returns_edl():
    edl = tsv_to_edl(TSV_DATA)
    assert isinstance(edl, EDL)


def test_tsv_to_edl_event_count():
    edl = tsv_to_edl(TSV_DATA)
    assert len(edl.events) == 2


def test_tsv_to_edl_reel_field():
    edl = tsv_to_edl(TSV_DATA)
    assert edl.events[1].reel == "REEL02"
