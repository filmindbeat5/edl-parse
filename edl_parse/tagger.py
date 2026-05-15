"""Tag events in an EDL with user-defined labels based on reel or edit type patterns."""

from typing import Dict, List, Optional
from edl_parse.parser import EDL, EDLEvent


class TagError(Exception):
    def __str__(self) -> str:
        return f"TagError: {self.args[0]}"


def tag_event(
    event: EDLEvent,
    tags: Dict[str, str],
    field: str = "reel",
) -> EDLEvent:
    """Add a 'tag' attribute to an event based on a field-to-tag mapping.

    Args:
        event: The EDLEvent to tag.
        tags: Mapping of field value (case-insensitive) to tag label.
        field: The event attribute to match against (default: 'reel').

    Returns:
        The same event with a 'tag' attribute set (or None if no match).

    Raises:
        TagError: If the field does not exist on the event.
    """
    if not hasattr(event, field):
        raise TagError(f"Event has no field '{field}'")

    value = getattr(event, field)
    if value is None:
        event.tag = None
        return event

    normalized = value.strip().lower()
    for key, label in tags.items():
        if key.strip().lower() == normalized:
            event.tag = label
            return event

    event.tag = None
    return event


def tag_events(
    events: List[EDLEvent],
    tags: Dict[str, str],
    field: str = "reel",
) -> List[EDLEvent]:
    """Tag a list of events in place.

    Args:
        events: List of EDLEvent objects.
        tags: Mapping of field value to tag label.
        field: The event attribute to match against.

    Returns:
        The same list with tag attributes set on each event.
    """
    for event in events:
        tag_event(event, tags, field=field)
    return events


def tag_edl_events(
    edl: EDL,
    tags: Dict[str, str],
    field: str = "reel",
) -> EDL:
    """Tag all events in an EDL object.

    Args:
        edl: The EDL to process.
        tags: Mapping of field value to tag label.
        field: The event attribute to match against.

    Returns:
        The same EDL with tagged events.
    """
    tag_events(edl.events, tags, field=field)
    return edl
