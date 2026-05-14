"""CLI entry point for diffing two EDL files."""

import argparse
import sys

from edl_parse.parser import parse_edl
from edl_parse.differ import diff_edls, diff_summary, DiffError
from edl_parse.converter import edl_to_json


def build_diff_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="edl-diff",
        description="Compare two EDL files and report differences.",
    )
    parser.add_argument("base", help="Base EDL file path.")
    parser.add_argument("updated", help="Updated EDL file path.")
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output diff as JSON instead of plain text.",
    )
    parser.add_argument(
        "--exit-code",
        action="store_true",
        dest="exit_code",
        help="Exit with code 1 if differences are found.",
    )
    return parser


def cmd_diff(args: argparse.Namespace) -> None:
    try:
        with open(args.base, "r") as f:
            base_text = f.read()
        with open(args.updated, "r") as f:
            updated_text = f.read()
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    base_edl = parse_edl(base_text)
    updated_edl = parse_edl(updated_text)

    try:
        diff = diff_edls(base_edl, updated_edl)
    except DiffError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        import json
        output = {
            "added": [e.__dict__ for e in diff.added],
            "removed": [e.__dict__ for e in diff.removed],
            "changed": [
                {"base": b.__dict__, "updated": u.__dict__}
                for b, u in diff.changed
            ],
        }
        print(json.dumps(output, indent=2))
    else:
        print(diff_summary(diff))

    if args.exit_code and diff.has_differences:
        sys.exit(1)


def main():
    parser = build_diff_parser()
    args = parser.parse_args()
    cmd_diff(args)


if __name__ == "__main__":
    main()
