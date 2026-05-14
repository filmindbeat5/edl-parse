"""Export EDL data to various formats (CSV, TSV)."""

import csv
import io
from typing import List, Optional

from edl_parse.parser import EDL, EDLEvent


class ExportError(Exception):
    def __str__(self):
        return f"ExportError: {self.args[0]}"


EVENT_FIELDS = [
    "event_number",
    "reel",
    "track",
    "edit_type",
    "source_in",
    "source_out",
    "record_in",
    "record_out",
]


def events_to_csv(
    events: List[EDLEvent],
    delimiter: str = ",",
    include_header: bool = True,
) -> str:
    """Serialize a list of EDLEvents to a CSV/TSV string."""
    if not events:
        raise ExportError("Cannot export an empty event list")
    if delimiter not in (",", "\t", "|", ";"):
        raise ExportError(f"Unsupported delimiter: {repr(delimiter)}")

    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=EVENT_FIELDS,
        delimiter=delimiter,
        extrasaction="ignore",
        lineterminator="\n",
    )
    if include_header:
        writer.writeheader()
    for event in events:
        writer.writerow(
            {
                "event_number": event.event_number,
                "reel": event.reel,
                "track": event.track,
                "edit_type": event.edit_type,
                "source_in": event.source_in,
                "source_out": event.source_out,
                "record_in": event.record_in,
                "record_out": event.record_out,
            }
        )
    return output.getvalue()


def edl_to_csv(edl: EDL, delimiter: str = ",", include_header: bool = True) -> str:
    """Serialize all events in an EDL to a CSV/TSV string."""
    return events_to_csv(edl.events, delimiter=delimiter, include_header=include_header)


def edl_to_tsv(edl: EDL, include_header: bool = True) -> str:
    """Convenience wrapper: serialize EDL events to TSV."""
    return edl_to_csv(edl, delimiter="\t", include_header=include_header)
