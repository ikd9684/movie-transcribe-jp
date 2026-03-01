from __future__ import annotations

import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime

from app.models.schemas import JobSettings, JobStatus


@dataclass
class Job:
    job_id: str
    status: JobStatus
    settings: JobSettings
    step: str = ""
    progress: int = 0
    error_message: str | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


class JobManager:
    def __init__(self) -> None:
        self._jobs: dict[str, Job] = {}
        self._lock = threading.Lock()

    def create_job(self, settings: JobSettings) -> str:
        job_id = str(uuid.uuid4())
        job = Job(job_id=job_id, status=JobStatus.queued, settings=settings)
        with self._lock:
            self._jobs[job_id] = job
        return job_id

    def get_job(self, job_id: str) -> Job | None:
        with self._lock:
            return self._jobs.get(job_id)

    def update_job(
        self,
        job_id: str,
        *,
        status: JobStatus | None = None,
        step: str | None = None,
        progress: int | None = None,
        error_message: str | None = None,
    ) -> None:
        with self._lock:
            job = self._jobs.get(job_id)
            if job is None:
                return
            if status is not None:
                job.status = status
            if step is not None:
                job.step = step
            if progress is not None:
                job.progress = progress
            if error_message is not None:
                job.error_message = error_message
            job.updated_at = datetime.utcnow()


job_manager = JobManager()
