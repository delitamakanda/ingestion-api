from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from ingestion_api.domain.jobs.enums import JobStatus

class JobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    document_id: UUID | None
    original_filename: str
    status: JobStatus | str
    current_step: str | None
    progress: int
    attempts: int
    error_code: str | None
    error_message: str | None
    created_at: datetime
    started_at: datetime | None
    finished_at: datetime | None