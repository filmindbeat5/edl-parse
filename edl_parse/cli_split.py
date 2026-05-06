"""CLI entry point for the EDL splitter."""

import argparse
import json
import sys
from edl_parse.parser import parse_edl
from edl_parse.converter import edl_to_dict
from edl_parse.splitter import (
    SplitError,
    split_by_reel,
    split_by_edit_type,
    split_into_chunks,
)


def build_split_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="edl-split",
        description="Split an EDL file by reel, edit type, or chunk size.",
    )
    parser.add_argument("input", help="Path to the input EDL file.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--by-reel",
        action="store_true",
        help="Split the EDL into one EDL per reel.",
    )
    group.add_argument(
        "--by-edit-type",
        action="store_true",
        help="Split the EDL into one EDL per edit type.",
    )
    group.add_argument(
        "--chunk",
        type=int,
        metavar="N",
        help="Split the EDL into chunks of N events each.",
    )
    parser.add_argument(
        "--indent",
        type=int,
        default=2,
        help="JSON indentation level (default: 2).",
    )
    return parser


def cmd_split(args: argparse.Namespace) -> None:
    try:
        with open(args.input, "r") as fh:
            raw = fh.read()
    except FileNotFoundError:
        print(f"Error: file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    edl = parse_edl(raw)

    try:
        if args.by_reel:
            splits = split_by_reel(edl)
            output = {key: edl_to_dict(child) for key, child in splits.items()}
        elif args.by_edit_type:
            splits = split_by_edit_type(edl)
            output = {key: edl_to_dict(child) for key, child in splits.items()}
        else:
            chunks = split_into_chunks(edl, args.chunk)
            output = [
                edl_to_dict(chunk) for chunk in chunks
            ]
    except SplitError as exc:
        print(f"Split error: {exc}", file=sys.stderr)
        sys.exit(1)

    print(json.dumps(output, indent=args.indent))


def main() -> None:
    parser = build_split_parser()
    args = parser.parse_args()
    cmd_split(args)


if __name__ == "__main__":
    main()
