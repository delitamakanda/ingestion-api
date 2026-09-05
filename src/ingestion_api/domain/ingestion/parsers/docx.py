from pathlib import Path
from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph

from ingestion_api.domain.ingestion.parsers.base import DocumentParser

from ingestion_api.domain.ingestion.schemas import ParsedDocument, DocumentElement

class DocxParser(DocumentParser):

    async def parse(self, file_path: Path) -> ParsedDocument:
        document = Document(file_path)
        elements: list[DocumentElement] = []

        current_section: str | None = None

        title = document.core_properties.title or file_path.stem

        for element in document.iter_inner_content():
            if isinstance(element, Paragraph):
                text = element.text.strip()

                if not text:
                    continue

                style_name = (
                    element.style.name if element.style else ""
                )
                if style_name.startswith("Title "):
                    element_type = "title"
                    level = 0
                elif style_name.startswith("Heading "):
                    element_type = "heading"
                    level = self._heading_level(
                        style_name
                    )
                    current_section = text
                else:
                    element_type = "paragraph"
                    level = 0

                elements.append(
                    DocumentElement(
                        type=element_type,
                        content=text,
                        section=current_section,
                        level=level)
                )
            elif isinstance(element, Table):
                table_content, rows = self._table_to_data(element)

                if not table_content:
                    continue

                elements.append(DocumentElement(type="table", content=table_content, section=current_section, metadata={"rows": rows}))

        return ParsedDocument(elements=elements, filename=file_path.name, title=title, metadata={})

    @staticmethod
    def _heading_level(style_name: str) -> int:
        return int(style_name.split()[-1])

    @staticmethod
    def _table_to_text(table: Table) -> str:
        rows = []
        for row in table.rows:
            cells = [cell.text.strip() for cell in row.cells]
            if any(cells):
                rows.append(" | ".join(cells))
        return "\n".join(rows)


    @staticmethod
    def _table_to_data(table: Table) -> tuple[str, list[list[str]]]:
        rows = []
        for row in table.rows:
            cells = [cell.text.strip() for cell in row.cells]
            if any(cells):
                rows.append(cells)

        text = "\n".join(" | ".join(row) for row in rows)
        return text, rows

    def supports(self, extension: str) -> bool:
        return extension.lower() == ".docx"
