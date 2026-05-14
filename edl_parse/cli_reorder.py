"""CLI entry point for EDL event reordering."""

import argparse
import sys
import json

from edl_parse.parser import parse_edl
from edl_parse.reorderer import reorder_edl_events, ReorderError
from edl_parse.converter import edl_to_dict


def build_reorder_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="edl-reorder",
        description="Reorder events in an EDL file by field or custom reel sequence.",
    )
    parser.add_argument("input", help="Path to the input EDL file.")
    parser.add_argument("-o", "--output", help="Write JSON output to this file instead of stdout.")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--field",
        choices=["event_number", "reel", "edit_type", "source_in", "source_out", "record_in", "record_out"],
        help="Sort events by this field.",
    )
    group.add_argument(
        "--sequence",
        nargs="+",
        metavar="REEL",
        help="Reorder events by custom reel sequence (space-separated reel names).",
    )
    parser.add_argument(
        "--reverse",
        action="store_true",
        default=False,
        help="Reverse the sort order (only applies with --field).",
    )
    return parser


def cmd_reorder(args: argparse.Namespace) -> None:
    try:
        with open(args.input, "r") as fh:
            edl = parse_edl(fh.read())
    except FileNotFoundError:
        print(f"Error: File not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    try:
        reordered = reorder_edl_events(
            edl,
            field=getattr(args, "field", None),
            sequence=getattr(args, "sequence", None),
            reverse=getattr(args, "reverse", False),
        )
    except ReorderError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    output = json.dumps(edl_to_dict(reordered), indent=2)

    if args.output:
        with open(args.output, "w") as fh:
            fh.write(output)
    else:
        print(output)


def main():
    parser = build_reorder_parser()
    args = parser.parse_args()
    cmd_reorder(args)


if __name__ == "__main__":
    main()
