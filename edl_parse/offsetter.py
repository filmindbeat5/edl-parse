"""Timecode offsetting for EDL events."""

from edl_parse.parser import EDL, EDLEvent


class OffsetError(Exception):
    """Raised when an offset operation fails."""

    def __str__(self):
        return f"OffsetError: {self.args[0]}"


def _timecode_to_frames(tc: str, fps: int = 25) -> int:
    """Convert a timecode string HH:MM:SS:FF to total frames."""
    parts = tc.strip().split(":")
    if len(parts) != 4:
        raise OffsetError(f"Invalid timecode format: {tc!r}")
    hh, mm, ss, ff = (int(p) for p in parts)
    return ((hh * 3600) + (mm * 60) + ss) * fps + ff


def _frames_to_timecode(frames: int, fps: int = 25) -> str:
    """Convert total frames to a timecode string HH:MM:SS:FF."""
    if frames < 0:
        raise OffsetError(f"Negative timecode result: {frames} frames")
    ff = frames % fps
    total_seconds = frames // fps
    ss = total_seconds % 60
    mm = (total_seconds // 60) % 60
    hh = total_seconds // 3600
    return f"{hh:02}:{mm:02}:{ss:02}:{ff:02}"


def offset_event_record(event: EDLEvent, offset_frames: int, fps: int = 25) -> EDLEvent:
    """Return a new EDLEvent with record in/out timecodes shifted by offset_frames."""
    rec_in_frames = _timecode_to_frames(event.rec_in, fps) + offset_frames
    rec_out_frames = _timecode_to_frames(event.rec_out, fps) + offset_frames

    new_event = EDLEvent(
        event_number=event.event_number,
        reel=event.reel,
        track=event.track,
        edit_type=event.edit_type,
        src_in=event.src_in,
        src_out=event.src_out,
        rec_in=_frames_to_timecode(rec_in_frames, fps),
        rec_out=_frames_to_timecode(rec_out_frames, fps),
    )
    return new_event


def offset_edl_record(edl: EDL, offset_frames: int, fps: int = 25) -> EDL:
    """Return a new EDL with all record timecodes shifted by offset_frames."""
    new_edl = EDL(title=edl.title, fcm=edl.fcm)
    for event in edl.events:
        new_edl.events.append(offset_event_record(event, offset_frames, fps))
    return new_edl
