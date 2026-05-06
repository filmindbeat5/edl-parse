"""Splitter module: split an EDL into multiple EDLs by reel or edit type."""

from typing import Dict, List
from edl_parse.parser import EDL, EDLEvent


class SplitError(Exception):
    """Raised when splitting fails."""
    pass


def split_by_reel(edl: EDL) -> Dict[str, EDL]:
    """Split an EDL into separate EDLs, one per reel name.

    Args:
        edl: The source EDL to split.

    Returns:
        A dict mapping reel name -> EDL containing only events for that reel.
    """
    if not edl.events:
        raise SplitError("Cannot split an EDL with no events.")

    buckets: Dict[str, List[EDLEvent]] = {}
    for event in edl.events:
        reel = event.reel.upper()
        buckets.setdefault(reel, []).append(event)

    result: Dict[str, EDL] = {}
    for reel, events in buckets.items():
        child = EDL()
        child.title = edl.title
        child.fcm = edl.fcm
        child.events = events
        result[reel] = child

    return result


def split_by_edit_type(edl: EDL) -> Dict[str, EDL]:
    """Split an EDL into separate EDLs, one per edit type (C, D, W, etc.).

    Args:
        edl: The source EDL to split.

    Returns:
        A dict mapping edit type -> EDL containing only events of that type.
    """
    if not edl.events:
        raise SplitError("Cannot split an EDL with no events.")

    buckets: Dict[str, List[EDLEvent]] = {}
    for event in edl.events:
        etype = event.edit_type.upper()
        buckets.setdefault(etype, []).append(event)

    result: Dict[str, EDL] = {}
    for etype, events in buckets.items():
        child = EDL()
        child.title = edl.title
        child.fcm = edl.fcm
        child.events = events
        result[etype] = child

    return result


def split_into_chunks(edl: EDL, chunk_size: int) -> List[EDL]:
    """Split an EDL into fixed-size chunks of events.

    Args:
        edl: The source EDL to split.
        chunk_size: Maximum number of events per chunk.

    Returns:
        A list of EDL objects each containing at most chunk_size events.
    """
    if chunk_size < 1:
        raise SplitError("chunk_size must be at least 1.")
    if not edl.events:
        raise SplitError("Cannot split an EDL with no events.")

    chunks: List[EDL] = []
    for i in range(0, len(edl.events), chunk_size):
        child = EDL()
        child.title = edl.title
        child.fcm = edl.fcm
        child.events = edl.events[i:i + chunk_size]
        chunks.append(child)

    return chunks
