"""Reverse the order of events in an EDL or event list."""

from edl_parse.parser import EDL, EDLEvent


class ReverseError(Exception):
    def __str__(self):
        return f"ReverseError: {self.args[0]}"


def reverse_events(events: list) -> list:
    """Return a new list of events in reversed order, renumbering sequentially."""
    if not isinstance(events, list):
        raise ReverseError("events must be a list")
    if len(events) == 0:
        return []

    reversed_events = list(reversed(events))
    renumbered = []
    for i, event in enumerate(reversed_events, start=1):
        new_event = EDLEvent(
            event_number=str(i).zfill(3),
            reel=event.reel,
            edit_type=event.edit_type,
            transition=event.transition,
            source_in=event.source_in,
            source_out=event.source_out,
            record_in=event.record_in,
            record_out=event.record_out,
        )
        if hasattr(event, 'note') and event.note:
            new_event.note = event.note
        renumbered.append(new_event)
    return renumbered


def reverse_edl(edl: EDL) -> EDL:
    """Return a new EDL with events in reversed order."""
    if not isinstance(edl, EDL):
        raise ReverseError("edl must be an EDL instance")
    if not edl.events:
        raise ReverseError("EDL has no events to reverse")

    new_edl = EDL()
    new_edl.title = edl.title
    new_edl.fcm = edl.fcm
    new_edl.events = reverse_events(edl.events)
    return new_edl
