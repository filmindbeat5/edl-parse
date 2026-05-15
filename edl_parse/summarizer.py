"""Summarizer: generate human-readable text summaries of EDL objects."""

from edl_parse.parser import EDL, EDLEvent


class SummaryError(Exception):
    def __str__(self):
        return f"SummaryError: {self.args[0]}"


def summarize_event(event: EDLEvent) -> str:
    """Return a single-line summary string for one EDL event."""
    if not event.event_number:
        raise SummaryError("Event is missing an event number.")
    parts = [
        f"Event {event.event_number}",
        f"Reel: {event.reel}",
        f"Type: {event.edit_type}",
        f"Src: {event.source_in}-{event.source_out}",
        f"Rec: {event.record_in}-{event.record_out}",
    ]
    if getattr(event, "note", None):
        parts.append(f"Note: {event.note}")
    return " | ".join(parts)


def summarize_edl(edl: EDL) -> str:
    """Return a multi-line summary string for an entire EDL."""
    if not edl.events:
        raise SummaryError("EDL contains no events to summarize.")

    lines = []
    title = getattr(edl, "title", None) or "Untitled"
    fcm = getattr(edl, "fcm", None) or "Unknown"
    lines.append(f"Title : {title}")
    lines.append(f"FCM   : {fcm}")
    lines.append(f"Events: {len(edl.events)}")

    reels = sorted({e.reel for e in edl.events if e.reel})
    lines.append(f"Reels : {', '.join(reels) if reels else 'none'}")

    edit_types = sorted({e.edit_type for e in edl.events if e.edit_type})
    lines.append(f"Types : {', '.join(edit_types) if edit_types else 'none'}")

    lines.append("")
    for event in edl.events:
        lines.append(summarize_event(event))

    return "\n".join(lines)


def summarize_edl_brief(edl: EDL) -> str:
    """Return a short one-paragraph summary without per-event detail."""
    if not edl.events:
        raise SummaryError("EDL contains no events to summarize.")

    title = getattr(edl, "title", None) or "Untitled"
    fcm = getattr(edl, "fcm", None) or "Unknown"
    count = len(edl.events)
    reels = sorted({e.reel for e in edl.events if e.reel})
    reel_str = ", ".join(reels) if reels else "none"
    return (
        f"'{title}' [{fcm}]: {count} event(s) across reel(s): {reel_str}."
    )
