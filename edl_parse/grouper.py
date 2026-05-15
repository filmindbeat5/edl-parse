"""Group EDL events by a specified field into named buckets."""

from typing import Dict, List, Optional
from edl_parse.parser import EDL, EDLEvent


class GroupError(Exception):
    def __str__(self) -> str:
        return f"GroupError: {self.args[0]}"


VALID_FIELDS = {"reel", "edit_type", "event_number"}


def group_events_by_field(
    events: List[EDLEvent], field: str
) -> Dict[str, List[EDLEvent]]:
    """Group a list of events by the value of a given field.

    Args:
        events: List of EDLEvent instances.
        field: Field name to group by. Must be one of VALID_FIELDS.

    Returns:
        Dict mapping field values to lists of matching events.

    Raises:
        GroupError: If field is not valid or events is not a list.
    """
    if not isinstance(events, list):
        raise GroupError("events must be a list")
    if field not in VALID_FIELDS:
        raise GroupError(
            f"Invalid field '{field}'. Must be one of: {sorted(VALID_FIELDS)}"
        )

    groups: Dict[str, List[EDLEvent]] = {}
    for event in events:
        value: Optional[str] = getattr(event, field, None)
        key = str(value) if value is not None else "__unknown__"
        groups.setdefault(key, []).append(event)
    return groups


def group_edl_events(
    edl: EDL, field: str
) -> Dict[str, EDL]:
    """Group events in an EDL by field, returning a dict of sub-EDLs.

    Each sub-EDL inherits the title and FCM of the source EDL.

    Args:
        edl: Source EDL instance.
        field: Field name to group by.

    Returns:
        Dict mapping field values to EDL instances.

    Raises:
        GroupError: If field is invalid.
    """
    grouped_events = group_events_by_field(edl.events, field)
    result: Dict[str, EDL] = {}
    for key, events in grouped_events.items():
        sub_edl = EDL()
        sub_edl.title = edl.title
        sub_edl.fcm = edl.fcm
        sub_edl.events = events
        result[key] = sub_edl
    return result
