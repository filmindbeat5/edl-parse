"""CLI sub-command for formatting EDL files as human-readable text."""

import argparse
import sys
from edl_parse.parser import parse_edl
from edl_parse.formatter import format_edl_table, format_edl_summary


def build_format_parser(subparsers: argparse._SubParsersAction) -> None:
    """Register the 'format' sub-command onto an existing subparsers object."""
    fmt_parser = subparsers.add_parser(
        "format",
        help="Display an EDL file in a human-readable format.",
    )
    fmt_parser.add_argument(
        "input",
        metavar="INPUT",
        help="Path to the EDL file to format.",
    )
    fmt_parser.add_argument(
        "--mode",
        choices=["table", "summary"],
        default="table",
        help="Output mode: 'table' (default) or 'summary'.",
    )
    fmt_parser.add_argument(
        "--output",
        metavar="OUTPUT",
        default=None,
        help="Write output to this file instead of stdout.",
    )
    fmt_parser.set_defaults(func=cmd_format)


def cmd_format(args: argparse.Namespace) -> int:
    """Execute the format sub-command."""
    try:
        with open(args.input, "r") as fh:
            raw = fh.read()
    except FileNotFoundError:
        print(f"Error: file not found: {args.input}", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"Error reading file: {exc}", file=sys.stderr)
        return 1

    edl = parse_edl(raw)

    if args.mode == "summary":
        output = format_edl_summary(edl)
    else:
        output = format_edl_table(edl)

    if args.output:
        try:
            with open(args.output, "w") as fh:
                fh.write(output)
                fh.write("\n")
        except OSError as exc:
            print(f"Error writing file: {exc}", file=sys.stderr)
            return 1
    else:
        print(output)

    return 0
