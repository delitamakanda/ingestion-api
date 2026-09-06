import uuid
from datetime import datetime, date

from pgvector.sqlalchemy import VECTOR
from sqlalchemy import ForeignKey, Text, text
from sqlalchemy import Integer, String, DateTime, Date, func, Computed
from sqlalchemy.dialects.postgresql import JSONB, UUID, TSVECTOR, ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from ingestion_api.core.models import Base


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    title: Mapped[str] = mapped_column(String(1000), nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)

    document_type: Mapped[str] = mapped_column(String(255), nullable=False)

    publication_date: Mapped[date] = mapped_column(Date, nullable=False)

    status: Mapped[str] = mapped_column(String(255), default="upload", nullable=False)

    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    countries: Mapped[list[str]] = mapped_column(
        ARRAY(String(2)),
        nullable=False,
        default=list,
    )

    language: Mapped[str | None] = mapped_column(String(100), nullable=True)

    effective_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    expiration_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    source_type: Mapped[str | None] = mapped_column(String(100), nullable=True)

    source_url: Mapped[str | None] = mapped_column(String(2000), unique=True, nullable=True)

    authority: Mapped[str | None] = mapped_column(String(100), nullable=True)

    legal_references: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=True, default=list)

class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    document_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"),
                                                   index=True)

    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)

    text: Mapped[str] = mapped_column(Text, nullable=False)

    sections: Mapped[str] = mapped_column(String(1000), nullable=False)

    page_start: Mapped[int] = mapped_column(Integer, nullable=True)

    page_end: Mapped[int] = mapped_column(Integer, nullable=True)

    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)

    embedding: Mapped[list[float]] = mapped_column(VECTOR(768), nullable=True)

    search_vector: Mapped[str] = mapped_column(
        TSVECTOR,
        Computed(
            """to_tsvector('simple', coalesce(sections, '') || ' ' || coalesce(text, ''))""", persisted=True, ), )
