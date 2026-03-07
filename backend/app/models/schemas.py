from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class JobStatus(str, Enum):
    queued = "queued"
    processing = "processing"
    done = "done"
    error = "error"


class JobSettings(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    whisper_model: str = "large-v3"
    whisper_language: str = "auto"
    ollama_base_url: str = "http://localhost:11434"
    translation_model: str = "gpt-oss:20b"
    translation_parallel: int = Field(4, ge=1, le=8)
    translation_context_window: int = Field(2, ge=0, le=4)
    subtitle_font_size: int = Field(24, ge=12, le=48)
    subtitle_position: str = "bottom"  # "bottom" | "top"
    output_crf: int = Field(23, ge=18, le=28)


class Segment(BaseModel):
    start: float
    end: float
    text: str
    ja_text: str = ""


class JobInfo(BaseModel):
    job_id: str
    status: JobStatus
    step: str = ""
    progress: int = 0
    error_message: str | None = None
    created_at: datetime
    updated_at: datetime


class UploadResponse(BaseModel):
    job_id: str
    status: JobStatus
    message: str = "Job created"
