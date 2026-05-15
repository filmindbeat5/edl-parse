"""Tests for edl_parse.validator_batch."""

import pytest
from edl_parse.parser import EDL, EDLEvent
from edl_parse.validator_batch import (
    BatchValidationError,
    BatchValidationReport,
    EventValidationReport,
    validate_events_batch,
    validate_edl_batch,
)


def make_event(number="001", reel="AX", src_in="01:00:00:00", src_out="01:00:05:00",
               rec_in="01:00:00:00", rec_out="01:00:05:00", edit_type="C"):
    return EDLEvent(
        event_number=number,
        reel=reel,
        edit_type=edit_type,
        transition="",
        source_in=src_in,
        source_out=src_out,
        record_in=rec_in,
        record_out=rec_out,
    )


def make_edl(events):
    edl = EDL()
    edl.title = "TEST"
    edl.fcm = "NON-DROP FRAME"
    edl.events = events
    return edl


# --- validate_events_batch ---

def test_validate_events_batch_returns_report():
    events = [make_event()]
    report = validate_events_batch(events)
    assert isinstance(report, BatchValidationReport)


def test_validate_events_batch_all_valid():
    events = [make_event("001"), make_event("002")]
    report = validate_events_batch(events)
    assert report.is_fully_valid
    assert report.valid_count == 2
    assert report.invalid_count == 0


def test_validate_events_batch_detects_invalid():
    bad = make_event(src_in="not_a_timecode")
    report = validate_events_batch([bad])
    assert not report.is_fully_valid
    assert report.invalid_count == 1


def test_validate_events_batch_empty_reel_invalid():
    bad = make_event(reel="")
    report = validate_events_batch([bad])
    assert not report.is_fully_valid


def test_validate_events_batch_empty_list():
    report = validate_events_batch([])
    assert report.total == 0
    assert report.is_fully_valid


def test_validate_events_batch_non_list_raises():
    with pytest.raises(BatchValidationError):
        validate_events_batch("not a list")


def test_validate_events_batch_invalid_reports_list():
    bad = make_event(src_in="bad")
    good = make_event(number="002")
    report = validate_events_batch([bad, good])
    invalid = report.invalid_reports()
    assert len(invalid) == 1
    assert invalid[0].event_number == "001"


# --- validate_edl_batch ---

def test_validate_edl_batch_returns_report():
    edl = make_edl([make_event()])
    report = validate_edl_batch(edl)
    assert isinstance(report, BatchValidationReport)


def test_validate_edl_batch_valid_edl():
    edl = make_edl([make_event("001"), make_event("002")])
    report = validate_edl_batch(edl)
    assert report.is_fully_valid
    assert report.total == 2


def test_validate_edl_batch_non_edl_raises():
    with pytest.raises(BatchValidationError):
        validate_edl_batch({"not": "an edl"})


# --- summary ---

def test_summary_contains_totals():
    events = [make_event("001"), make_event(number="002", src_in="bad")]
    report = validate_events_batch(events)
    summary = report.summary()
    assert "Total events" in summary
    assert "Invalid" in summary


def test_summary_mentions_event_number_on_error():
    bad = make_event(number="007", src_in="bad_tc")
    report = validate_events_batch([bad])
    summary = report.summary()
    assert "007" in summary
