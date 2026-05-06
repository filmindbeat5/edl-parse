"""Tests for edl_parse.validator module."""

import pytest
from edl_parse.parser import EDL, EDLEvent
from edl_parse.validator import (
    validate_edl,
    validate_event,
    validate_timecode,
    ValidationResult,
    ValidationError,
)


VALID_EVENT = EDLEvent(
    event_number=1,
    reel="AX",
    track="V",
    edit_type="C",
    source_in="01:00:00:00",
    source_out="01:00:05:00",
    record_in="01:00:00:00",
    record_out="01:00:05:00",
)

VALID_EDL = EDL(title="TEST EDL", fcm="NON-DROP FRAME", events=[VALID_EVENT])


# --- validate_timecode ---

@pytest.mark.parametrize("tc", [
    "01:00:00:00",
    "00:00:00:00",
    "23:59:59:29",
    "01:00:00;00",  # drop-frame semicolon
])
def test_valid_timecodes(tc):
    assert validate_timecode(tc) is True


@pytest.mark.parametrize("tc", [
    "1:00:00:00",
    "01:00:00",
    "ab:cd:ef:gh",
    "",
    "01:00:00:000",
])
def test_invalid_timecodes(tc):
    assert validate_timecode(tc) is False


# --- validate_event ---

def test_validate_event_valid():
    errors = validate_event(VALID_EVENT, 1)
    assert errors == []


def test_validate_event_bad_timecode():
    bad_event = EDLEvent(
        event_number=2,
        reel="AX",
        track="V",
        edit_type="C",
        source_in="bad_tc",
        source_out="01:00:05:00",
        record_in="01:00:00:00",
        record_out="01:00:05:00",
    )
    errors = validate_event(bad_event, 2)
    assert any(e.field == "source_in" for e in errors)


def test_validate_event_empty_reel():
    bad_event = EDLEvent(
        event_number=3, reel="", track="V", edit_type="C",
        source_in="01:00:00:00", source_out="01:00:05:00",
        record_in="01:00:00:00", record_out="01:00:05:00",
    )
    errors = validate_event(bad_event, 3)
    assert any(e.field == "reel" for e in errors)


# --- validate_edl ---

def test_validate_edl_valid():
    result = validate_edl(VALID_EDL)
    assert isinstance(result, ValidationResult)
    assert result.valid is True
    assert result.errors == []


def test_validate_edl_missing_title():
    edl = EDL(title="", fcm="NON-DROP FRAME", events=[VALID_EVENT])
    result = validate_edl(edl)
    assert result.valid is False
    assert any(e.field == "title" for e in result.errors)


def test_validate_edl_no_events():
    edl = EDL(title="TEST", fcm="NON-DROP FRAME", events=[])
    result = validate_edl(edl)
    assert result.valid is False
    assert any(e.field == "events" for e in result.errors)


def test_validation_result_str_valid():
    result = ValidationResult(valid=True, errors=[])
    assert "valid" in str(result).lower()


def test_validation_result_str_invalid():
    err = ValidationError(field="title", message="missing")
    result = ValidationResult(valid=False, errors=[err])
    assert "1 error" in str(result)
