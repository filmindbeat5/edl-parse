"""Tests for edl_parse.cli module."""

import json
import pytest
from pathlib import Path
from unittest.mock import patch
from edl_parse.cli import build_parser, cmd_convert, cmd_validate, main


SAMPLE_EDL = """TITLE: CLI TEST
FCM: NON-DROP FRAME

001  AX       V     C        01:00:00:00 01:00:05:00 01:00:00:00 01:00:05:00
"""


@pytest.fixture
def edl_file(tmp_path):
    f = tmp_path / "test.edl"
    f.write_text(SAMPLE_EDL, encoding="utf-8")
    return f


def test_build_parser_returns_parser():
    parser = build_parser()
    assert parser is not None


def test_convert_prints_to_stdout(edl_file, capsys):
    parser = build_parser()
    args = parser.parse_args(["convert", str(edl_file)])
    result = cmd_convert(args)
    assert result == 0
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["title"] == "CLI TEST"


def test_convert_writes_output_file(edl_file, tmp_path):
    out_file = tmp_path / "output.json"
    parser = build_parser()
    args = parser.parse_args(["convert", str(edl_file), "-o", str(out_file)])
    result = cmd_convert(args)
    assert result == 0
    assert out_file.exists()
    data = json.loads(out_file.read_text())
    assert "events" in data


def test_convert_missing_file(tmp_path):
    parser = build_parser()
    args = parser.parse_args(["convert", str(tmp_path / "missing.edl")])
    result = cmd_convert(args)
    assert result == 1


def test_validate_valid_edl(edl_file, capsys):
    parser = build_parser()
    args = parser.parse_args(["validate", str(edl_file)])
    result = cmd_validate(args)
    assert result == 0
    captured = capsys.readouterr()
    assert "valid" in captured.out.lower()


def test_validate_missing_file(tmp_path):
    parser = build_parser()
    args = parser.parse_args(["validate", str(tmp_path / "missing.edl")])
    result = cmd_validate(args)
    assert result == 1


def test_validate_invalid_edl(tmp_path, capsys):
    bad_edl = tmp_path / "bad.edl"
    bad_edl.write_text("TITLE: \nFCM: NON-DROP FRAME\n", encoding="utf-8")
    parser = build_parser()
    args = parser.parse_args(["validate", str(bad_edl)])
    result = cmd_validate(args)
    assert result == 1
