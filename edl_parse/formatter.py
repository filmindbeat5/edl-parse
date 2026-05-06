"""Formatters for EDL output in various human-readable formats."""

from typing import List
from edl_parse.parser import EDL, EDLEvent


def format_timecode_row(event: EDLEvent) -> str:
    """Format a single EDL event as a human-readable timecode row."""
    return (
        f"{event.number:>4}  "
        f"{event.reel:<32} "
        f"{event.track:<6} "
        f"{event.edit_type:<6} "
        f"{event.source_in}  "
        f"{event.source_out}  "
        f"{event.record_in}  "
        f"{event.record_out}"
    )


def format_event_block(event: EDLEvent) -> str:
    """Format a single EDL event as a detailed block string."""
    lines = [
        f"Event    : {event.number}",
        f"Reel     : {event.reel}",
        f"Track    : {event.track}",
        f"Edit Type: {event.edit_type}",
        f"Src In   : {event.source_in}",
        f"Src Out  : {event.source_out}",
        f"Rec In   : {event.record_in}",
        f"Rec Out  : {event.record_out}",
    ]
    if event.clip_name:
        lines.append(f"Clip     : {event.clip_name}")
    if event.comments:
        for comment in event.comments:
            lines.append(f"Comment  : {comment}")
    return "\n".join(lines)


def format_edl_table(edl: EDL) -> str:
    """Format a full EDL as a plain-text table."""
    header_lines = []
    if edl.title:
        header_lines.append(f"TITLE: {edl.title}")
    if edl.fcm:
        header_lines.append(f"FCM: {edl.fcm}")
    header_lines.append("")

    col_header = (
        f"{'NUM':>4}  "
        f"{'REEL':<32} "
        f"{'TRACK':<6} "
        f"{'TYPE':<6} "
        f"{'SRC IN':<12} "
        f"{'SRC OUT':<12} "
        f"{'REC IN':<12} "
        f"{'REC OUT':<12}"
    )
    separator = "-" * len(col_header)

    rows = [col_header, separator]
    for event in edl.events:
        rows.append(format_timecode_row(event))

    return "\n".join(header_lines + rows)


def format_edl_summary(edl: EDL) -> str:
    """Return a brief summary of an EDL."""
    event_count = len(edl.events)
    reels = sorted({e.reel for e in edl.events})
    lines = [
        f"Title     : {edl.title or '(none)'}",
        f"FCM       : {edl.fcm or '(none)'}",
        f"Events    : {event_count}",
        f"Reels ({len(reels)}): {', '.join(reels) if reels else '(none)'}",
    ]
    return "\n".join(lines)
