from abc import ABC, abstractmethod
from pathlib import Path


from ingestion_api.domain.ingestion.schemas import ParsedDocument

class DocumentParser(ABC):
    @abstractmethod
    async def parse(self, file_path: Path) -> ParsedDocument:
        ...

    @abstractmethod
    def supports(self, extension: str) -> bool:
        ...