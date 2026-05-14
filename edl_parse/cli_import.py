"""CLI entry point for importing EDL events from CSV or TSV files."""

import argparse
import json
import sys

from edl_parse.importer import csv_to_edl, tsv_to_edl, ImportError
from edl_parse.converter import edl_to_dict


def build_import_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="edl-import",
        description="Import events from a CSV or TSV file and output an EDL as JSON.",
    )
    parser.add_argument("input", help="Path to the CSV or TSV input file.")
    parser.add_argument("-o", "--output", help="Write JSON output to this file instead of stdout.")
    parser.add_argument("--tsv", action="store_true", help="Treat input as TSV (tab-separated).")
    parser.add_argument("--title", default="IMPORTED", help="EDL title for the output (default: IMPORTED).")
    parser.add_argument("--fcm", default="NON-DROP FRAME", help="Frame count mode (default: NON-DROP FRAME).")
    return parser


def cmd_import(args: argparse.Namespace) -> int:
    try:
        with open(args.input, "r", encoding="utf-8") as fh:
            text = fh.read()
    except OSError as exc:
        print(f"Error reading file: {exc}", file=sys.stderr)
        return 1

    try:
        if args.tsv:
            edl = tsv_to_edl(text, title=args.title, fcm=args.fcm)
        else:
            edl = csv_to_edl(text, title=args.title, fcm=args.fcm)
    except ImportError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    output = json.dumps(edl_to_dict(edl), indent=2)

    if args.output:
        try:
            with open(args.output, "w", encoding="utf-8") as fh:
                fh.write(output)
        except OSError as exc:
            print(f"Error writing output: {exc}", file=sys.stderr)
            return 1
    else:
        print(output)

    return 0


def main() -> None:
    parser = build_import_parser()
    args = parser.parse_args()
    sys.exit(cmd_import(args))


if __name__ == "__main__":
    main()
