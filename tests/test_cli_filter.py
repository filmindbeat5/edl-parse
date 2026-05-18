"""Tests for edl_parse.cli_filter module."""

import json
import os
import pytest
from unittest.mock import patch, mock_open
from edl_parse.cli_filter import build_filter_parser, cmd_filter


EDL_CONTENT = """TITLE: FILTER_TEST
FCM: NON-DROP FRAME

001  REEL_A  V  C  01:00:00:00 01:00:05:00 01:00:00:00 01:00:05:00
002  REEL_B  V  D  01:00:05:00 01:00:10:00 01:00:05:00 01:00:10:00
003  REEL_A  V  C  01:00:10:00 01:00:15:00 01:00:10:00 01:00:15:00
"""


@pytest.fixture
def edl_file(tmp_path):
    p = tmp_path / "test.edl"
    p.write_text(EDL_CONTENT)
    return str(p)


def test_build_filter_parser_returns_parser():
    parser = build_filter_parser()
    assert parser is not None


def test_build_filter_parser_has_input_arg():
    parser = build_filter_parser()
    args = parser.parse_args(["some.edl"])
    assert args.input == "some.edl"


def test_build_filter_parser_optional_flags():
    parser = build_filter_parser()
    args = parser.parse_args(["some.edl", "--reel", "REEL_A", "--edit-type", "C"])
    assert args.reel == "REEL_A"
    assert args.edit_type == "C"


def test_cmd_filter_by_reel_stdout(edl_file, capsys):
    parser = build_filter_parser()
    args = parser.parse_args([edl_file, "--reel", "REEL_A"])
    cmd_filter(args)
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert len(data["events"]) == 2
    assert all(e["reel"] == "REEL_A" for e in data["events"])


def test_cmd_filter_by_edit_type(edl_file, capsys):
    parser = build_filter_parser()
    args = parser.parse_args([edl_file, "--edit-type", "D"])
    cmd_filter(args)
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert len(data["events"]) == 1


def test_cmd_filter_event_range(edl_file, capsys):
    parser = build_filter_parser()
    args = parser.parse_args([edl_file, "--event-start", "2", "--event-end", "3"])
    cmd_filter(args)
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert len(data["events"]) == 2


def test_cmd_filter_writes_output_file(edl_file, tmp_path):
    out_file = str(tmp_path / "out.json")
    parser = build_filter_parser()
    args = parser.parse_args([edl_file, "--reel", "REEL_B", "-o", out_file])
    cmd_filter(args)
    assert os.path.exists(out_file)
    with open(out_file) as fh:
        data = json.load(fh)
    assert len(data["events"]) == 1


def test_cmd_filter_missing_file(tmp_path):
    parser = build_filter_parser()
    args = parser.parse_args([str(tmp_path / "nonexistent.edl")])
    with pytest.raises(SystemExit) as exc_info:
        cmd_filter(args)
    assert exc_info.value.code == 1


def test_cmd_filter_no_matching_events(edl_file, capsys):
    """Filtering by a reel that does not exist should return an empty events list."""
    parser = build_filter_parser()
    args = parser.parse_args([edl_file, "--reel", "REEL_NONEXISTENT"])
    cmd_filter(args)
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["events"] == []
