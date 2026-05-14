"""CLI entry point for EDL statistics reporting."""

import argparse
import json
import sys

from edl_parse.parser import parse_edl
from edl_parse.statistics import edl_statistics, StatisticsError


def build_stats_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="edl-stats",
        description="Print statistics for an EDL file.",
    )
    parser.add_argument("input", help="Path to the EDL file.")
    parser.add_argument(
        "--fps",
        type=int,
        default=25,
        help="Frames per second used for duration calculations (default: 25).",
    )
    parser.add_argument(
        "--output",
        "-o",
        default=None,
        help="Optional path to write JSON output. Defaults to stdout.",
    )
    return parser


def cmd_stats(args: argparse.Namespace) -> None:
    try:
        with open(args.input, "r") as fh:
            raw = fh.read()
    except FileNotFoundError:
        print(f"Error: file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    edl = parse_edl(raw)

    try:
        stats = edl_statistics(edl, fps=args.fps)
    except StatisticsError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    output = json.dumps(stats, indent=2)

    if args.output:
        with open(args.output, "w") as fh:
            fh.write(output)
    else:
        print(output)


def main() -> None:
    parser = build_stats_parser()
    args = parser.parse_args()
    cmd_stats(args)


if __name__ == "__main__":
    main()
