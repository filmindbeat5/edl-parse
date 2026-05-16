"""Compare two EDL objects field-by-field and produce a structured comparison report."""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from edl_parse.parser import EDL, EDLEvent


class CompareError(Exception):
    def __str__(self):
        return f"CompareError: {self.args[0]}"


@dataclass
class FieldDiff:
    event_number: str
    field_name: str
    base_value: Any
    updated_value: Any


@dataclass
class ComparisonReport:
    base_title: str
    updated_title: str
    events_only_in_base: List[str] = field(default_factory=list)
    events_only_in_updated: List[str] = field(default_factory=list)
    field_diffs: List[FieldDiff] = field(default_factory=list)

    @property
    def has_differences(self) -> bool:
        return bool(
            self.events_only_in_base
            or self.events_only_in_updated
            or self.field_diffs
        )

    def summary(self) -> str:
        lines = [
            f"Base: {self.base_title}",
            f"Updated: {self.updated_title}",
            f"Events only in base: {len(self.events_only_in_base)}",
            f"Events only in updated: {len(self.events_only_in_updated)}",
            f"Field differences: {len(self.field_diffs)}",
        ]
        return "\n".join(lines)


EVENT_FIELDS = ["reel", "edit_type", "source_in", "source_out", "record_in", "record_out"]


def _event_index(events: List[EDLEvent]) -> Dict[str, EDLEvent]:
    return {e.event_number: e for e in events}


def compare_edls(base: EDL, updated: EDL) -> ComparisonReport:
    """Compare two EDL objects and return a ComparisonReport."""
    if not isinstance(base, EDL) or not isinstance(updated, EDL):
        raise CompareError("Both arguments must be EDL instances.")

    report = ComparisonReport(
        base_title=base.title or "",
        updated_title=updated.title or "",
    )

    base_index = _event_index(base.events)
    updated_index = _event_index(updated.events)

    base_keys = set(base_index.keys())
    updated_keys = set(updated_index.keys())

    report.events_only_in_base = sorted(base_keys - updated_keys)
    report.events_only_in_updated = sorted(updated_keys - base_keys)

    for key in sorted(base_keys & updated_keys):
        b_event = base_index[key]
        u_event = updated_index[key]
        for f_name in EVENT_FIELDS:
            b_val = getattr(b_event, f_name, None)
            u_val = getattr(u_event, f_name, None)
            if b_val != u_val:
                report.field_diffs.append(
                    FieldDiff(
                        event_number=key,
                        field_name=f_name,
                        base_value=b_val,
                        updated_value=u_val,
                    )
                )

    return report
