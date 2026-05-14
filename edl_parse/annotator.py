"""Annotator module: add or update custom metadata annotations on EDL events."""

from typing import Dict, List, Optional
from edl_parse.parser import EDL, EDLEvent


class AnnotationError(Exception):
    """Raised when an annotation operation fails."""

    def __str__(self) -> str:
        return f"AnnotationError: {self.args[0]}"


def annotate_event(event: EDLEvent, key: str, value: str) -> EDLEvent:
    """Add or update a single annotation key/value on an event.

    Annotations are stored in event.notes as 'KEY=VALUE' entries.
    Returns the mutated event.
    """
    if not key or not key.strip():
        raise AnnotationError("Annotation key must not be empty.")
    tag = f"{key.strip()}={value.strip()}"
    existing = [n for n in event.notes if not n.startswith(f"{key.strip()}=")]
    event.notes = existing + [tag]
    return event


def annotate_events(
    events: List[EDLEvent],
    key: str,
    value: str,
    event_numbers: Optional[List[int]] = None,
) -> List[EDLEvent]:
    """Annotate a list of events with key=value.

    If event_numbers is provided, only events whose number is in the list
    are annotated. Otherwise all events are annotated.
    """
    if not key or not key.strip():
        raise AnnotationError("Annotation key must not be empty.")
    result = []
    for event in events:
        if event_numbers is None or event.event_number in event_numbers:
            annotate_event(event, key, value)
        result.append(event)
    return result


def annotate_edl(
    edl: EDL,
    key: str,
    value: str,
    event_numbers: Optional[List[int]] = None,
) -> EDL:
    """Annotate events in an EDL object in-place and return it."""
    edl.events = annotate_events(edl.events, key, value, event_numbers)
    return edl


def get_annotations(event: EDLEvent) -> Dict[str, str]:
    """Return a dict of all key=value annotations stored in event.notes."""
    annotations: Dict[str, str] = {}
    for note in event.notes:
        if "=" in note:
            k, _, v = note.partition("=")
            annotations[k.strip()] = v.strip()
    return annotations


def remove_annotation(event: EDLEvent, key: str) -> EDLEvent:
    """Remove an annotation by key from an event's notes. Returns the event."""
    event.notes = [n for n in event.notes if not n.startswith(f"{key.strip()}=")]
    return event
