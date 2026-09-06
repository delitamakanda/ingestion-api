from fileinput import filename
from pathlib import Path
from tempfile import NamedTemporaryFile
from urllib.parse import urlparse

import httpx

from ingestion_api.domain.ingestion.parsers.web import WebParser
from ingestion_api.domain.ingestion.pipeline import IngestionPipeline


class RegulationService:

    def __init__(self, session, web_parser: WebParser, pipeline: IngestionPipeline):
        self.session = session
        self.web_parser = web_parser
        self.pipeline = pipeline

    async def enrich_regulation(self, regulation_urls: list[str]):
        documents = []
        for url in regulation_urls:
            document = await self._find_existing_url(url)
            if document:
                documents.append(document)
                continue
            document = await self._ingest_url(url)
            documents.append(document)
        return documents

    async def _find_existing_url(self, url: str):
        normalize_url = self._normalized_url(url)
        return await self.pipeline.document_repository.get_by_source_url(normalize_url)

    async def _ingest_url(self, url: str):
        normalized_url = self._normalized_url(url)
        existing_document = await self.pipeline.document_repository.get_by_source_url(normalized_url)
        if existing_document:
            return existing_document

        async with httpx.AsyncClient(
            follow_redirects=True,
            timeout=30,
            verify=False,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
                ),
                "Accept": (
                    "text/html,application/xhtml+xml,application/xml;q=0.9,"
                    "application/pdf;q=0.8,*/*;q=0.7"
                ),
                "Content-Type": "application/json",
                "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
            },
        ) as client:
            response = await client.get(normalized_url)
            response.raise_for_status()

        content = response.content.decode("utf-8")

        extension = self._resolve_extension(
            url=normalized_url,
            content_type=response.headers.get("Content-Type", "").lower()
        )
        with NamedTemporaryFile(suffix=extension, delete=False) as temp_file:
            temp_file.write(content.encode("utf-8"))
            temp_file_path = Path(temp_file.name)

        try:
            import hashlib
            content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
            document = await self.pipeline.ingest(file_path=temp_file_path, content_hash=content_hash,original_filename=self._build_filename(normalized_url, extension))

            await self.pipeline.document_repository.attach_source_url(document.id, normalized_url)

            return document
        finally:
            temp_file_path.unlink(missing_ok=True)

    def _normalized_url(self, url: str):
        return url.strip().lower()

    @staticmethod
    def _resolve_extension(*, url: str, content_type: str | None) -> str:
        suffix = Path(urlparse(url).path).suffix.lower()
        if suffix in [".pdf", ".docx", ".txt", ".html", ".htm"]:
            return suffix
        content_type = (content_type or "").lower()

        if "application/pdf" in content_type:
            return ".pdf"
        if "application/vnd.openxmlformats-officedocument" in content_type:
            return ".docx"
        if "text/html" in content_type:
            return ".html"
        return ".txt"

    def _build_filename(self, url: str, extension: str):
        parsed = urlparse(url)
        filename = Path(parsed.path).name
        if filename:
            return filename
        return f"regulation{extension}"