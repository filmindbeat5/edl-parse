"""Import EDL events from CSV or TSV files."""

import csv
import io
from typing import List

from edl_parse.parser import EDL, EDLEvent


class ImportError(Exception):
    """Raised when an import operation fails."""

    def __str__(self) -> str:
        return f"ImportError: {self.args[0]}"


REQUIRED_FIELDS = {"event_number", "reel", "edit_type", "source_in", "source_out", "record_in", "record_out"}


def _row_to_event(row: dict) -> EDLEvent:
    """Convert a CSV/TSV row dict to an EDLEvent."""
    missing = REQUIRED_FIELDS - set(row.keys())
    if missing:
        raise ImportError(f"Row is missing required fields: {sorted(missing)}")

    event = EDLEvent()
    event.event_number = row["event_number"].strip()
    event.reel = row["reel"].strip()
    event.edit_type = row["edit_type"].strip()
    event.source_in = row["source_in"].strip()
    event.source_out = row["source_out"].strip()
    event.record_in = row["record_in"].strip()
    event.record_out = row["record_out"].strip()
    if "note" in row and row["note"].strip():
        event.note = row["note"].strip()
    return event


def csv_to_events(text: str, delimiter: str = ",") -> List[EDLEvent]:
    """Parse a CSV or TSV string and return a list of EDLEvent objects."""
    reader = csv.DictReader(io.StringIO(text), delimiter=delimiter)
    events: List[EDLEvent] = []
    for i, row in enumerate(reader, start=1):
        try:
            events.append(_row_to_event(row))
        except ImportError as exc:
            raise ImportError(f"Row {i}: {exc.args[0]}") from exc
    if not events:
        raise ImportError("No events found in input data.")
    return events


def csv_to_edl(text: str, title: str = "IMPORTED", fcm: str = "NON-DROP FRAME", delimiter: str = ",") -> EDL:
    """Parse a CSV string and return a populated EDL object."""
    edl = EDL()
    edl.title = title
    edl.fcm = fcm
    edl.events = csv_to_events(text, delimiter=delimiter)
    return edl


def tsv_to_edl(text: str, title: str = "IMPORTED", fcm: str = "NON-DROP FRAME") -> EDL:
    """Parse a TSV string and return a populated EDL object."""
    return csv_to_edl(text, title=title, fcm=fcm, delimiter="\t")
