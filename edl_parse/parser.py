"""Core EDL parser module for reading and tokenizing EDL files."""

import re
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class EDLEvent:
    """Represents a single edit event in an EDL file."""
    event_number: str
    reel: str
    track: str
    edit_type: str
    transition: Optional[str]
    source_in: str
    source_out: str
    record_in: str
    record_out: str
    clip_name: Optional[str] = None
    comments: List[str] = field(default_factory=list)


@dataclass
class EDL:
    """Represents a parsed EDL file."""
    title: Optional[str]
    fcm: Optional[str]
    events: List[EDLEvent] = field(default_factory=list)


# Matches standard CMX 3600 event lines
EVENT_PATTERN = re.compile(
    r'^(\d+)\s+(\S+)\s+(\S+)\s+(\S+)(?:\s+(\S+))?\s+'
    r'(\d{2}:\d{2}:\d{2}[:\;]\d{2})\s+'
    r'(\d{2}:\d{2}:\d{2}[:\;]\d{2})\s+'
    r'(\d{2}:\d{2}:\d{2}[:\;]\d{2})\s+'
    r'(\d{2}:\d{2}:\d{2}[:\;]\d{2})'
)
CLIP_NAME_PATTERN = re.compile(r'^\*\s*FROM CLIP NAME:\s*(.+)$', re.IGNORECASE)
TITLE_PATTERN = re.compile(r'^TITLE:\s*(.+)$', re.IGNORECASE)
FCM_PATTERN = re.compile(r'^FCM:\s*(.+)$', re.IGNORECASE)


def parse_edl(content: str) -> EDL:
    """Parse EDL file content string into an EDL dataclass."""
    title = None
    fcm = None
    events: List[EDLEvent] = []
    current_event: Optional[EDLEvent] = None

    for line in content.splitlines():
        line = line.strip()
        if not line:
            continue

        title_match = TITLE_PATTERN.match(line)
        if title_match:
            title = title_match.group(1).strip()
            continue

        fcm_match = FCM_PATTERN.match(line)
        if fcm_match:
            fcm = fcm_match.group(1).strip()
            continue

        event_match = EVENT_PATTERN.match(line)
        if event_match:
            groups = event_match.groups()
            current_event = EDLEvent(
                event_number=groups[0],
                reel=groups[1],
                track=groups[2],
                edit_type=groups[3],
                transition=groups[4],
                source_in=groups[5],
                source_out=groups[6],
                record_in=groups[7],
                record_out=groups[8],
            )
            events.append(current_event)
            continue

        if current_event:
            clip_match = CLIP_NAME_PATTERN.match(line)
            if clip_match:
                current_event.clip_name = clip_match.group(1).strip()
            elif line.startswith('*') or line.startswith(';'):
                current_event.comments.append(line)

    return EDL(title=title, fcm=fcm, events=events)
