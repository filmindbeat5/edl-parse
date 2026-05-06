"""Command-line interface for edl-parse."""

import argparse
import sys
import json
from pathlib import Path

from .converter import edl_file_to_json
from .parser import parse_edl
from .validator import validate_edl


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="edl-parse",
        description="Parse and convert EDL files to JSON.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    convert_cmd = subparsers.add_parser("convert", help="Convert an EDL file to JSON.")
    convert_cmd.add_argument("input", type=Path, help="Path to the EDL file.")
    convert_cmd.add_argument(
        "-o", "--output", type=Path, default=None,
        help="Output JSON file path. Prints to stdout if omitted."
    )
    convert_cmd.add_argument(
        "--indent", type=int, default=2,
        help="JSON indentation level (default: 2)."
    )

    validate_cmd = subparsers.add_parser("validate", help="Validate an EDL file.")
    validate_cmd.add_argument("input", type=Path, help="Path to the EDL file.")

    return parser


def cmd_convert(args: argparse.Namespace) -> int:
    if not args.input.exists():
        print(f"Error: File not found: {args.input}", file=sys.stderr)
        return 1
    try:
        json_output = edl_file_to_json(str(args.input), indent=args.indent)
    except Exception as exc:
        print(f"Error parsing EDL: {exc}", file=sys.stderr)
        return 1

    if args.output:
        args.output.write_text(json_output, encoding="utf-8")
        print(f"Written to {args.output}")
    else:
        print(json_output)
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    if not args.input.exists():
        print(f"Error: File not found: {args.input}", file=sys.stderr)
        return 1
    try:
        edl_text = args.input.read_text(encoding="utf-8")
        edl = parse_edl(edl_text)
    except Exception as exc:
        print(f"Error parsing EDL: {exc}", file=sys.stderr)
        return 1

    result = validate_edl(edl)
    print(result)
    return 0 if result.valid else 1


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "convert":
        sys.exit(cmd_convert(args))
    elif args.command == "validate":
        sys.exit(cmd_validate(args))


if __name__ == "__main__":
    main()
