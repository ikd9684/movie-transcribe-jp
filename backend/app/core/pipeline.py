from __future__ import annotations

from pathlib import Path

import httpx

from app.core.config import settings
from app.core.job_manager import job_manager
from app.models.schemas import JobStatus
from app.services import subtitle, transcription, translation, video


async def run_pipeline(job_id: str) -> None:
    """Execute the full transcription/translation/subtitle pipeline for a job."""
    job = job_manager.get_job(job_id)
    if job is None:
        return

    upload_dir = Path(settings.storage_root) / "uploads" / job_id
    output_dir = Path(settings.storage_root) / "outputs" / job_id
    output_dir.mkdir(parents=True, exist_ok=True)

    # Locate the uploaded file (original.*)
    candidates = list(upload_dir.glob("original.*"))
    if not candidates:
        job_manager.update_job(
            job_id,
            status=JobStatus.error,
            error_message="アップロードファイルが見つかりません",
        )
        return
    input_path = candidates[0]
    audio_path = upload_dir / "audio.wav"
    srt_path = output_dir / "subtitle.srt"
    output_video_path = output_dir / "output.mp4"

    job_settings = job.settings

    try:
        # Step 1: 音声抽出 (0% → 20%)
        job_manager.update_job(
            job_id,
            status=JobStatus.processing,
            step="音声抽出中",
            progress=0,
        )
        await video.extract_audio(input_path, audio_path)
        job_manager.update_job(job_id, progress=20)

        # Step 2: 文字起こし (20% → 50%)
        job_manager.update_job(job_id, step="文字起こし中", progress=20)
        segments = await transcription.transcribe(
            audio_path,
            job_settings.whisper_model,
            job_settings.whisper_language,
        )
        job_manager.update_job(job_id, progress=50)

        # Step 3: 翻訳 (50% → 75%)
        job_manager.update_job(job_id, step="日本語翻訳中", progress=50)
        segments = await translation.translate_segments(segments, job_settings)
        job_manager.update_job(job_id, progress=75)

        # Step 4: SRT 生成 (75% → 85%)
        job_manager.update_job(job_id, step="字幕ファイル生成中", progress=75)
        subtitle.generate_srt(segments, srt_path)
        job_manager.update_job(job_id, progress=85)

        # Step 5: 字幕焼き込み (85% → 100%)
        job_manager.update_job(job_id, step="字幕焼き込み中", progress=85)
        await video.burn_subtitles(input_path, srt_path, output_video_path, job_settings)

        job_manager.update_job(
            job_id,
            status=JobStatus.done,
            step="完了",
            progress=100,
        )

    except RuntimeError as exc:
        job_manager.update_job(
            job_id,
            status=JobStatus.error,
            error_message=f"処理エラー: {exc}",
        )
    except httpx.ConnectError as exc:
        job_manager.update_job(
            job_id,
            status=JobStatus.error,
            error_message=f"Ollama への接続に失敗しました: {exc}",
        )
    except httpx.HTTPStatusError as exc:
        job_manager.update_job(
            job_id,
            status=JobStatus.error,
            error_message=f"翻訳 API エラー (HTTP {exc.response.status_code}): {exc.response.text[:200]}",
        )
    except Exception as exc:  # noqa: BLE001
        job_manager.update_job(
            job_id,
            status=JobStatus.error,
            error_message=f"予期しないエラーが発生しました: {exc}",
        )
