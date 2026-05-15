"""Map EDL events to a new structure using a field mapping dictionary."""

from typing import Dict, List, Optional
from edl_parse.parser import EDLEvent, EDL


class MapError(Exception):
    def __str__(self) -> str:
        return f"MapError: {self.args[0]}"


def map_event_fields(
    event: EDLEvent,
    field_map: Dict[str, str],
    drop_unmapped: bool = False,
) -> Dict[str, object]:
    """Return a dict representing the event with fields renamed per field_map.

    Args:
        event: The source EDLEvent.
        field_map: Mapping of original field names to new field names.
        drop_unmapped: If True, omit fields not present in field_map.

    Returns:
        A dict with renamed (and optionally filtered) fields.

    Raises:
        MapError: If field_map is empty.
    """
    if not field_map:
        raise MapError("field_map must not be empty")

    source = {
        "event_number": event.event_number,
        "reel": event.reel,
        "edit_type": event.edit_type,
        "transition": event.transition,
        "source_in": event.source_in,
        "source_out": event.source_out,
        "record_in": event.record_in,
        "record_out": event.record_out,
    }
    if hasattr(event, "note") and event.note is not None:
        source["note"] = event.note

    result: Dict[str, object] = {}
    for key, value in source.items():
        if key in field_map:
            result[field_map[key]] = value
        elif not drop_unmapped:
            result[key] = value

    return result


def map_events(
    events: List[EDLEvent],
    field_map: Dict[str, str],
    drop_unmapped: bool = False,
) -> List[Dict[str, object]]:
    """Apply map_event_fields to a list of events."""
    return [map_event_fields(e, field_map, drop_unmapped) for e in events]


def map_edl_events(
    edl: EDL,
    field_map: Dict[str, str],
    drop_unmapped: bool = False,
) -> List[Dict[str, object]]:
    """Apply field mapping to all events in an EDL.

    Raises:
        MapError: If the EDL has no events.
    """
    if not edl.events:
        raise MapError("EDL contains no events to map")
    return map_events(edl.events, field_map, drop_unmapped)
