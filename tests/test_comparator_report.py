"""Additional tests for ComparisonReport and FieldDiff details."""

import pytest
from edl_parse.parser import EDL, EDLEvent
from edl_parse.comparator import compare_edls, ComparisonReport, FieldDiff


def make_event(number="001", reel="A001", edit_type="C",
               src_in="01:00:00:00", src_out="01:00:05:00",
               rec_in="00:00:00:00", rec_out="00:00:05:00"):
    e = EDLEvent()
    e.event_number = number
    e.reel = reel
    e.edit_type = edit_type
    e.source_in = src_in
    e.source_out = src_out
    e.record_in = rec_in
    e.record_out = rec_out
    return e


def make_edl(title="TEST", events=None):
    edl = EDL()
    edl.title = title
    edl.events = events or []
    return edl


def test_field_diff_attributes():
    fd = FieldDiff(event_number="001", field_name="reel", base_value="A", updated_value="B")
    assert fd.event_number == "001"
    assert fd.field_name == "reel"
    assert fd.base_value == "A"
    assert fd.updated_value == "B"


def test_report_has_differences_false_when_empty():
    report = ComparisonReport(base_title="A", updated_title="B")
    assert not report.has_differences


def test_report_has_differences_true_with_field_diff():
    report = ComparisonReport(base_title="A", updated_title="B")
    report.field_diffs.append(
        FieldDiff(event_number="001", field_name="reel", base_value="A", updated_value="B")
    )
    assert report.has_differences


def test_report_has_differences_true_with_base_only():
    report = ComparisonReport(base_title="A", updated_title="B")
    report.events_only_in_base.append("002")
    assert report.has_differences


def test_report_has_differences_true_with_updated_only():
    report = ComparisonReport(base_title="A", updated_title="B")
    report.events_only_in_updated.append("003")
    assert report.has_differences


def test_summary_contains_counts():
    base = make_edl(events=[make_event("001"), make_event("002")])
    updated = make_edl(events=[make_event("001"), make_event("003")])
    report = compare_edls(base, updated)
    summary = report.summary()
    assert "Events only in base: 1" in summary
    assert "Events only in updated: 1" in summary


def test_compare_timecode_diff_detected():
    base = make_edl(events=[make_event(src_in="01:00:00:00")])
    updated = make_edl(events=[make_event(src_in="01:00:05:00")])
    report = compare_edls(base, updated)
    fields = [d.field_name for d in report.field_diffs]
    assert "source_in" in fields


def test_compare_no_shared_events():
    base = make_edl(events=[make_event("001")])
    updated = make_edl(events=[make_event("002")])
    report = compare_edls(base, updated)
    assert "001" in report.events_only_in_base
    assert "002" in report.events_only_in_updated
    assert report.field_diffs == []


def test_compare_multiple_events_partial_diff():
    base = make_edl(events=[
        make_event("001", reel="A"),
        make_event("002", reel="B"),
    ])
    updated = make_edl(events=[
        make_event("001", reel="A"),
        make_event("002", reel="X"),
    ])
    report = compare_edls(base, updated)
    assert len(report.field_diffs) == 1
    assert report.field_diffs[0].event_number == "002"
