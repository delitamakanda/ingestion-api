from pathlib import Path
from bs4 import BeautifulSoup

from ingestion_api.domain.ingestion.parsers.base import DocumentParser
from ingestion_api.domain.ingestion.schemas import ParsedDocument, DocumentElement


class HtmlParser(DocumentParser):
    async def parse(self, file_path: Path) -> ParsedDocument:
        html = file_path.read_text(
            encoding="utf-8",
            errors="ignore"
        )
        soup = BeautifulSoup(
            html,
            "html.parser"
        )
        for tag in soup(["style", "script", "noscript"]):
            tag.decompose()

        title = soup.title.string.strip() if soup.title and soup.title.string else file_path.stem

        text = soup.get_text(
            "\n",
            strip=True
        )
        return ParsedDocument(
            filename=file_path.name,
            elements=[DocumentElement(type="paragraph", content=text, section=None, page=None)],
            title=title,
            metadata={"source_url": str(file_path), "content_type": "html"}
        )

    def supports(self, extension: str) -> bool:
        return extension.lower() in {".html", ".htm"}