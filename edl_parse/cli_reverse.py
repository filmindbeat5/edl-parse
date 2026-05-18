"""CLI interface for reversing event order in an EDL."""

import argparse
import sys
import json

from edl_parse.parser import parse_edl
from edl_parse.reverser import ReverseError, reverse_edl
from edl_parse.converter import edl_to_json


def build_reverse_parser():
    parser = argparse.ArgumentParser(
        prog="edl-reverse",
        description="Reverse the event order of an EDL file.",
    )
    parser.add_argument("input", help="Path to the input EDL file")
    parser.add_argument(
        "-o", "--output",
        help="Write JSON output to this file instead of stdout",
        default=None,
    )
    parser.add_argument(
        "--indent",
        type=int,
        default=2,
        help="JSON indentation level (default: 2)",
    )
    return parser


def cmd_reverse(args):
    try:
        with open(args.input, "r") as f:
            raw = f.read()
    except FileNotFoundError:
        print(f"Error: file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    edl = parse_edl(raw)

    try:
        reversed_edl = reverse_edl(edl)
    except ReverseError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)

    output = edl_to_json(reversed_edl, indent=args.indent)

    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
    else:
        print(output)


def main():
    parser = build_reverse_parser()
    args = parser.parse_args()
    cmd_reverse(args)


if __name__ == "__main__":
    main()
