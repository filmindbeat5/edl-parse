"""CLI entry point for reel renaming operations."""

import argparse
import json
import sys

from edl_parse.parser import parse_edl
from edl_parse.converter import edl_to_json
from edl_parse.renamer import RenameError, rename_reels_in_edl, build_reel_map_from_prefix


def build_rename_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="edl-rename",
        description="Rename reels in an EDL file.",
    )
    parser.add_argument("input", help="Path to the input EDL file")
    parser.add_argument("-o", "--output", help="Write JSON output to file instead of stdout")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--map",
        nargs="+",
        metavar="OLD=NEW",
        help="One or more reel rename mappings in OLD=NEW format",
    )
    group.add_argument(
        "--prefix",
        metavar="PREFIX",
        help="Add a prefix to all reel names",
    )
    return parser


def _parse_map(pairs: list) -> dict:
    """Parse a list of 'OLD=NEW' strings into a dict."""
    reel_map = {}
    for pair in pairs:
        if "=" not in pair:
            raise ValueError(f"Invalid mapping '{pair}': expected OLD=NEW format")
        old, new = pair.split("=", 1)
        reel_map[old.strip()] = new.strip()
    return reel_map


def cmd_rename(args: argparse.Namespace) -> None:
    try:
        with open(args.input, "r") as fh:
            edl = parse_edl(fh.read())
    except FileNotFoundError:
        print(f"Error: file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    try:
        if args.map:
            reel_map = _parse_map(args.map)
        else:
            reel_map = build_reel_map_from_prefix(edl.events, args.prefix)

        renamed = rename_reels_in_edl(edl, reel_map)
    except (RenameError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    output = edl_to_json(renamed, indent=2)

    if args.output:
        with open(args.output, "w") as fh:
            fh.write(output)
    else:
        print(output)


def main() -> None:
    parser = build_rename_parser()
    args = parser.parse_args()
    cmd_rename(args)


if __name__ == "__main__":
    main()
