from datetime import datetime, UTC
import uuid
from enum import StrEnum

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import (
DateTime,
ForeignKey,
Integer,
String,
Text
)
from sqlalchemy.dialects.postgresql import UUID
from ingestion_api.core.models import Base

class JobType(StrEnum):
    INGESTION = "ingestion"
    REINDEX = "reindex"


class IngestionJob(Base):
    __tablename__ = "ingestion_jobs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    job_type: Mapped[JobType] = mapped_column(String(50), nullable=True, default=JobType.INGESTION, index=True)

    document_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="SET NULL"), nullable=True, index=True)

    original_filename: Mapped[str] = mapped_column(String(500), nullable=False)

    stored_filename: Mapped[str] = mapped_column(String(500), nullable=False)

    content_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)

    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending", index=True)

    current_step: Mapped[str | None] = mapped_column(String(100), nullable=True)

    progress: Mapped[int] = mapped_column(Integer, default=0)

    attempts: Mapped[int] = mapped_column(Integer, default=0)

    error_code: Mapped[str | None] = mapped_column(String(100), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now(UTC))

    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True, onupdate=datetime.now(UTC), default=datetime.now(UTC))

