from __future__ import annotations

import asyncio
import threading
from collections.abc import Callable
from pathlib import Path

from faster_whisper import WhisperModel

from app.models.schemas import Segment

_model_cache: dict[str, WhisperModel] = {}
_cache_lock = threading.Lock()


def _get_model(model_name: str) -> WhisperModel:
    """Load and cache WhisperModel by name (thread-safe)."""
    with _cache_lock:
        if model_name not in _model_cache:
            _model_cache[model_name] = WhisperModel(model_name, device="auto")
        return _model_cache[model_name]


def _transcribe_sync(
    audio_path: Path,
    model_name: str,
    language: str | None,
    on_progress: Callable[[float], None] | None = None,
) -> list[Segment]:
    """Synchronous transcription. Runs in executor to avoid blocking the event loop."""
    model = _get_model(model_name)
    segments_iter, info = model.transcribe(
        str(audio_path),
        language=language,
        vad_filter=True,
    )
    results = []
    duration = info.duration or 0
    for seg in segments_iter:
        results.append(Segment(start=seg.start, end=seg.end, text=seg.text.strip()))
        if on_progress and duration > 0:
            on_progress(min(seg.end / duration, 1.0))
    return results


async def transcribe(
    audio_path: Path,
    model_name: str,
    language: str,
    on_progress: Callable[[float], None] | None = None,
) -> list[Segment]:
    """Transcribe audio file and return list of Segments."""
    lang = None if language == "auto" else language
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _transcribe_sync, audio_path, model_name, lang, on_progress)
