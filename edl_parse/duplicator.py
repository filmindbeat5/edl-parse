"""Duplicate and clone EDL events with optional offset and renumbering."""

from dataclasses import dataclass, field
from typing import List, Optional
from edl_parse.parser import EDLEvent, EDL


class DuplicateError(Exception):
    def __str__(self):
        return f"DuplicateError: {self.args[0]}"


def _copy_event(event: EDLEvent) -> EDLEvent:
    """Return a shallow copy of an EDLEvent."""
    copy = EDLEvent()
    copy.event_number = event.event_number
    copy.reel = event.reel
    copy.edit_type = event.edit_type
    copy.transition = event.transition
    copy.source_in = event.source_in
    copy.source_out = event.source_out
    copy.record_in = event.record_in
    copy.record_out = event.record_out
    copy.clip_name = event.clip_name
    copy.note = event.note
    return copy


def duplicate_event(event: EDLEvent, count: int = 1) -> List[EDLEvent]:
    """Return `count` copies of the given event.

    Args:
        event: The source EDLEvent to duplicate.
        count: Number of copies to produce (must be >= 1).

    Returns:
        A list of copied EDLEvent instances.

    Raises:
        DuplicateError: If count is less than 1.
    """
    if count < 1:
        raise DuplicateError("count must be >= 1")
    return [_copy_event(event) for _ in range(count)]


def duplicate_events(events: List[EDLEvent], count: int = 1) -> List[EDLEvent]:
    """Duplicate every event in the list `count` times.

    Each original event is followed immediately by its copies in the result.

    Args:
        events: Source list of EDLEvent objects.
        count: Number of times each event is duplicated (>= 1).

    Returns:
        Expanded list with duplicates interleaved.

    Raises:
        DuplicateError: If count is less than 1.
    """
    if count < 1:
        raise DuplicateError("count must be >= 1")
    result: List[EDLEvent] = []
    for event in events:
        result.append(event)
        result.extend(_copy_event(event) for _ in range(count))
    return result


def duplicate_edl_events(edl: EDL, count: int = 1) -> EDL:
    """Return a new EDL whose events are each duplicated `count` additional times.

    Event numbers are reassigned sequentially starting from 1.

    Args:
        edl: Source EDL.
        count: Number of additional copies per event.

    Returns:
        New EDL with duplicated events.

    Raises:
        DuplicateError: If count is less than 1.
    """
    expanded = duplicate_events(edl.events, count=count)
    for idx, ev in enumerate(expanded, start=1):
        ev.event_number = str(idx).zfill(3)
    new_edl = EDL()
    new_edl.title = edl.title
    new_edl.fcm = edl.fcm
    new_edl.events = expanded
    return new_edl
