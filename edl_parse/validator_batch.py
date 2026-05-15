"""Batch validation of EDL events with summary reporting."""

from dataclasses import dataclass, field
from typing import List, Optional
from edl_parse.parser import EDL, EDLEvent
from edl_parse.validator import validate_event, ValidationResult


class BatchValidationError(Exception):
    def __str__(self):
        return self.args[0] if self.args else "Batch validation error"


@dataclass
class EventValidationReport:
    event_number: str
    result: ValidationResult

    @property
    def is_valid(self) -> bool:
        return self.result.is_valid

    @property
    def errors(self) -> List[str]:
        return [str(e) for e in self.result.errors]


@dataclass
class BatchValidationReport:
    reports: List[EventValidationReport] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.reports)

    @property
    def valid_count(self) -> int:
        return sum(1 for r in self.reports if r.is_valid)

    @property
    def invalid_count(self) -> int:
        return self.total - self.valid_count

    @property
    def is_fully_valid(self) -> bool:
        return self.invalid_count == 0

    def invalid_reports(self) -> List[EventValidationReport]:
        return [r for r in self.reports if not r.is_valid]

    def summary(self) -> str:
        lines = [
            f"Batch Validation Summary",
            f"  Total events : {self.total}",
            f"  Valid        : {self.valid_count}",
            f"  Invalid      : {self.invalid_count}",
        ]
        if self.invalid_count:
            lines.append("  Issues:")
            for r in self.invalid_reports():
                for err in r.errors:
                    lines.append(f"    Event {r.event_number}: {err}")
        return "\n".join(lines)


def validate_events_batch(events: List[EDLEvent]) -> BatchValidationReport:
    """Validate a list of EDLEvent objects and return a BatchValidationReport."""
    if not isinstance(events, list):
        raise BatchValidationError("events must be a list")
    reports = []
    for event in events:
        result = validate_event(event)
        reports.append(EventValidationReport(event_number=event.event_number, result=result))
    return BatchValidationReport(reports=reports)


def validate_edl_batch(edl: EDL) -> BatchValidationReport:
    """Validate all events in an EDL and return a BatchValidationReport."""
    if not isinstance(edl, EDL):
        raise BatchValidationError("edl must be an EDL instance")
    return validate_events_batch(edl.events)
