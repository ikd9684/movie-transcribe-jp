from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Form, HTTPException, UploadFile

from app.core.config import settings
from app.core.job_manager import job_manager
from app.core.pipeline import run_pipeline
from app.models.schemas import JobSettings, JobStatus, UploadResponse

router = APIRouter()

ALLOWED_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv", ".webm", ".m4v"}
MAX_BYTES = settings.max_upload_size_mb * 1024 * 1024


@router.post("/upload", response_model=UploadResponse, status_code=202)
async def upload_video(
    file: UploadFile,
    background_tasks: BackgroundTasks,
    settings_json: str = Form("{}", alias="settings"),
) -> UploadResponse:
    # Validate extension
    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {ext}. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    # Validate size (read first chunk to check Content-Length, then stream)
    if file.size and file.size > MAX_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Max allowed: {settings.max_upload_size_mb} MB",
        )

    # Parse settings
    job_settings = JobSettings.model_validate_json(settings_json)

    # Create job
    job_id = job_manager.create_job(job_settings)

    # Persist file
    upload_dir = Path(settings.storage_root) / "uploads" / job_id
    upload_dir.mkdir(parents=True, exist_ok=True)
    dest = upload_dir / f"original{ext}"

    content = await file.read()
    if len(content) > MAX_BYTES:
        raise HTTPException(status_code=413, detail="File too large")

    dest.write_bytes(content)

    background_tasks.add_task(run_pipeline, job_id)

    return UploadResponse(job_id=job_id, status=JobStatus.queued)
