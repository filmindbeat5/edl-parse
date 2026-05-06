"""Tests for the EDL parser module."""

import pytest
from edl_parse.parser import parse_edl, EDL, EDLEvent

SAMPLE_EDL = """\
TITLE: MY_PROJECT
FCM: NON-DROP FRAME

001  AX       V     C        00:00:00:00 00:00:05:12 01:00:00:00 01:00:05:12
* FROM CLIP NAME: interview_raw.mov

002  BX       V     C        00:00:10:00 00:00:15:00 01:00:05:12 01:00:10:12
* FROM CLIP NAME: b_roll_001.mov
* COMMENT: Color grade needed
"""


def test_parse_returns_edl_instance():
    edl = parse_edl(SAMPLE_EDL)
    assert isinstance(edl, EDL)


def test_parse_title():
    edl = parse_edl(SAMPLE_EDL)
    assert edl.title == "MY_PROJECT"


def test_parse_fcm():
    edl = parse_edl(SAMPLE_EDL)
    assert edl.fcm == "NON-DROP FRAME"


def test_parse_event_count():
    edl = parse_edl(SAMPLE_EDL)
    assert len(edl.events) == 2


def test_parse_first_event_fields():
    edl = parse_edl(SAMPLE_EDL)
    ev: EDLEvent = edl.events[0]
    assert ev.event_number == "001"
    assert ev.reel == "AX"
    assert ev.track == "V"
    assert ev.edit_type == "C"
    assert ev.source_in == "00:00:00:00"
    assert ev.source_out == "00:00:05:12"
    assert ev.record_in == "01:00:00:00"
    assert ev.record_out == "01:00:05:12"


def test_parse_clip_name():
    edl = parse_edl(SAMPLE_EDL)
    assert edl.events[0].clip_name == "interview_raw.mov"
    assert edl.events[1].clip_name == "b_roll_001.mov"


def test_parse_comments():
    edl = parse_edl(SAMPLE_EDL)
    assert len(edl.events[1].comments) == 1
    assert "Color grade needed" in edl.events[1].comments[0]


def test_parse_empty_string():
    edl = parse_edl("")
    assert edl.title is None
    assert edl.fcm is None
    assert edl.events == []


def test_parse_no_title():
    edl = parse_edl("001  AX  V  C  00:00:00:00 00:00:01:00 01:00:00:00 01:00:01:00")
    assert edl.title is None
    assert len(edl.events) == 1
