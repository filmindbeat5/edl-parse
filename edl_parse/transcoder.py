"""Framerate transcoding utilities for EDL events.

Allows converting timecodes from one framerate to another (e.g. 24fps -> 25fps).
"""

from edl_parse.parser import EDLEvent, EDL


SUPPORTED_FRAMERATES = {23.976, 24, 25, 29.97, 30, 48, 50, 59.94, 60}


class TranscodeError(Exception):
    def __str__(self):
        return f"TranscodeError: {self.args[0]}"


def _timecode_to_frames(tc: str, fps: float) -> int:
    """Convert a timecode string HH:MM:SS:FF to total frame count."""
    tc = tc.replace(";", ":")
    parts = tc.split(":")
    if len(parts) != 4:
        raise TranscodeError(f"Invalid timecode format: {tc!r}")
    try:
        hh, mm, ss, ff = (int(p) for p in parts)
    except ValueError:
        raise TranscodeError(f"Non-integer timecode component in: {tc!r}")
    int_fps = round(fps)
    return ff + ss * int_fps + mm * 60 * int_fps + hh * 3600 * int_fps


def _frames_to_timecode(frames: int, fps: float) -> str:
    """Convert total frame count to a timecode string HH:MM:SS:FF."""
    int_fps = round(fps)
    if int_fps <= 0:
        raise TranscodeError(f"Invalid framerate: {fps}")
    ff = frames % int_fps
    total_seconds = frames // int_fps
    ss = total_seconds % 60
    total_minutes = total_seconds // 60
    mm = total_minutes % 60
    hh = total_minutes // 60
    return f"{hh:02d}:{mm:02d}:{ss:02d}:{ff:02d}"


def transcode_timecode(tc: str, src_fps: float, dst_fps: float) -> str:
    """Convert a single timecode from src_fps to dst_fps."""
    if src_fps not in SUPPORTED_FRAMERATES:
        raise TranscodeError(f"Unsupported source framerate: {src_fps}")
    if dst_fps not in SUPPORTED_FRAMERATES:
        raise TranscodeError(f"Unsupported destination framerate: {dst_fps}")
    frames = _timecode_to_frames(tc, src_fps)
    # Scale frame count proportionally
    scaled = round(frames * dst_fps / src_fps)
    return _frames_to_timecode(scaled, dst_fps)


def transcode_event(event: EDLEvent, src_fps: float, dst_fps: float) -> EDLEvent:
    """Return a new EDLEvent with all timecodes transcoded from src_fps to dst_fps."""
    fields = ["source_in", "source_out", "record_in", "record_out"]
    kwargs = {}
    for field in fields:
        tc = getattr(event, field, None)
        if tc:
            kwargs[field] = transcode_timecode(tc, src_fps, dst_fps)
        else:
            kwargs[field] = tc
    return EDLEvent(
        event_number=event.event_number,
        reel=event.reel,
        track=event.track,
        edit_type=event.edit_type,
        source_in=kwargs["source_in"],
        source_out=kwargs["source_out"],
        record_in=kwargs["record_in"],
        record_out=kwargs["record_out"],
        clip_name=event.clip_name,
        note=event.note,
    )


def transcode_edl(edl: EDL, src_fps: float, dst_fps: float) -> EDL:
    """Return a new EDL with all events transcoded from src_fps to dst_fps."""
    new_edl = EDL(title=edl.title, fcm=edl.fcm)
    new_edl.events = [transcode_event(e, src_fps, dst_fps) for e in edl.events]
    return new_edl
