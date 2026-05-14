"""Tests for edl_parse.cli_reorder."""

import json
import os
import tempfile
import pytest

from unittest.mock import patch
from edl_parse.cli_reorder import build_reorder_parser, cmd_reorder


EDL_CONTENT = """TITLE: REORDER TEST
FCM: NON-DROP FRAME

003  REEL_C  C  00:00:20:00 00:00:21:00 01:00:20:00 01:00:21:00
001  REEL_A  C  00:00:00:00 00:00:01:00 01:00:00:00 01:00:01:00
002  REEL_B  C  00:00:10:00 00:00:11:00 01:00:10:00 01:00:11:00
"""


@pytest.fixture
def edl_file():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".edl", delete=False) as f:
        f.write(EDL_CONTENT)
        name = f.name
    yield name
    os.unlink(name)


def test_build_reorder_parser_returns_parser():
    parser = build_reorder_parser()
    assert parser is not None


def test_build_reorder_parser_has_input_arg():
    parser = build_reorder_parser()
    args = parser.parse_args(["dummy.edl", "--field", "reel"])
    assert args.input == "dummy.edl"


def test_build_reorder_parser_field_and_sequence_mutually_exclusive():
    parser = build_reorder_parser()
    with pytest.raises(SystemExit):
        parser.parse_args(["dummy.edl", "--field", "reel", "--sequence", "REEL_A"])


def test_cmd_reorder_by_field_stdout(edl_file, capsys):
    parser = build_reorder_parser()
    args = parser.parse_args([edl_file, "--field", "event_number"])
    cmd_reorder(args)
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    numbers = [e["event_number"] for e in data["events"]]
    assert numbers == sorted(numbers)


def test_cmd_reorder_by_sequence_stdout(edl_file, capsys):
    parser = build_reorder_parser()
    args = parser.parse_args([edl_file, "--sequence", "REEL_B", "REEL_C", "REEL_A"])
    cmd_reorder(args)
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    reels = [e["reel"] for e in data["events"]]
    assert reels == ["REEL_B", "REEL_C", "REEL_A"]


def test_cmd_reorder_writes_output_file(edl_file):
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        out_path = f.name
    try:
        parser = build_reorder_parser()
        args = parser.parse_args([edl_file, "--field", "reel", "--output", out_path])
        cmd_reorder(args)
        with open(out_path) as f:
            data = json.load(f)
        assert "events" in data
    finally:
        os.unlink(out_path)


def test_cmd_reorder_missing_file_exits(capsys):
    parser = build_reorder_parser()
    args = parser.parse_args(["nonexistent.edl", "--field", "reel"])
    with pytest.raises(SystemExit) as exc_info:
        cmd_reorder(args)
    assert exc_info.value.code == 1
