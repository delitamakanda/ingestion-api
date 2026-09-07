from datetime import date

from pydantic import BaseModel, Field

from ingestion_api.domain.documents.schemas import SourceType
from ingestion_api.llm.agents.query_planner import SYSTEM_PROMPT


class LLMExtractedMetadata(BaseModel):
    countries: list[str] = Field(default_factory=list)

    language: str | None = None

    source_type: SourceType = Field(default=SourceType.OTHER)

    authority: str | None = None

    publication_date: date | None = None

    effective_date: date | None = None

    expiration_date: date | None = None

    topics: list[str] = Field(default_factory=list)

    legal_references: list[str] = Field(default_factory=list)


SYSTEM_PROMPT = """
You extract metadata from documents. 

Return only information that is supported by the document.

Rules:
- countries must be ISO 3166-1 alpha-2 country codes.
- Do not infer a country merely because another country is mentioned in the document.
- language: language of the document
- source_type: type of the document source (e.g. newspaper, website, etc.)
- autority: authority or organization that published the document
- publication_date: date when the document was published
- effective_date: date when the document became effective
- do not confuse publication_date with effective_date.
- expiration_date: date when the document expired
- topics: list of topics covered in the document
- legal_references should preserve their official naming when possible
- Do not invent dates.
"""

class LLMMetadataExtractor:
    def __init__(self, llm):
        self.llm = llm

    async def extract_metadata(self, document) -> LLMExtractedMetadata:
        content = self._build_context(document)

        return await self.llm.structured(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=content,
            schema=LLMExtractedMetadata
        )

    def _build_context(self, document) -> str:
        parts = [
            f"Filename: {document.filename}",
            f"Title: {document.title}",
        ]

        for element in (
            document.elements[:40]
        ):
            parts.append(element.content)

        if len(document.elements) > 40:
            parts.append(
                "\n---- DOCUMENT END ----\n"
            )
            for element in document.elements[-15:]:
                parts.append(element.content)
        return "\n".join(parts)