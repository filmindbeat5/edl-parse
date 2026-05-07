"""Trim EDL events to a specified record timecode range."""

from typing import Optional
from edl_parse.parser import EDL, EDLEvent
from edl_parse.sorter import _timecode_to_frames


class TrimError(Exception):
    """Raised when trimming parameters are invalid."""
    pass


def _event_in_range(
    event: EDLEvent,
    start_frames: Optional[int],
    end_frames: Optional[int],
) -> bool:
    """Return True if event's record range overlaps with [start_frames, end_frames]."""
    rec_in = _timecode_to_frames(event.rec_in)
    rec_out = _timecode_to_frames(event.rec_out)

    if start_frames is not None and rec_out <= start_frames:
        return False
    if end_frames is not None and rec_in >= end_frames:
        return False
    return True


def trim_events(
    events: list,
    start_tc: Optional[str] = None,
    end_tc: Optional[str] = None,
    fps: int = 25,
) -> list:
    """Filter events to those whose record timecodes fall within the given range.

    Args:
        events: List of EDLEvent objects.
        start_tc: Inclusive start timecode string (e.g. '01:00:00:00').
        end_tc: Exclusive end timecode string (e.g. '01:30:00:00').
        fps: Frames per second used for timecode conversion.

    Returns:
        Filtered list of EDLEvent objects.
    """
    if start_tc is None and end_tc is None:
        raise TrimError("At least one of start_tc or end_tc must be provided.")

    start_frames = _timecode_to_frames(start_tc, fps) if start_tc else None
    end_frames = _timecode_to_frames(end_tc, fps) if end_tc else None

    if start_frames is not None and end_frames is not None:
        if end_frames <= start_frames:
            raise TrimError(
                f"end_tc '{end_tc}' must be after start_tc '{start_tc}'."
            )

    return [e for e in events if _event_in_range(e, start_frames, end_frames)]


def trim_edl(
    edl: EDL,
    start_tc: Optional[str] = None,
    end_tc: Optional[str] = None,
    fps: int = 25,
) -> EDL:
    """Return a new EDL containing only events within the specified record range.

    Args:
        edl: Source EDL object.
        start_tc: Inclusive start record timecode.
        end_tc: Exclusive end record timecode.
        fps: Frames per second.

    Returns:
        New EDL with filtered events.
    """
    trimmed_events = trim_events(edl.events, start_tc=start_tc, end_tc=end_tc, fps=fps)
    result = EDL(title=edl.title, fcm=edl.fcm)
    result.events = trimmed_events
    return result
