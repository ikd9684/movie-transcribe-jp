from __future__ import annotations

import asyncio
import json
from pathlib import Path

import httpx
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse, StreamingResponse

from app.core.config import settings
from app.core.job_manager import job_manager
from app.models.schemas import JobInfo, JobStatus

router = APIRouter()


@router.get("/ollama/models")
async def list_ollama_models(base_url: str = Query(..., description="Ollama base URL")) -> dict:
    """Proxy to Ollama /api/tags to avoid browser CORS restrictions."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            res = await client.get(f"{base_url}/api/tags")
            res.raise_for_status()
            return res.json()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Ollama に接続できませんでした: {e}")


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
    """SSE progress stream."""
    _get_job_or_404(job_id)

    async def event_generator():
        while True:
            job = job_manager.get_job(job_id)
            if job is None:
                break
            data = json.dumps(
                {
                    "status": job.status,
                    "step": job.step,
                    "progress": job.progress,
                    "error_message": job.error_message,
                }
            )
            yield f"data: {data}\n\n"
            if job.status in (JobStatus.done, JobStatus.error):
                break
            await asyncio.sleep(0.5)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/jobs/{job_id}/download/srt")
async def download_srt(job_id: str) -> FileResponse:
    job = _get_job_or_404(job_id)
    if job.status != JobStatus.done:
        raise HTTPException(status_code=409, detail="Job is not yet complete")
    srt_path = Path(settings.storage_root) / "outputs" / job_id / "subtitle.srt"
    if not srt_path.exists():
        raise HTTPException(status_code=404, detail="SRT file not found")
    return FileResponse(srt_path, media_type="text/plain", filename="subtitle.srt")


@router.get("/jobs/{job_id}/download/video")
async def download_video(job_id: str) -> FileResponse:
    job = _get_job_or_404(job_id)
    if job.status != JobStatus.done:
        raise HTTPException(status_code=409, detail="Job is not yet complete")
    video_path = Path(settings.storage_root) / "outputs" / job_id / "output.mp4"
    if not video_path.exists():
        raise HTTPException(status_code=404, detail="Video file not found")
    return FileResponse(video_path, media_type="video/mp4", filename="output.mp4")
