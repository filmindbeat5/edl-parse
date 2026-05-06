"""Converter module to transform parsed EDL objects into JSON-serializable dicts."""

import json
from typing import Any, Dict

from edl_parse.parser import EDL, EDLEvent


def event_to_dict(event: EDLEvent) -> Dict[str, Any]:
    """Convert an EDLEvent dataclass to a plain dictionary."""
    return {
        "event_number": event.event_number,
        "reel": event.reel,
        "track": event.track,
        "edit_type": event.edit_type,
        "transition": event.transition,
        "source_in": event.source_in,
        "source_out": event.source_out,
        "record_in": event.record_in,
        "record_out": event.record_out,
        "clip_name": event.clip_name,
        "comments": event.comments,
    }


def edl_to_dict(edl: EDL) -> Dict[str, Any]:
    """Convert an EDL dataclass to a plain dictionary."""
    return {
        "title": edl.title,
        "fcm": edl.fcm,
        "events": [event_to_dict(e) for e in edl.events],
    }


def edl_to_json(edl: EDL, indent: int = 2) -> str:
    """Serialize an EDL dataclass to a JSON string."""
    return json.dumps(edl_to_dict(edl), indent=indent)


def edl_file_to_json(edl_path: str, output_path: str = None, indent: int = 2) -> str:
    """Read an EDL file, parse it, and return (or write) JSON output.

    Args:
        edl_path: Path to the source .edl file.
        output_path: Optional path to write the JSON output file.
        indent: JSON indentation level.

    Returns:
        JSON string representation of the EDL.
    """
    from edl_parse.parser import parse_edl

    with open(edl_path, "r", encoding="utf-8") as fh:
        content = fh.read()

    edl = parse_edl(content)
    json_str = edl_to_json(edl, indent=indent)

    if output_path:
        with open(output_path, "w", encoding="utf-8") as fh:
            fh.write(json_str)

    return json_str
