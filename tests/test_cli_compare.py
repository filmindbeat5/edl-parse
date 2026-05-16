"""Tests for edl_parse.cli_compare."""

import json
import os
import pytest
from unittest.mock import patch
from edl_parse.cli_compare import build_compare_parser, cmd_compare


EDL_BASE = """TITLE: BASE_EDL
FCM: NON-DROP FRAME

001  A001     C        01:00:00:00 01:00:10:00 00:00:00:00 00:00:10:00
"""

EDL_UPDATED_SAME = """TITLE: UPDATED_EDL
FCM: NON-DROP FRAME

001  A001     C        01:00:00:00 01:00:10:00 00:00:00:00 00:00:10:00
"""

EDL_UPDATED_DIFF = """TITLE: UPDATED_EDL
FCM: NON-DROP FRAME

001  B002     C        01:00:00:00 01:00:10:00 00:00:00:00 00:00:10:00
"""


@pytest.fixture
def edl_files(tmp_path):
    base_path = tmp_path / "base.edl"
    same_path = tmp_path / "same.edl"
    diff_path = tmp_path / "diff.edl"
    base_path.write_text(EDL_BASE)
    same_path.write_text(EDL_UPDATED_SAME)
    diff_path.write_text(EDL_UPDATED_DIFF)
    return str(base_path), str(same_path), str(diff_path)


def test_build_compare_parser_returns_parser():
    parser = build_compare_parser()
    assert parser is not None


def test_build_compare_parser_has_base_and_updated(edl_files):
    base, same, _ = edl_files
    parser = build_compare_parser()
    args = parser.parse_args([base, same])
    assert args.base == base
    assert args.updated == same


def test_build_compare_parser_json_flag(edl_files):
    base, same, _ = edl_files
    parser = build_compare_parser()
    args = parser.parse_args([base, same, "--json"])
    assert args.output_json is True


def test_build_compare_parser_exit_code_flag(edl_files):
    base, same, _ = edl_files
    parser = build_compare_parser()
    args = parser.parse_args([base, same, "--exit-code"])
    assert args.exit_code is True


def test_cmd_compare_no_diff_prints_summary(edl_files, capsys):
    base, same, _ = edl_files
    parser = build_compare_parser()
    args = parser.parse_args([base, same])
    cmd_compare(args)
    captured = capsys.readouterr()
    assert "BASE_EDL" in captured.out or "Field differences: 0" in captured.out


def test_cmd_compare_diff_prints_field(edl_files, capsys):
    base, _, diff = edl_files
    parser = build_compare_parser()
    args = parser.parse_args([base, diff])
    cmd_compare(args)
    captured = capsys.readouterr()
    assert "reel" in captured.out


def test_cmd_compare_json_output(edl_files, capsys):
    base, _, diff = edl_files
    parser = build_compare_parser()
    args = parser.parse_args([base, diff, "--json"])
    cmd_compare(args)
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert "field_diffs" in data
    assert len(data["field_diffs"]) > 0


def test_cmd_compare_missing_file_exits(tmp_path):
    base = str(tmp_path / "nonexistent.edl")
    updated = str(tmp_path / "also_nonexistent.edl")
    parser = build_compare_parser()
    args = parser.parse_args([base, updated])
    with pytest.raises(SystemExit) as exc:
        cmd_compare(args)
    assert exc.value.code == 2


def test_cmd_compare_exit_code_on_diff(edl_files):
    base, _, diff = edl_files
    parser = build_compare_parser()
    args = parser.parse_args([base, diff, "--exit-code"])
    with pytest.raises(SystemExit) as exc:
        cmd_compare(args)
    assert exc.value.code == 1
