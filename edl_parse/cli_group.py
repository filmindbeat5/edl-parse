"""CLI entry point for grouping EDL events by a field."""

import argparse
import json
import sys
from edl_parse.parser import parse_edl
from edl_parse.converter import edl_to_dict
from edl_parse.grouper import group_edl_events, VALID_FIELDS, GroupError


def build_group_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="edl-group",
        description="Group EDL events by a specified field and output as JSON.",
    )
    parser.add_argument("input", help="Path to input EDL file")
    parser.add_argument(
        "--field",
        required=True,
        choices=sorted(VALID_FIELDS),
        help="Field to group events by",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Path to output JSON file (default: stdout)",
    )
    parser.add_argument(
        "--indent",
        type=int,
        default=2,
        help="JSON indent level (default: 2)",
    )
    return parser


def cmd_group(args: argparse.Namespace) -> None:
    """Execute the group command."""
    try:
        with open(args.input, "r") as fh:
            raw = fh.read()
    except OSError as exc:
        print(f"Error reading file: {exc}", file=sys.stderr)
        sys.exit(1)

    edl = parse_edl(raw)

    try:
        grouped = group_edl_events(edl, args.field)
    except GroupError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)

    output = {
        key: edl_to_dict(sub_edl) for key, sub_edl in sorted(grouped.items())
    }
    serialized = json.dumps(output, indent=args.indent)

    if args.output:
        try:
            with open(args.output, "w") as fh:
                fh.write(serialized)
                fh.write("\n")
        except OSError as exc:
            print(f"Error writing file: {exc}", file=sys.stderr)
            sys.exit(1)
    else:
        print(serialized)


def main() -> None:
    parser = build_group_parser()
    args = parser.parse_args()
    cmd_group(args)


if __name__ == "__main__":
    main()
