"""Tests for edl_parse.cli_rename module."""

import json
import os
import tempfile
import pytest

from unittest.mock import patch
from argparse import Namespace
from edl_parse.cli_rename import build_rename_parser, cmd_rename, _parse_map


SAMPLE_EDL = """TITLE: TEST EDL
FCM: NON-DROP FRAME

001  CAM_A  V  C  01:00:00:00 01:00:05:00 00:00:00:00 00:00:05:00
002  CAM_B  V  C  01:00:10:00 01:00:15:00 00:00:05:00 00:00:10:00
"""


@pytest.fixture
def edl_file(tmp_path):
    p = tmp_path / "test.edl"
    p.write_text(SAMPLE_EDL)
    return str(p)


def test_build_rename_parser_returns_parser():
    parser = build_rename_parser()
    assert parser is not None


def test_build_rename_parser_has_input_arg():
    parser = build_rename_parser()
    args = parser.parse_args(["file.edl", "--map", "CAM_A=REEL_001"])
    assert args.input == "file.edl"


def test_parse_map_valid():
    result = _parse_map(["CAM_A=REEL_001", "CAM_B=REEL_002"])
    assert result == {"CAM_A": "REEL_001", "CAM_B": "REEL_002"}


def test_parse_map_invalid_raises():
    with pytest.raises(ValueError):
        _parse_map(["INVALID"])


def test_cmd_rename_map_stdout(edl_file, capsys):
    args = Namespace(input=edl_file, output=None, map=["CAM_A=REEL_001", "CAM_B=REEL_002"], prefix=None)
    cmd_rename(args)
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    reels = [e["reel"] for e in data["events"]]
    assert "REEL_001" in reels
    assert "REEL_002" in reels


def test_cmd_rename_prefix_stdout(edl_file, capsys):
    args = Namespace(input=edl_file, output=None, map=None, prefix="PRJ_")
    cmd_rename(args)
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    reels = [e["reel"] for e in data["events"]]
    assert all(r.startswith("PRJ_") for r in reels)


def test_cmd_rename_writes_output_file(edl_file, tmp_path):
    out_file = str(tmp_path / "output.json")
    args = Namespace(input=edl_file, output=out_file, map=["CAM_A=REEL_001"], prefix=None)
    cmd_rename(args)
    assert os.path.exists(out_file)
    with open(out_file) as fh:
        data = json.load(fh)
    assert "events" in data


def test_cmd_rename_missing_file_exits(tmp_path):
    args = Namespace(input="nonexistent.edl", output=None, map=["X=Y"], prefix=None)
    with pytest.raises(SystemExit):
        cmd_rename(args)
