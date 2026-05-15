"""Replace field values across EDL events."""

from typing import Optional
from edl_parse.parser import EDL, EDLEvent


class ReplaceError(Exception):
    def __str__(self):
        return f"ReplaceError: {self.args[0]}"


ALLOWED_FIELDS = {"reel", "edit_type", "source_in", "source_out", "record_in", "record_out"}


def replace_field_value(
    events: list,
    field: str,
    old_value: str,
    new_value: str,
    case_sensitive: bool = True,
) -> list:
    """Return a new list of events with matching field values replaced."""
    if field not in ALLOWED_FIELDS:
        raise ReplaceError(
            f"Field '{field}' is not replaceable. Allowed: {sorted(ALLOWED_FIELDS)}"
        )
    if not old_value:
        raise ReplaceError("old_value must not be empty.")

    updated = []
    for event in events:
        current = getattr(event, field, None)
        if current is None:
            updated.append(event)
            continue
        match = (
            current == old_value
            if case_sensitive
            else current.lower() == old_value.lower()
        )
        if match:
            new_event = EDLEvent(
                event_number=event.event_number,
                reel=event.reel,
                edit_type=event.edit_type,
                source_in=event.source_in,
                source_out=event.source_out,
                record_in=event.record_in,
                record_out=event.record_out,
            )
            setattr(new_event, field, new_value)
            if hasattr(event, "note"):
                new_event.note = event.note
            updated.append(new_event)
        else:
            updated.append(event)
    return updated


def replace_in_edl(
    edl: EDL,
    field: str,
    old_value: str,
    new_value: str,
    case_sensitive: bool = True,
) -> EDL:
    """Return a new EDL with field replacements applied to all events."""
    new_events = replace_field_value(
        edl.events, field, old_value, new_value, case_sensitive
    )
    new_edl = EDL(title=edl.title, fcm=edl.fcm)
    new_edl.events = new_events
    return new_edl
