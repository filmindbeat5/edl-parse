"""Deduplication utilities for EDL events."""

from typing import List, Optional
from edl_parse.parser import EDL, EDLEvent


def _event_key(event: EDLEvent, key_fields: Optional[List[str]] = None) -> tuple:
    """Build a hashable key from event fields for comparison."""
    if key_fields is None:
        key_fields = ["reel", "source_in", "source_out", "record_in", "record_out"]
    return tuple(getattr(event, field, None) for field in key_fields)


def find_duplicates(events: List[EDLEvent], key_fields: Optional[List[str]] = None) -> List[List[EDLEvent]]:
    """Return groups of duplicate events based on key fields.

    Each group contains two or more events that share the same key.
    """
    seen: dict = {}
    for event in events:
        key = _event_key(event, key_fields)
        seen.setdefault(key, []).append(event)
    return [group for group in seen.values() if len(group) > 1]


def remove_duplicates(
    events: List[EDLEvent],
    key_fields: Optional[List[str]] = None,
    keep: str = "first",
) -> List[EDLEvent]:
    """Return a new list of events with duplicates removed.

    Args:
        events: List of EDLEvent objects.
        key_fields: Fields used to determine equality. Defaults to timecode + reel.
        keep: 'first' keeps the earliest occurrence; 'last' keeps the latest.

    Returns:
        Deduplicated list of EDLEvent objects.
    """
    if keep not in ("first", "last"):
        raise ValueError("keep must be 'first' or 'last'")

    ordered = events if keep == "first" else list(reversed(events))
    seen: set = set()
    result: List[EDLEvent] = []
    for event in ordered:
        key = _event_key(event, key_fields)
        if key not in seen:
            seen.add(key)
            result.append(event)

    if keep == "last":
        result = list(reversed(result))
    return result


def deduplicate_edl(
    edl: EDL,
    key_fields: Optional[List[str]] = None,
    keep: str = "first",
) -> EDL:
    """Return a new EDL with duplicate events removed.

    The returned EDL preserves the original title and FCM.
    Events are re-numbered sequentially after deduplication.
    """
    deduped = remove_duplicates(edl.events, key_fields=key_fields, keep=keep)
    new_edl = EDL(title=edl.title, fcm=edl.fcm)
    for idx, event in enumerate(deduped, start=1):
        event.event_number = str(idx).zfill(3)
        new_edl.events.append(event)
    return new_edl
