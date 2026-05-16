"""CLI entry point for EDL comparison."""

import argparse
import json
import sys

from edl_parse.parser import parse_edl
from edl_parse.comparator import compare_edls, CompareError


def build_compare_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compare two EDL files and report differences."
    )
    parser.add_argument("base", help="Path to the base EDL file.")
    parser.add_argument("updated", help="Path to the updated EDL file.")
    parser.add_argument(
        "--json",
        action="store_true",
        dest="output_json",
        help="Output differences as JSON.",
    )
    parser.add_argument(
        "--exit-code",
        action="store_true",
        help="Exit with code 1 if differences are found.",
    )
    return parser


def cmd_compare(args: argparse.Namespace) -> None:
    try:
        with open(args.base, "r") as f:
            base_edl = parse_edl(f.read())
        with open(args.updated, "r") as f:
            updated_edl = parse_edl(f.read())
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(f"Parse error: {e}", file=sys.stderr)
        sys.exit(2)

    try:
        report = compare_edls(base_edl, updated_edl)
    except CompareError as e:
        print(str(e), file=sys.stderr)
        sys.exit(2)

    if args.output_json:
        output = {
            "base_title": report.base_title,
            "updated_title": report.updated_title,
            "events_only_in_base": report.events_only_in_base,
            "events_only_in_updated": report.events_only_in_updated,
            "field_diffs": [
                {
                    "event_number": d.event_number,
                    "field": d.field_name,
                    "base": d.base_value,
                    "updated": d.updated_value,
                }
                for d in report.field_diffs
            ],
        }
        print(json.dumps(output, indent=2))
    else:
        print(report.summary())
        for d in report.field_diffs:
            print(f"  [{d.event_number}] {d.field_name}: {d.base_value!r} -> {d.updated_value!r}")
        for ev in report.events_only_in_base:
            print(f"  Only in base: event {ev}")
        for ev in report.events_only_in_updated:
            print(f"  Only in updated: event {ev}")

    if args.exit_code and report.has_differences:
        sys.exit(1)


def main():
    parser = build_compare_parser()
    args = parser.parse_args()
    cmd_compare(args)


if __name__ == "__main__":
    main()
