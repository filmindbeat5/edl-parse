"""CLI interface for patching EDL event fields."""

import argparse
import json
import sys

from edl_parse.parser import parse_edl
from edl_parse.patcher import patch_edl, PatchError
from edl_parse.converter import edl_to_json


def build_patch_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="edl-patch",
        description="Patch fields on EDL events by event number or reel.",
    )
    parser.add_argument("input", help="Path to input EDL file.")
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument(
        "--event-number", metavar="NUM",
        help="Event number to patch.",
    )
    target.add_argument(
        "--reel", metavar="REEL",
        help="Reel name to patch (all matching events).",
    )
    parser.add_argument(
        "--set", dest="fields", metavar="KEY=VALUE", nargs="+", required=True,
        help="Fields to set, e.g. --set reel=NEW_REEL edit_type=D",
    )
    parser.add_argument(
        "--output", "-o", metavar="FILE",
        help="Write JSON output to file instead of stdout.",
    )
    return parser


def _parse_fields(raw: list) -> dict:
    fields = {}
    for item in raw:
        if "=" not in item:
            raise ValueError(f"Invalid field spec '{item}': expected KEY=VALUE.")
        key, _, value = item.partition("=")
        fields[key.strip()] = value.strip()
    return fields


def cmd_patch(args: argparse.Namespace) -> None:
    try:
        with open(args.input, "r") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    try:
        fields = _parse_fields(args.fields)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    edl = parse_edl(content)

    try:
        patched = patch_edl(
            edl,
            event_number=getattr(args, "event_number", None),
            reel=getattr(args, "reel", None),
            fields=fields,
        )
    except PatchError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    output = edl_to_json(patched, indent=2)

    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
    else:
        print(output)


def main():
    parser = build_patch_parser()
    args = parser.parse_args()
    cmd_patch(args)


if __name__ == "__main__":
    main()
