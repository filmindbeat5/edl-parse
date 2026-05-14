"""Normalize EDL events: standardize timecode formatting and reel name casing."""

from edl_parse.parser import EDL, EDLEvent


class NormalizeError(Exception):
    def __str__(self):
        return f"NormalizeError: {self.args[0]}"


def _normalize_timecode(tc: str) -> str:
    """Ensure timecode is zero-padded and uses colons: HH:MM:SS:FF."""
    if not tc or not isinstance(tc, str):
        raise NormalizeError(f"Invalid timecode value: {tc!r}")
    parts = tc.replace(";", ":").replace(".", ":").split(":")
    if len(parts) != 4:
        raise NormalizeError(f"Timecode must have 4 components, got: {tc!r}")
    try:
        normalized = ":".join(f"{int(p):02d}" for p in parts)
    except ValueError:
        raise NormalizeError(f"Non-integer timecode component in: {tc!r}")
    return normalized


def normalize_event(
    event: EDLEvent,
    reel_case: str = "upper",
    normalize_timecodes: bool = True,
) -> EDLEvent:
    """Return a new EDLEvent with normalized reel name and/or timecodes.

    Args:
        event: The source EDLEvent.
        reel_case: One of 'upper', 'lower', or 'preserve'.
        normalize_timecodes: Whether to normalize timecode strings.

    Returns:
        A new EDLEvent instance with normalized fields.
    """
    if reel_case not in ("upper", "lower", "preserve"):
        raise NormalizeError(f"Invalid reel_case: {reel_case!r}. Use 'upper', 'lower', or 'preserve'.")

    reel = event.reel
    if reel_case == "upper":
        reel = reel.upper()
    elif reel_case == "lower":
        reel = reel.lower()

    source_in = event.source_in
    source_out = event.source_out
    record_in = event.record_in
    record_out = event.record_out

    if normalize_timecodes:
        source_in = _normalize_timecode(source_in)
        source_out = _normalize_timecode(source_out)
        record_in = _normalize_timecode(record_in)
        record_out = _normalize_timecode(record_out)

    return EDLEvent(
        event_number=event.event_number,
        reel=reel,
        edit_type=event.edit_type,
        transition=event.transition,
        source_in=source_in,
        source_out=source_out,
        record_in=record_in,
        record_out=record_out,
    )


def normalize_edl(
    edl: EDL,
    reel_case: str = "upper",
    normalize_timecodes: bool = True,
) -> EDL:
    """Return a new EDL with all events normalized."""
    normalized_events = [
        normalize_event(e, reel_case=reel_case, normalize_timecodes=normalize_timecodes)
        for e in edl.events
    ]
    result = EDL()
    result.title = edl.title
    result.fcm = edl.fcm
    result.events = normalized_events
    return result
