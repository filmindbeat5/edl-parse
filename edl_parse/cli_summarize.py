"""CLI entry point for the EDL summarizer."""

import argparse
import sys

from edl_parse.parser import parse_edl
from edl_parse.summarizer import SummaryError, summarize_edl, summarize_edl_brief


def build_summarize_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="edl-summarize",
        description="Print a human-readable summary of an EDL file.",
    )
    parser.add_argument("input", help="Path to the EDL file.")
    parser.add_argument(
        "--brief",
        action="store_true",
        default=False,
        help="Print a single-line brief summary instead of full detail.",
    )
    parser.add_argument(
        "--output",
        metavar="FILE",
        default=None,
        help="Write summary to FILE instead of stdout.",
    )
    return parser


def cmd_summarize(args: argparse.Namespace) -> None:
    try:
        with open(args.input, "r") as fh:
            raw = fh.read()
    except OSError as exc:
        print(f"Error reading file: {exc}", file=sys.stderr)
        sys.exit(1)

    edl = parse_edl(raw)

    try:
        if args.brief:
            result = summarize_edl_brief(edl)
        else:
            result = summarize_edl(edl)
    except SummaryError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)

    if args.output:
        try:
            with open(args.output, "w") as fh:
                fh.write(result + "\n")
        except OSError as exc:
            print(f"Error writing output: {exc}", file=sys.stderr)
            sys.exit(1)
    else:
        print(result)


def main() -> None:
    parser = build_summarize_parser()
    args = parser.parse_args()
    cmd_summarize(args)


if __name__ == "__main__":
    main()
