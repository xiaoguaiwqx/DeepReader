from datetime import datetime, timezone
import threading
from typing import Dict, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class JobStatus(BaseModel):
    job_id: str
    status: str = Field(..., description="pending|running|completed|failed")
    total: Optional[int] = None
    processed: int = 0
    new: int = 0
    error: Optional[str] = None
    started_at: datetime
    finished_at: Optional[datetime] = None


_job_lock = threading.Lock()
_jobs: Dict[str, JobStatus] = {}


def create_job() -> JobStatus:
    job_id = uuid4().hex
    job = JobStatus(
        job_id=job_id,
        status="pending",
        started_at=datetime.now(timezone.utc),
    )
    with _job_lock:
        _jobs[job_id] = job
    return job


def get_job(job_id: str) -> Optional[JobStatus]:
    with _job_lock:
        return _jobs.get(job_id)


def update_job(job_id: str, **updates) -> Optional[JobStatus]:
    with _job_lock:
        job = _jobs.get(job_id)
        if not job:
            return None
        job = job.model_copy(update=updates)
        _jobs[job_id] = job
        return job
