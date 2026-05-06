"""CLI entry point for merging multiple EDL files into one."""

import argparse
import sys

from edl_parse.parser import parse_edl
from edl_parse.merger import merge_edls, MergeError
from edl_parse.converter import edl_to_json


def build_merge_parser() -> argparse.ArgumentParser:
    """Build and return the argument parser for the merge command."""
    parser = argparse.ArgumentParser(
        prog="edl-merge",
        description="Merge multiple EDL files into a single EDL JSON output.",
    )
    parser.add_argument(
        "inputs",
        nargs="+",
        metavar="INPUT",
        help="Two or more EDL files to merge.",
    )
    parser.add_argument(
        "-o", "--output",
        metavar="OUTPUT",
        help="Write JSON output to this file instead of stdout.",
    )
    parser.add_argument(
        "--title",
        metavar="TITLE",
        help="Override the title of the merged EDL.",
    )
    parser.add_argument(
        "--no-renumber",
        action="store_true",
        help="Preserve original event numbers instead of renumbering.",
    )
    return parser


def cmd_merge(args: argparse.Namespace) -> None:
    """Execute the merge command."""
    edls = []
    for path in args.inputs:
        try:
            with open(path, "r") as fh:
                content = fh.read()
            edls.append(parse_edl(content))
        except FileNotFoundError:
            print(f"Error: file not found: {path}", file=sys.stderr)
            sys.exit(1)

    try:
        merged = merge_edls(
            edls,
            title=args.title,
            renumber=not args.no_renumber,
        )
    except MergeError as exc:
        print(f"Merge error: {exc}", file=sys.stderr)
        sys.exit(1)

    json_output = edl_to_json(merged)

    if args.output:
        with open(args.output, "w") as fh:
            fh.write(json_output)
    else:
        print(json_output)


def main() -> None:
    parser = build_merge_parser()
    args = parser.parse_args()
    cmd_merge(args)


if __name__ == "__main__":
    main()
