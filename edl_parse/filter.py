"""Filter EDL events based on various criteria."""

from typing import List, Optional, Callable
from edl_parse.parser import EDL, EDLEvent


def filter_by_reel(events: List[EDLEvent], reel: str) -> List[EDLEvent]:
    """Return events matching the given reel name (case-insensitive)."""
    reel_lower = reel.lower()
    return [e for e in events if e.reel.lower() == reel_lower]


def filter_by_edit_type(events: List[EDLEvent], edit_type: str) -> List[EDLEvent]:
    """Return events matching the given edit type (e.g. 'C', 'D')."""
    edit_type_upper = edit_type.upper()
    return [e for e in events if e.edit_type.upper() == edit_type_upper]


def filter_by_event_number_range(
    events: List[EDLEvent],
    start: Optional[int] = None,
    end: Optional[int] = None,
) -> List[EDLEvent]:
    """Return events whose event number falls within [start, end] (inclusive)."""
    result = []
    for event in events:
        try:
            num = int(event.event_number)
        except (ValueError, TypeError):
            continue
        if start is not None and num < start:
            continue
        if end is not None and num > end:
            continue
        result.append(event)
    return result


def filter_events(
    events: List[EDLEvent],
    reel: Optional[str] = None,
    edit_type: Optional[str] = None,
    event_start: Optional[int] = None,
    event_end: Optional[int] = None,
    custom: Optional[Callable[[EDLEvent], bool]] = None,
) -> List[EDLEvent]:
    """Apply one or more filters to a list of EDL events."""
    result = list(events)
    if reel is not None:
        result = filter_by_reel(result, reel)
    if edit_type is not None:
        result = filter_by_edit_type(result, edit_type)
    if event_start is not None or event_end is not None:
        result = filter_by_event_number_range(result, event_start, event_end)
    if custom is not None:
        result = [e for e in result if custom(e)]
    return result


def filter_edl_events(
    edl: EDL,
    reel: Optional[str] = None,
    edit_type: Optional[str] = None,
    event_start: Optional[int] = None,
    event_end: Optional[int] = None,
    custom: Optional[Callable[[EDLEvent], bool]] = None,
) -> EDL:
    """Return a new EDL instance with filtered events."""
    filtered = filter_events(
        edl.events,
        reel=reel,
        edit_type=edit_type,
        event_start=event_start,
        event_end=event_end,
        custom=custom,
    )
    new_edl = EDL()
    new_edl.title = edl.title
    new_edl.fcm = edl.fcm
    new_edl.events = filtered
    return new_edl
