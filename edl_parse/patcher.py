"""Patch specific fields on EDL events by event number or reel."""

from typing import Dict, Any, List, Optional
from edl_parse.parser import EDL, EDLEvent


class PatchError(Exception):
    def __str__(self):
        return f"PatchError: {self.args[0]}"


def patch_event_by_number(
    events: List[EDLEvent],
    event_number: str,
    fields: Dict[str, Any],
) -> List[EDLEvent]:
    """Apply field updates to the event matching event_number."""
    if not fields:
        raise PatchError("No fields provided for patching.")
    matched = False
    for event in events:
        if event.event_number == event_number:
            for key, value in fields.items():
                if not hasattr(event, key):
                    raise PatchError(f"EDLEvent has no field '{key}'.")
                setattr(event, key, value)
            matched = True
    if not matched:
        raise PatchError(f"No event found with event_number '{event_number}'.")
    return events


def patch_events_by_reel(
    events: List[EDLEvent],
    reel: str,
    fields: Dict[str, Any],
) -> List[EDLEvent]:
    """Apply field updates to all events matching reel (case-insensitive)."""
    if not fields:
        raise PatchError("No fields provided for patching.")
    reel_lower = reel.lower()
    for event in events:
        if event.reel.lower() == reel_lower:
            for key, value in fields.items():
                if not hasattr(event, key):
                    raise PatchError(f"EDLEvent has no field '{key}'.")
                setattr(event, key, value)
    return events


def patch_edl(
    edl: EDL,
    event_number: Optional[str] = None,
    reel: Optional[str] = None,
    fields: Optional[Dict[str, Any]] = None,
) -> EDL:
    """Patch events in an EDL by event_number or reel. Returns modified EDL."""
    if not fields:
        raise PatchError("No fields provided for patching.")
    if event_number is not None and reel is not None:
        raise PatchError("Specify either event_number or reel, not both.")
    if event_number is None and reel is None:
        raise PatchError("Must specify either event_number or reel.")
    if event_number is not None:
        patch_event_by_number(edl.events, event_number, fields)
    else:
        patch_events_by_reel(edl.events, reel, fields)
    return edl
