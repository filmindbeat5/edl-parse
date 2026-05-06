"""Sorting and ordering utilities for EDL events."""

from typing import List, Optional
from edl_parse.parser import EDL, EDLEvent


def _timecode_to_frames(timecode: str, fps: int = 25) -> int:
    """Convert a timecode string HH:MM:SS:FF to total frame count."""
    parts = timecode.strip().replace(";", ":").split(":")
    if len(parts) != 4:
        raise ValueError(f"Invalid timecode format: {timecode}")
    hours, minutes, seconds, frames = (int(p) for p in parts)
    return ((hours * 3600) + (minutes * 60) + seconds) * fps + frames


def sort_events_by_record_in(
    events: List[EDLEvent], fps: int = 25, reverse: bool = False
) -> List[EDLEvent]:
    """Return events sorted by their record_in timecode.

    Args:
        events: List of EDLEvent objects to sort.
        fps: Frames per second used for timecode conversion.
        reverse: If True, sort in descending order.

    Returns:
        A new sorted list of EDLEvent objects.
    """
    return sorted(
        events,
        key=lambda e: _timecode_to_frames(e.record_in, fps),
        reverse=reverse,
    )


def sort_events_by_source_in(
    events: List[EDLEvent], fps: int = 25, reverse: bool = False
) -> List[EDLEvent]:
    """Return events sorted by their source_in timecode.

    Args:
        events: List of EDLEvent objects to sort.
        fps: Frames per second used for timecode conversion.
        reverse: If True, sort in descending order.

    Returns:
        A new sorted list of EDLEvent objects.
    """
    return sorted(
        events,
        key=lambda e: _timecode_to_frames(e.source_in, fps),
        reverse=reverse,
    )


def sort_edl_events(
    edl: EDL,
    key: str = "record_in",
    fps: int = 25,
    reverse: bool = False,
) -> EDL:
    """Return a new EDL with events sorted by the given key.

    Args:
        edl: The source EDL object.
        key: One of 'record_in' or 'source_in'.
        fps: Frames per second for timecode conversion.
        reverse: If True, sort in descending order.

    Returns:
        A new EDL instance with sorted events.
    """
    if key == "record_in":
        sorted_events = sort_events_by_record_in(edl.events, fps=fps, reverse=reverse)
    elif key == "source_in":
        sorted_events = sort_events_by_source_in(edl.events, fps=fps, reverse=reverse)
    else:
        raise ValueError(f"Unsupported sort key: '{key}'. Use 'record_in' or 'source_in'.")

    new_edl = EDL()
    new_edl.title = edl.title
    new_edl.fcm = edl.fcm
    new_edl.events = sorted_events
    return new_edl
