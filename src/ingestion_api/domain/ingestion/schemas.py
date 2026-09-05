from typing import Any
from pydantic import BaseModel, Field


class DocumentElement(BaseModel):
    type: str = Field(..., description="The type of the document element.")
    content: str = Field(..., description="The content of the document element.")

    page: int | None = Field(None, description="The page number where the element is located.")
    section: str | None = Field(..., description="The section where the element is located.")
    level: int | None = Field(None, description="The level of the element.")

    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata about the element.")


class ParsedDocument(BaseModel):
    filename: str = Field(..., description="The name of the uploaded file.")
    title: str = Field(..., description="The title of the document.")
    elements: list[DocumentElement] = Field(default_factory=list, description="The list of document elements.")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata about the document.")


class ChunkData(BaseModel):
    text: str = Field(..., description="The text content of the chunk.")
    page_start: int | None = Field(..., description="The page number where the chunk is located.")
    page_end: int | None = Field(..., description="The page number where the chunk ends.")
    section: str = Field(..., description="The section where the chunk is located.")
    chunk_index: int = Field(..., description="The index of the chunk within the section.")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata about the chunk.")