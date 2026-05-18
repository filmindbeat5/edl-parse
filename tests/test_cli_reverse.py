"""Tests for edl_parse/cli_reverse.py"""

import json
import os
import tempfile
import pytest
from unittest.mock import patch

from edl_parse.cli_reverse import build_reverse_parser, cmd_reverse


EDL_CONTENT = """TITLE: REVERSE TEST
FCM: NON-DROP FRAME

001  CAM1  V  C  01:00:00:00 01:00:05:00 01:00:00:00 01:00:05:00
002  CAM2  V  C  01:00:05:00 01:00:10:00 01:00:05:00 01:00:10:00
003  CAM3  V  C  01:00:10:00 01:00:15:00 01:00:10:00 01:00:15:00
"""


@pytest.fixture
def edl_file(tmp_path):
    p = tmp_path / "test.edl"
    p.write_text(EDL_CONTENT)
    return str(p)


def test_build_reverse_parser_returns_parser():
    parser = build_reverse_parser()
    assert parser is not None


def test_build_reverse_parser_has_input_arg():
    parser = build_reverse_parser()
    args = parser.parse_args(["input.edl"])
    assert args.input == "input.edl"


def test_build_reverse_parser_has_output_flag():
    parser = build_reverse_parser()
    args = parser.parse_args(["input.edl", "-o", "out.json"])
    assert args.output == "out.json"


def test_build_reverse_parser_default_output_none():
    parser = build_reverse_parser()
    args = parser.parse_args(["input.edl"])
    assert args.output is None


def test_cmd_reverse_prints_to_stdout(edl_file, capsys):
    parser = build_reverse_parser()
    args = parser.parse_args([edl_file])
    cmd_reverse(args)
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert "events" in data


def test_cmd_reverse_events_order(edl_file, capsys):
    parser = build_reverse_parser()
    args = parser.parse_args([edl_file])
    cmd_reverse(args)
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    reels = [e["reel"] for e in data["events"]]
    assert reels[0] == "CAM3"
    assert reels[-1] == "CAM1"


def test_cmd_reverse_writes_output_file(edl_file, tmp_path):
    out_file = str(tmp_path / "out.json")
    parser = build_reverse_parser()
    args = parser.parse_args([edl_file, "-o", out_file])
    cmd_reverse(args)
    assert os.path.exists(out_file)
    with open(out_file) as f:
        data = json.load(f)
    assert "events" in data


def test_cmd_reverse_missing_file_exits(tmp_path):
    parser = build_reverse_parser()
    args = parser.parse_args([str(tmp_path / "missing.edl")])
    with pytest.raises(SystemExit) as exc_info:
        cmd_reverse(args)
    assert exc_info.value.code == 1
