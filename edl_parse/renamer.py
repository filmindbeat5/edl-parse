"""Reel renaming utilities for EDL events."""

from typing import Dict, Optional
from edl_parse.parser import EDL, EDLEvent


class RenameError(Exception):
    """Raised when a renaming operation fails."""
    pass


def rename_reel(event: EDLEvent, reel_map: Dict[str, str]) -> EDLEvent:
    """Return a copy of event with reel name replaced according to reel_map.

    Args:
        event: The source EDLEvent.
        reel_map: Mapping of old reel name -> new reel name.

    Returns:
        A new EDLEvent with the reel updated if a match is found.
    """
    new_reel = reel_map.get(event.reel, event.reel)
    return EDLEvent(
        event_number=event.event_number,
        reel=new_reel,
        edit_type=event.edit_type,
        transition=event.transition,
        source_in=event.source_in,
        source_out=event.source_out,
        record_in=event.record_in,
        record_out=event.record_out,
    )


def rename_reels_in_edl(edl: EDL, reel_map: Dict[str, str]) -> EDL:
    """Return a new EDL with all reel names replaced according to reel_map.

    Args:
        edl: The source EDL.
        reel_map: Mapping of old reel name -> new reel name.

    Returns:
        A new EDL instance with renamed reels.

    Raises:
        RenameError: If reel_map is empty.
    """
    if not reel_map:
        raise RenameError("reel_map must not be empty")

    new_edl = EDL(title=edl.title, fcm=edl.fcm)
    new_edl.events = [rename_reel(e, reel_map) for e in edl.events]
    return new_edl


def build_reel_map_from_prefix(events: list, prefix: str) -> Dict[str, str]:
    """Build a reel_map that adds a prefix to every unique reel name.

    Args:
        events: List of EDLEvent objects.
        prefix: String prefix to prepend to each reel name.

    Returns:
        Dict mapping original reel name to prefixed reel name.
    """
    unique_reels = {e.reel for e in events if e.reel}
    return {reel: f"{prefix}{reel}" for reel in unique_reels}
