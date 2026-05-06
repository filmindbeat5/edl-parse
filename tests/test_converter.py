"""Tests for the EDL converter module."""

import json
import pytest
from edl_parse.parser import parse_edl
from edl_parse.converter import edl_to_dict, edl_to_json, event_to_dict

SAMPLE_EDL = """\
TITLE: CONVERT_TEST
FCM: DROP FRAME

001  REEL1    V     C        00:01:00:00 00:01:10:00 01:00:00:00 01:00:10:00
* FROM CLIP NAME: scene_01.mov
"""


@pytest.fixture
def parsed_edl():
    return parse_edl(SAMPLE_EDL)


def test_edl_to_dict_keys(parsed_edl):
    result = edl_to_dict(parsed_edl)
    assert set(result.keys()) == {"title", "fcm", "events"}


def test_edl_to_dict_title(parsed_edl):
    result = edl_to_dict(parsed_edl)
    assert result["title"] == "CONVERT_TEST"


def test_edl_to_dict_fcm(parsed_edl):
    result = edl_to_dict(parsed_edl)
    assert result["fcm"] == "DROP FRAME"


def test_edl_to_dict_events_list(parsed_edl):
    result = edl_to_dict(parsed_edl)
    assert isinstance(result["events"], list)
    assert len(result["events"]) == 1


def test_event_to_dict_keys(parsed_edl):
    ev_dict = event_to_dict(parsed_edl.events[0])
    expected_keys = {
        "event_number", "reel", "track", "edit_type", "transition",
        "source_in", "source_out", "record_in", "record_out",
        "clip_name", "comments",
    }
    assert set(ev_dict.keys()) == expected_keys


def test_event_to_dict_clip_name(parsed_edl):
    ev_dict = event_to_dict(parsed_edl.events[0])
    assert ev_dict["clip_name"] == "scene_01.mov"


def test_edl_to_json_is_valid_json(parsed_edl):
    json_str = edl_to_json(parsed_edl)
    parsed = json.loads(json_str)
    assert parsed["title"] == "CONVERT_TEST"


def test_edl_to_json_indent(parsed_edl):
    json_str = edl_to_json(parsed_edl, indent=4)
    # With indent=4 each nested line should start with 4 spaces
    assert "    " in json_str


def test_edl_to_json_events_structure(parsed_edl):
    data = json.loads(edl_to_json(parsed_edl))
    event = data["events"][0]
    assert event["reel"] == "REEL1"
    assert event["source_in"] == "00:01:00:00"
