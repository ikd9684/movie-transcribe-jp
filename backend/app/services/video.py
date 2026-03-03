from __future__ import annotations

import asyncio
import subprocess
from pathlib import Path

from app.models.schemas import JobSettings


def _run_ffmpeg(cmd: list[str]) -> None:
    """Run FFmpeg command synchronously, raising RuntimeError on failure."""
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg failed (code {result.returncode}):\n{result.stderr}")


async def extract_audio(input_path: Path, output_path: Path) -> None:
    """Extract audio from video as 16kHz mono WAV."""
    cmd = [
        "ffmpeg", "-y",
        "-i", str(input_path),
        "-vn",
        "-acodec", "pcm_s16le",
        "-ar", "16000",
        "-ac", "1",
        str(output_path),
    ]
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, _run_ffmpeg, cmd)


async def burn_subtitles(
    input_path: Path,
    srt_path: Path,
    output_path: Path,
    job_settings: JobSettings,
) -> None:
    """Burn SRT subtitles into video using FFmpeg libass."""
    alignment = 2 if job_settings.subtitle_position == "bottom" else 6
    force_style = (
        f"FontSize={job_settings.subtitle_font_size},"
        f"Alignment={alignment}"
    )
    # Escape path for libass filter (colons and backslashes must be escaped)
    srt_escaped = str(srt_path).replace("\\", "/").replace(":", "\\:")

    cmd = [
        "ffmpeg", "-y",
        "-i", str(input_path),
        "-vf", f"subtitles={srt_escaped}:force_style='{force_style}'",
        "-crf", str(job_settings.output_crf),
        "-preset", "fast",
        str(output_path),
    ]
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, _run_ffmpeg, cmd)
