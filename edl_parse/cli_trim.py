"""CLI entry point for trimming EDL files by record timecode range."""

import argparse
import sys

from edl_parse.converter import edl_file_to_json, edl_to_json
from edl_parse.parser import parse_edl
from edl_parse.trimmer import TrimError, trim_edl


def build_trim_parser() -> argparse.ArgumentParser:
    """Build and return the argument parser for the trim command."""
    parser = argparse.ArgumentParser(
        prog="edl-trim",
        description="Trim an EDL to a record timecode range and output JSON.",
    )
    parser.add_argument("input", help="Path to the input EDL file.")
    parser.add_argument(
        "--start",
        metavar="TIMECODE",
        default=None,
        help="Inclusive start record timecode (e.g. 01:00:00:00).",
    )
    parser.add_argument(
        "--end",
        metavar="TIMECODE",
        default=None,
        help="Exclusive end record timecode (e.g. 01:30:00:00).",
    )
    parser.add_argument(
        "--fps",
        type=int,
        default=25,
        help="Frames per second for timecode conversion (default: 25).",
    )
    parser.add_argument(
        "-o", "--output",
        metavar="FILE",
        default=None,
        help="Write JSON output to FILE instead of stdout.",
    )
    return parser


def cmd_trim(args: argparse.Namespace) -> None:
    """Execute the trim command."""
    try:
        with open(args.input, "r") as fh:
            raw = fh.read()
    except FileNotFoundError:
        print(f"Error: file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    edl = parse_edl(raw)

    try:
        trimmed = trim_edl(edl, start_tc=args.start, end_tc=args.end, fps=args.fps)
    except TrimError as exc:
        print(f"Trim error: {exc}", file=sys.stderr)
        sys.exit(1)

    json_output = edl_to_json(trimmed)

    if args.output:
        with open(args.output, "w") as fh:
            fh.write(json_output)
    else:
        print(json_output)


def main() -> None:
    parser = build_trim_parser()
    args = parser.parse_args()
    if args.start is None and args.end is None:
        parser.error("At least one of --start or --end must be provided.")
    cmd_trim(args)


if __name__ == "__main__":
    main()
