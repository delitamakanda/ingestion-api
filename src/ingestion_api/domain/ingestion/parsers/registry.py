from pathlib import Path
from ingestion_api.domain.ingestion.parsers.base import DocumentParser

from ingestion_api.domain.ingestion.parsers.docx import DocxParser
from ingestion_api.domain.ingestion.parsers.html import HtmlParser
from ingestion_api.domain.ingestion.parsers.pdf import PdfParser
from ingestion_api.domain.ingestion.parsers.web import WebParser


class ParserRegistry:

    def __init__(self):
        self.parsers: list[DocumentParser] = [DocxParser(), PdfParser(), HtmlParser()]

    def get(self, file_path: Path) -> DocumentParser:
        for parser in self.parsers:
            if parser.supports(file_path.suffix.lower()):
                return parser
        raise ValueError(f"No suitable parser found for file: {file_path}")