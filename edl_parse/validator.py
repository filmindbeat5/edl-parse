"""Validation utilities for EDL data structures."""

from dataclasses import dataclass
from typing import List, Optional
from .parser import EDL, EDLEvent


@dataclass
class ValidationError:
    field: str
    message: str
    event_index: Optional[int] = None

    def __str__(self) -> str:
        if self.event_index is not None:
            return f"Event {self.event_index} - {self.field}: {self.message}"
        return f"{self.field}: {self.message}"


@dataclass
class ValidationResult:
    valid: bool
    errors: List[ValidationError]

    def __str__(self) -> str:
        if self.valid:
            return "EDL is valid."
        error_lines = "\n".join(str(e) for e in self.errors)
        return f"EDL validation failed with {len(self.errors)} error(s):\n{error_lines}"


TIMECODE_PATTERN = r"^\d{2}:\d{2}:\d{2}[:\;]\d{2}$"


def validate_timecode(tc: str) -> bool:
    import re
    return bool(re.match(TIMECODE_PATTERN, tc))


def validate_event(event: EDLEvent, index: int) -> List[ValidationError]:
    errors = []

    if not str(event.event_number).strip():
        errors.append(ValidationError("event_number", "Event number is missing.", index))

    if not event.reel.strip():
        errors.append(ValidationError("reel", "Reel name is empty.", index))

    if not event.track.strip():
        errors.append(ValidationError("track", "Track is empty.", index))

    for tc_field in ("source_in", "source_out", "record_in", "record_out"):
        tc_value = getattr(event, tc_field, "")
        if not validate_timecode(tc_value):
            errors.append(ValidationError(
                tc_field,
                f"Invalid timecode format: '{tc_value}'",
                index
            ))

    return errors


def validate_edl(edl: EDL) -> ValidationResult:
    errors = []

    if not edl.title or not edl.title.strip():
        errors.append(ValidationError("title", "EDL title is missing or empty."))

    if not edl.events:
        errors.append(ValidationError("events", "EDL contains no events."))
    else:
        for i, event in enumerate(edl.events):
            errors.extend(validate_event(event, i + 1))

    return ValidationResult(valid=len(errors) == 0, errors=errors)
