"""Merge multiple EDL objects into a single EDL."""

from typing import List, Optional
from edl_parse.parser import EDL, EDLEvent


class MergeError(Exception):
    """Raised when EDL merging fails."""
    pass


def _renumber_events(events: List[EDLEvent], start: int = 1) -> List[EDLEvent]:
    """Return a new list of events with sequential event numbers starting at start."""
    renumbered = []
    for i, event in enumerate(events):
        new_event = EDLEvent(
            event_number=str(start + i).zfill(3),
            reel=event.reel,
            track=event.track,
            edit_type=event.edit_type,
            source_in=event.source_in,
            source_out=event.source_out,
            record_in=event.record_in,
            record_out=event.record_out,
            clip_name=event.clip_name,
            comments=list(event.comments),
        )
        renumbered.append(new_event)
    return renumbered


def merge_edls(
    edls: List[EDL],
    title: Optional[str] = None,
    fcm: Optional[str] = None,
    renumber: bool = True,
) -> EDL:
    """Merge a list of EDL objects into a single EDL.

    Args:
        edls: List of EDL instances to merge.
        title: Title for the merged EDL. Defaults to the first EDL's title.
        fcm: FCM value for the merged EDL. Defaults to the first EDL's FCM.
        renumber: If True, renumber all events sequentially from 001.

    Returns:
        A new EDL containing all events from the input EDLs.

    Raises:
        MergeError: If the edls list is empty.
    """
    if not edls:
        raise MergeError("Cannot merge an empty list of EDLs.")

    merged_title = title if title is not None else edls[0].title
    merged_fcm = fcm if fcm is not None else edls[0].fcm

    all_events: List[EDLEvent] = []
    for edl in edls:
        all_events.extend(edl.events)

    if renumber:
        all_events = _renumber_events(all_events, start=1)

    merged = EDL(title=merged_title, fcm=merged_fcm)
    merged.events = all_events
    return merged
