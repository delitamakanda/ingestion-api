from datetime import date

from enum import StrEnum

from pydantic import BaseModel, Field

from ingestion_api.domain.documents.schemas import SourceType

class MetadataConfidence(BaseModel):
    countries: float = 0
    publication_date: float = 0
    effective_date: float = 0
    expiration_date: float = 0
    source_type: float = 0
    authority: float = 0
    language: float = 0
    legal_references: float = 0

class ExtractedMetadata(BaseModel):
    countries: list[str] = Field(default_factory=list)
    publication_date: date | None = None
    effective_date: date | None = None
    expiration_date: date | None = None
    source_type: SourceType = Field(default=SourceType.OTHER)
    authority: str | None = None
    language: str | None = None
    legal_references: list[str] = Field(default_factory=list)
    topics: list[str] = Field(default_factory=list)
    source_urls: list[str] = Field(default_factory=list)
    confidence: MetadataConfidence = Field(default_factory=MetadataConfidence)