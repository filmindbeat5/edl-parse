"""CLI entry point for the EDL field replacer."""

import argparse
import sys
import json

from edl_parse.parser import parse_edl
from edl_parse.replacer import replace_in_edl, ReplaceError, ALLOWED_FIELDS
from edl_parse.converter import edl_to_json


def build_replace_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Replace field values in an EDL file."
    )
    parser.add_argument("input", help="Path to input EDL file.")
    parser.add_argument(
        "--field",
        required=True,
        choices=sorted(ALLOWED_FIELDS),
        help="Field to apply replacement on.",
    )
    parser.add_argument("--old", required=True, help="Value to replace.")
    parser.add_argument("--new", required=True, help="Replacement value.")
    parser.add_argument(
        "--ignore-case",
        action="store_true",
        default=False,
        help="Perform case-insensitive matching.",
    )
    parser.add_argument(
        "--output", "-o", default=None, help="Output JSON file path (default: stdout)."
    )
    return parser


def cmd_replace(args) -> int:
    try:
        with open(args.input, "r") as fh:
            edl = parse_edl(fh.read())
    except FileNotFoundError:
        print(f"Error: file not found: {args.input}", file=sys.stderr)
        return 1

    try:
        result_edl = replace_in_edl(
            edl,
            field=args.field,
            old_value=args.old,
            new_value=args.new,
            case_sensitive=not args.ignore_case,
        )
    except ReplaceError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    output_json = edl_to_json(result_edl)

    if args.output:
        with open(args.output, "w") as fh:
            fh.write(output_json)
        print(f"Written to {args.output}")
    else:
        print(output_json)

    return 0


def main():
    parser = build_replace_parser()
    args = parser.parse_args()
    sys.exit(cmd_replace(args))


if __name__ == "__main__":
    main()
