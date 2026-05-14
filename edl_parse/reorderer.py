"""Reorder EDL events by custom field or sequence."""

from typing import List, Optional
from edl_parse.parser import EDL, EDLEvent


class ReorderError(Exception):
    def __str__(self):
        return f"ReorderError: {self.args[0]}"


VALID_FIELDS = ("event_number", "reel", "edit_type", "source_in", "source_out", "record_in", "record_out")


def reorder_by_field(events: List[EDLEvent], field: str, reverse: bool = False) -> List[EDLEvent]:
    """Return a new list of events sorted by the given field name."""
    if field not in VALID_FIELDS:
        raise ReorderError(f"Unknown sort field '{field}'. Valid fields: {VALID_FIELDS}")
    try:
        return sorted(events, key=lambda e: getattr(e, field) or "", reverse=reverse)
    except Exception as exc:
        raise ReorderError(f"Failed to sort by '{field}': {exc}") from exc


def reorder_by_custom_sequence(events: List[EDLEvent], sequence: List[str]) -> List[EDLEvent]:
    """Return events reordered so that reels appear in the given sequence order.
    Events whose reel is not in the sequence are appended at the end in original order.
    """
    if not sequence:
        raise ReorderError("Sequence list must not be empty.")
    order_map = {reel.upper(): idx for idx, reel in enumerate(sequence)}
    in_seq = [e for e in events if (e.reel or "").upper() in order_map]
    out_seq = [e for e in events if (e.reel or "").upper() not in order_map]
    in_seq_sorted = sorted(in_seq, key=lambda e: order_map[(e.reel or "").upper()])
    return in_seq_sorted + out_seq


def reorder_edl_events(
    edl: EDL,
    field: Optional[str] = None,
    sequence: Optional[List[str]] = None,
    reverse: bool = False,
) -> EDL:
    """Return a new EDL with events reordered. Provide either field or sequence."""
    if field is None and sequence is None:
        raise ReorderError("Provide either 'field' or 'sequence' to reorder events.")
    if field is not None and sequence is not None:
        raise ReorderError("Provide only one of 'field' or 'sequence', not both.")

    if field is not None:
        new_events = reorder_by_field(edl.events, field, reverse=reverse)
    else:
        new_events = reorder_by_custom_sequence(edl.events, sequence)

    new_edl = EDL()
    new_edl.title = edl.title
    new_edl.fcm = edl.fcm
    new_edl.events = new_events
    return new_edl
