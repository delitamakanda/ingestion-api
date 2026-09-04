import uuid
from datetime import datetime, date

from sqlalchemy import Column, Integer, String, DateTime, Date, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy import ForeignKey, Text
from pgvector.sqlalchemy import VECTOR


from ingestion_api.core.models import Base

class Document(Base):
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    title: Mapped[str] = mapped_column(String(1000), nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64),unique=True, index=True)

    document_type: Mapped[str] = mapped_column(String(255), nullable=False)

    publication_date: Mapped[date] = mapped_column(Date, nullable=False)

    status: Mapped[str] = mapped_column(String(255), default="upload", nullable=False)

    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    document_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), index=True)

    text: Mapped[str] = mapped_column(Text, nullable=False)


    sections: Mapped[str] = mapped_column(String(1000), nullable=False)

    page_start: Mapped[int]

    page_end: Mapped[int]

    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)

    embedding: Mapped[list[float]] = mapped_column(VECTOR(1024))