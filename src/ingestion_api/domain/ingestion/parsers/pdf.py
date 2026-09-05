from pathlib import Path
from uuid import UUID

import pymupdf

from ingestion_api.domain.ingestion.parsers.base import DocumentParser
from ingestion_api.domain.ingestion.schemas import ParsedDocument, DocumentElement

class PdfParser(DocumentParser):
    async def parse(self, file_path: Path) -> ParsedDocument:
        elements: list[DocumentElement] = []

        with pymupdf.open(file_path) as document:
            metadata = document.metadata or {}

            raw_title = (
                metadata.get("Title") or ""
            ).strip()

            if not raw_title or self._looks_like_uuid(raw_title):
                title = file_path.stem
            else:
                title = raw_title

            for page_index, page in enumerate(document):
                page_number = page_index + 1

                blocks = page.get_text(
                    "blocks",
                    sort=True,
                )

                for block in blocks:
                    text = block[4].strip()
                    if not text:
                        continue
                    block_type = block[6]
                    if block_type != 0:
                        continue

                    elements.append(
                        DocumentElement(
                            type="paragraph",
                            section=None,
                            content=text,
                            page=page_number,
                            metadata={"bbox": [
                                block[0], block[1], block[2], block[3]
                            ]}
                        )
                    )
        return ParsedDocument(
            title=title,
            elements=elements,
            filename=file_path.name,
            metadata=metadata
        )

    def supports(self, extension: str) -> bool:
        return extension.lower() == ".pdf"

    def _looks_like_uuid(self, text: str) -> bool:
        try:
            UUID(text)
            return True
        except ValueError:
            return False
