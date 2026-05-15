"""CLI entry point for applying timecode offsets to EDL record timecodes."""

import argparse
import json
import sys

from edl_parse.parser import parse_edl
from edl_parse.offsetter import offset_edl_events, OffsetError
from edl_parse.converter import edl_to_dict


def build_offset_parser() -> argparse.ArgumentParser:
    """Build and return the argument parser for the offset command."""
    parser = argparse.ArgumentParser(
        prog="edl-offset",
        description="Apply a timecode offset to record in/out points in an EDL.",
    )
    parser.add_argument(
        "input",
        help="Path to the input EDL file.",
    )
    parser.add_argument(
        "offset",
        help="Timecode offset to apply (e.g. '00:00:10:00'). Prefix with '-' to subtract.",
    )
    parser.add_argument(
        "--fps",
        type=float,
        default=25.0,
        help="Frames per second used for timecode calculation (default: 25).",
    )
    parser.add_argument(
        "--output",
        "-o",
        default=None,
        help="Path to write the resulting JSON output. Defaults to stdout.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        default=False,
        help="Output result as JSON (default behaviour; flag kept for explicitness).",
    )
    return parser


def cmd_offset(args: argparse.Namespace) -> int:
    """Execute the offset command.

    Reads the EDL from *args.input*, applies *args.offset* to every event's
    record in/out timecodes, then writes JSON to *args.output* or stdout.

    Returns an exit code (0 = success, 1 = error).
    """
    try:
        with open(args.input, "r") as fh:
            edl = parse_edl(fh.read())
    except FileNotFoundError:
        print(f"Error: file not found: {args.input}", file=sys.stderr)
        return 1
    except Exception as exc:  # noqa: BLE001
        print(f"Error reading EDL: {exc}", file=sys.stderr)
        return 1

    try:
        updated_edl = offset_edl_events(edl, args.offset, fps=args.fps)
    except OffsetError as exc:
        print(f"Offset error: {exc}", file=sys.stderr)
        return 1

    output_data = json.dumps(edl_to_dict(updated_edl), indent=2)

    if args.output:
        try:
            with open(args.output, "w") as fh:
                fh.write(output_data)
                fh.write("\n")
        except OSError as exc:
            print(f"Error writing output: {exc}", file=sys.stderr)
            return 1
    else:
        print(output_data)

    return 0


def main() -> None:  # pragma: no cover
    """Entry point for the edl-offset CLI command."""
    parser = build_offset_parser()
    args = parser.parse_args()
    sys.exit(cmd_offset(args))


if __name__ == "__main__":  # pragma: no cover
    main()
