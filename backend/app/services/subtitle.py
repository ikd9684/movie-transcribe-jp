from __future__ import annotations

from pathlib import Path

from app.models.schemas import Segment


def _format_timestamp(seconds: float) -> str:
    """Convert float seconds to SRT timestamp format: HH:MM:SS,mmm"""
    total_ms = int(seconds * 1000)
    ms = total_ms % 1000
    total_s = total_ms // 1000
    s = total_s % 60
    total_m = total_s // 60
    m = total_m % 60
    h = total_m // 60
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def generate_srt(segments: list[Segment], output_path: Path) -> None:
    """Generate SRT file from segments. Skips segments with empty ja_text."""
    lines: list[str] = []
    index = 1
    for seg in segments:
        if not seg.ja_text.strip():
            continue
        lines.append(str(index))
        lines.append(f"{_format_timestamp(seg.start)} --> {_format_timestamp(seg.end)}")
        lines.append(seg.ja_text.strip())
        lines.append("")
        index += 1

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")
