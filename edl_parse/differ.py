"""Diff two EDLs and report added, removed, and changed events."""

from dataclasses import dataclass, field
from typing import List, Dict, Tuple
from edl_parse.parser import EDL, EDLEvent


class DiffError(Exception):
    def __str__(self):
        return f"DiffError: {self.args[0]}"


@dataclass
class EDLDiff:
    added: List[EDLEvent] = field(default_factory=list)
    removed: List[EDLEvent] = field(default_factory=list)
    changed: List[Tuple[EDLEvent, EDLEvent]] = field(default_factory=list)

    @property
    def has_differences(self) -> bool:
        return bool(self.added or self.removed or self.changed)


def _event_key(event: EDLEvent) -> str:
    """Unique key for matching events across EDLs."""
    return str(event.event_number)


def _events_equal(a: EDLEvent, b: EDLEvent) -> bool:
    """Return True if two events are functionally identical."""
    return (
        a.reel == b.reel
        and a.edit_type == b.edit_type
        and a.source_in == b.source_in
        and a.source_out == b.source_out
        and a.record_in == b.record_in
        and a.record_out == b.record_out
    )


def diff_edls(base: EDL, updated: EDL) -> EDLDiff:
    """Compare two EDLs and return an EDLDiff describing the differences."""
    if not isinstance(base, EDL) or not isinstance(updated, EDL):
        raise DiffError("Both arguments must be EDL instances.")

    base_map: Dict[str, EDLEvent] = {_event_key(e): e for e in base.events}
    updated_map: Dict[str, EDLEvent] = {_event_key(e): e for e in updated.events}

    result = EDLDiff()

    for key, event in updated_map.items():
        if key not in base_map:
            result.added.append(event)
        elif not _events_equal(base_map[key], event):
            result.changed.append((base_map[key], event))

    for key, event in base_map.items():
        if key not in updated_map:
            result.removed.append(event)

    return result


def diff_summary(diff: EDLDiff) -> str:
    """Return a human-readable summary of an EDLDiff."""
    lines = []
    lines.append(f"Added:   {len(diff.added)} event(s)")
    lines.append(f"Removed: {len(diff.removed)} event(s)")
    lines.append(f"Changed: {len(diff.changed)} event(s)")
    if not diff.has_differences:
        lines.append("No differences found.")
    return "\n".join(lines)
