"""Tests for edl_parse.comparator."""

import pytest
from edl_parse.parser import EDL, EDLEvent
from edl_parse.comparator import (
    compare_edls,
    ComparisonReport,
    FieldDiff,
    CompareError,
)


def make_event(number="001", reel="A001", edit_type="C",
               src_in="01:00:00:00", src_out="01:00:10:00",
               rec_in="00:00:00:00", rec_out="00:00:10:00"):
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


def test_compare_identical_edls_no_differences():
    e = make_event()
    base = make_edl(events=[e])
    updated = make_edl(events=[make_event()])
    report = compare_edls(base, updated)
    assert not report.has_differences


def test_compare_returns_comparison_report():
    base = make_edl()
    updated = make_edl()
    report = compare_edls(base, updated)
    assert isinstance(report, ComparisonReport)


def test_compare_detects_field_diff():
    base = make_edl(events=[make_event(reel="A001")])
    updated = make_edl(events=[make_event(reel="B002")])
    report = compare_edls(base, updated)
    assert report.has_differences
    assert len(report.field_diffs) == 1
    assert report.field_diffs[0].field_name == "reel"
    assert report.field_diffs[0].base_value == "A001"
    assert report.field_diffs[0].updated_value == "B002"


def test_compare_detects_event_only_in_base():
    base = make_edl(events=[make_event("001"), make_event("002")])
    updated = make_edl(events=[make_event("001")])
    report = compare_edls(base, updated)
    assert "002" in report.events_only_in_base
    assert report.has_differences


def test_compare_detects_event_only_in_updated():
    base = make_edl(events=[make_event("001")])
    updated = make_edl(events=[make_event("001"), make_event("003")])
    report = compare_edls(base, updated)
    assert "003" in report.events_only_in_updated


def test_compare_titles_stored_in_report():
    base = make_edl(title="BASE_EDL")
    updated = make_edl(title="UPDATED_EDL")
    report = compare_edls(base, updated)
    assert report.base_title == "BASE_EDL"
    assert report.updated_title == "UPDATED_EDL"


def test_compare_summary_is_string():
    base = make_edl()
    updated = make_edl()
    report = compare_edls(base, updated)
    assert isinstance(report.summary(), str)


def test_compare_raises_on_invalid_input():
    with pytest.raises(CompareError):
        compare_edls("not_an_edl", make_edl())


def test_compare_multiple_field_diffs():
    base = make_edl(events=[make_event(reel="A001", edit_type="C")])
    updated = make_edl(events=[make_event(reel="B002", edit_type="D")])
    report = compare_edls(base, updated)
    field_names = [d.field_name for d in report.field_diffs]
    assert "reel" in field_names
    assert "edit_type" in field_names


def test_compare_empty_edls_no_differences():
    base = make_edl()
    updated = make_edl()
    report = compare_edls(base, updated)
    assert not report.has_differences
