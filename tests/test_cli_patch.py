"""Tests for edl_parse.cli_patch module."""

import json
import os
import pytest
from unittest.mock import patch as mock_patch
from argparse import Namespace

from edl_parse.cli_patch import build_patch_parser, cmd_patch, _parse_fields


EDL_CONTENT = """TITLE: TEST
FCM: NON-DROP FRAME

001  CAM_A  C  01:00:00:00 01:00:05:00 01:00:00:00 01:00:05:00
002  CAM_B  C  01:00:05:00 01:00:10:00 01:00:05:00 01:00:10:00
"""


@pytest.fixture
def edl_file(tmp_path):
    p = tmp_path / "test.edl"
    p.write_text(EDL_CONTENT)
    return str(p)


def test_build_patch_parser_returns_parser():
    parser = build_patch_parser()
    assert parser is not None


def test_build_patch_parser_has_input_arg():
    parser = build_patch_parser()
    args = parser.parse_args(["file.edl", "--event-number", "001", "--set", "reel=X"])
    assert args.input == "file.edl"


def test_build_patch_parser_event_number_and_reel_mutually_exclusive():
    parser = build_patch_parser()
    with pytest.raises(SystemExit):
        parser.parse_args(
            ["file.edl", "--event-number", "001", "--reel", "CAM_A", "--set", "reel=X"]
        )


def test_parse_fields_valid():
    result = _parse_fields(["reel=NEW_REEL", "edit_type=D"])
    assert result == {"reel": "NEW_REEL", "edit_type": "D"}


def test_parse_fields_invalid_raises():
    with pytest.raises(ValueError, match="Invalid field spec"):
        _parse_fields(["no_equals_sign"])


def test_cmd_patch_by_event_number_stdout(edl_file, capsys):
    args = Namespace(
        input=edl_file,
        event_number="001",
        reel=None,
        fields=["reel=PATCHED"],
        output=None,
    )
    cmd_patch(args)
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    events = data["events"]
    assert any(e["reel"] == "PATCHED" and e["event_number"] == "001" for e in events)


def test_cmd_patch_by_reel_stdout(edl_file, capsys):
    args = Namespace(
        input=edl_file,
        event_number=None,
        reel="CAM_B",
        fields=["edit_type=D"],
        output=None,
    )
    cmd_patch(args)
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    events = data["events"]
    assert any(e["reel"] == "CAM_B" and e["edit_type"] == "D" for e in events)


def test_cmd_patch_writes_output_file(edl_file, tmp_path):
    out_file = str(tmp_path / "out.json")
    args = Namespace(
        input=edl_file,
        event_number="002",
        reel=None,
        fields=["reel=NEWREEL"],
        output=out_file,
    )
    cmd_patch(args)
    assert os.path.exists(out_file)
    with open(out_file) as f:
        data = json.load(f)
    assert any(e["reel"] == "NEWREEL" for e in data["events"])


def test_cmd_patch_missing_file_exits(tmp_path):
    args = Namespace(
        input=str(tmp_path / "missing.edl"),
        event_number="001",
        reel=None,
        fields=["reel=X"],
        output=None,
    )
    with pytest.raises(SystemExit) as exc_info:
        cmd_patch(args)
    assert exc_info.value.code == 1
