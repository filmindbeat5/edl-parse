"""Tests for edl_parse.cli_stats module."""

import json
import os
import tempfile
import pytest
from unittest.mock import patch
from edl_parse.cli_stats import build_stats_parser, cmd_stats


EDL_CONTENT = """TITLE: CLI STATS TEST
FCM: NON-DROP FRAME

001  REEL_A  V  C  00:00:01:00 00:00:05:00 01:00:00:00 01:00:04:00
002  REEL_B  V  C  00:00:10:00 00:00:15:00 01:00:04:00 01:00:09:00
"""


@pytest.fixture
def edl_file(tmp_path):
    path = tmp_path / "test.edl"
    path.write_text(EDL_CONTENT)
    return str(path)


def test_build_stats_parser_returns_parser():
    parser = build_stats_parser()
    assert parser is not None


def test_build_stats_parser_has_input_arg():
    parser = build_stats_parser()
    args = parser.parse_args(["some.edl"])
    assert args.input == "some.edl"


def test_build_stats_parser_default_fps():
    parser = build_stats_parser()
    args = parser.parse_args(["some.edl"])
    assert args.fps == 25


def test_cmd_stats_prints_to_stdout(edl_file, capsys):
    parser = build_stats_parser()
    args = parser.parse_args([edl_file])
    cmd_stats(args)
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert "event_count" in data
    assert data["event_count"] == 2


def test_cmd_stats_writes_output_file(edl_file, tmp_path):
    out_path = str(tmp_path / "stats.json")
    parser = build_stats_parser()
    args = parser.parse_args([edl_file, "--output", out_path])
    cmd_stats(args)
    assert os.path.exists(out_path)
    with open(out_path) as fh:
        data = json.load(fh)
    assert data["title"] == "CLI STATS TEST"


def test_cmd_stats_missing_file_exits(tmp_path):
    parser = build_stats_parser()
    args = parser.parse_args([str(tmp_path / "missing.edl")])
    with pytest.raises(SystemExit) as exc_info:
        cmd_stats(args)
    assert exc_info.value.code == 1


def test_cmd_stats_reel_counts_present(edl_file, capsys):
    parser = build_stats_parser()
    args = parser.parse_args([edl_file])
    cmd_stats(args)
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert "reel_counts" in data
    assert data["reel_counts"]["REEL_A"] == 1
