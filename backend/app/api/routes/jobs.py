from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, StreamingResponse

from app.core.config import settings
from app.core.job_manager import job_manager
from app.models.schemas import JobInfo

router = APIRouter()


def _get_job_or_404(job_id: str):
    job = job_manager.get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.get("/jobs/{job_id}/status", response_model=JobInfo)
async def get_job_status(job_id: str) -> JobInfo:
    job = _get_job_or_404(job_id)
    return JobInfo(
        job_id=job.job_id,
        status=job.status,
        step=job.step,
        progress=job.progress,
        error_message=job.error_message,
        created_at=job.created_at,
        updated_at=job.updated_at,
    )


@router.get("/jobs/{job_id}/stream")
async def stream_job(job_id: str) -> StreamingResponse:
    """SSE progress stream — full implementation in Phase 2."""
    _get_job_or_404(job_id)

    async def event_generator():
        job = job_manager.get_job(job_id)
        if job:
            data = (
                f"data: {{\"status\": \"{job.status}\", "
                f"\"progress\": {job.progress}, "
                f"\"step\": \"{job.step}\"}}\n\n"
            )
            yield data

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.get("/jobs/{job_id}/download/srt")
async def download_srt(job_id: str) -> FileResponse:
    _get_job_or_404(job_id)
    srt_path = Path(settings.storage_root) / "outputs" / job_id / "subtitle.srt"
    if not srt_path.exists():
        raise HTTPException(status_code=404, detail="SRT file not yet available")
    return FileResponse(srt_path, media_type="text/plain", filename="subtitle.srt")


@router.get("/jobs/{job_id}/download/video")
async def download_video(job_id: str) -> FileResponse:
    _get_job_or_404(job_id)
    video_path = Path(settings.storage_root) / "outputs" / job_id / "output.mp4"
    if not video_path.exists():
        raise HTTPException(status_code=404, detail="Video not yet available")
    return FileResponse(video_path, media_type="video/mp4", filename="output.mp4")
