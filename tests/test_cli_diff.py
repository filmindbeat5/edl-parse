"""Tests for edl_parse.cli_diff."""

import json
import pytest
from unittest.mock import patch
from edl_parse.cli_diff import build_diff_parser, cmd_diff


BASE_EDL = """TITLE: BASE
FCM: NON-DROP FRAME

001  A001 V  C  01:00:00:00 01:00:05:00 01:00:00:00 01:00:05:00
002  A002 V  C  01:00:05:00 01:00:10:00 01:00:05:00 01:00:10:00
"""

UPDATED_EDL = """TITLE: UPDATED
FCM: NON-DROP FRAME

001  A001 V  C  01:00:00:00 01:00:05:00 01:00:00:00 01:00:05:00
002  A999 V  C  01:00:05:00 01:00:10:00 01:00:05:00 01:00:10:00
003  A003 V  C  01:00:10:00 01:00:15:00 01:00:10:00 01:00:15:00
"""


@pytest.fixture
def edl_files(tmp_path):
    base = tmp_path / "base.edl"
    updated = tmp_path / "updated.edl"
    base.write_text(BASE_EDL)
    updated.write_text(UPDATED_EDL)
    return str(base), str(updated)


def test_build_diff_parser_returns_parser():
    parser = build_diff_parser()
    assert parser is not None


def test_build_diff_parser_has_base_and_updated_args():
    parser = build_diff_parser()
    args = parser.parse_args(["base.edl", "updated.edl"])
    assert args.base == "base.edl"
    assert args.updated == "updated.edl"


def test_build_diff_parser_json_flag():
    parser = build_diff_parser()
    args = parser.parse_args(["base.edl", "updated.edl", "--json"])
    assert args.json is True


def test_build_diff_parser_exit_code_flag():
    parser = build_diff_parser()
    args = parser.parse_args(["base.edl", "updated.edl", "--exit-code"])
    assert args.exit_code is True


def test_cmd_diff_prints_summary(edl_files, capsys):
    base, updated = edl_files
    parser = build_diff_parser()
    args = parser.parse_args([base, updated])
    cmd_diff(args)
    out = capsys.readouterr().out
    assert "Changed:" in out or "Added:" in out


def test_cmd_diff_json_output(edl_files, capsys):
    base, updated = edl_files
    parser = build_diff_parser()
    args = parser.parse_args([base, updated, "--json"])
    cmd_diff(args)
    out = capsys.readouterr().out
    data = json.loads(out)
    assert "added" in data
    assert "removed" in data
    assert "changed" in data


def test_cmd_diff_missing_file_exits(tmp_path, capsys):
    parser = build_diff_parser()
    args = parser.parse_args(["nonexistent.edl", "also_missing.edl"])
    with pytest.raises(SystemExit) as exc_info:
        cmd_diff(args)
    assert exc_info.value.code == 1


def test_cmd_diff_exit_code_on_differences(edl_files):
    base, updated = edl_files
    parser = build_diff_parser()
    args = parser.parse_args([base, updated, "--exit-code"])
    with pytest.raises(SystemExit) as exc_info:
        cmd_diff(args)
    assert exc_info.value.code == 1


def test_cmd_diff_no_exit_code_when_identical(tmp_path, capsys):
    edl_path = tmp_path / "same.edl"
    edl_path.write_text(BASE_EDL)
    parser = build_diff_parser()
    args = parser.parse_args([str(edl_path), str(edl_path), "--exit-code"])
    # Should not raise SystemExit since files are identical
    cmd_diff(args)
    out = capsys.readouterr().out
    assert "No differences found." in out
