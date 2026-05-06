"""CLI subcommand for filtering EDL events."""

import argparse
import sys
from edl_parse.parser import parse_edl
from edl_parse.filter import filter_edl_events
from edl_parse.converter import edl_to_json


def build_filter_parser(subparsers=None):
    """Build argument parser for the filter subcommand."""
    description = "Filter EDL events by reel, edit type, or event number range."
    if subparsers is not None:
        parser = subparsers.add_parser("filter", help=description)
    else:
        parser = argparse.ArgumentParser(description=description)

    parser.add_argument("input", help="Path to the input EDL file")
    parser.add_argument("-o", "--output", help="Output JSON file path (default: stdout)")
    parser.add_argument("--reel", help="Filter by reel name")
    parser.add_argument("--edit-type", dest="edit_type", help="Filter by edit type (e.g. C, D)")
    parser.add_argument(
        "--event-start",
        dest="event_start",
        type=int,
        help="Minimum event number (inclusive)",
    )
    parser.add_argument(
        "--event-end",
        dest="event_end",
        type=int,
        help="Maximum event number (inclusive)",
    )
    return parser


def cmd_filter(args):
    """Execute the filter subcommand."""
    try:
        with open(args.input, "r") as fh:
            content = fh.read()
    except FileNotFoundError:
        print(f"Error: file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    edl = parse_edl(content)
    filtered_edl = filter_edl_events(
        edl,
        reel=getattr(args, "reel", None),
        edit_type=getattr(args, "edit_type", None),
        event_start=getattr(args, "event_start", None),
        event_end=getattr(args, "event_end", None),
    )

    json_output = edl_to_json(filtered_edl)

    if args.output:
        with open(args.output, "w") as fh:
            fh.write(json_output)
        print(f"Filtered EDL written to {args.output}")
    else:
        print(json_output)


def main():
    parser = build_filter_parser()
    args = parser.parse_args()
    cmd_filter(args)


if __name__ == "__main__":
    main()
