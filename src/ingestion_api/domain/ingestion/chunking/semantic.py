from typing import cast

from ingestion_api.domain.ingestion.schemas import ChunkData,ParsedDocument

class SemanticChunker:
    def __init__(self, max_chunk_size: int = 1000, overlap_chars: int = 500):
        self.max_chunk_size = max_chunk_size
        self.overlap_chars = overlap_chars

    def chunk(self, parsed_document: ParsedDocument) -> list[ChunkData]:
        """
        Chunk the parsed document into smaller chunks based on semantic boundaries.

        Args:
            parsed_document (ParsedDocument): The parsed document to be chunked.

        Returns:
            list[ChunkData]: A list of ChunkData objects representing the chunks.
        """
        chunks: list[ChunkData] = []
        buffer: list[str] = []
        current_size = 0
        current_section = ""

        page_start: int | None = None
        page_end: int | None = None

        for element in parsed_document.elements:
            text = element.content.strip()
            if not text:
                continue

            element_page = element.page

            # new section can enforce close previous chunk
            if element.type == "heading" and buffer:
                self._flush(chunks=chunks, buffer=buffer, section=current_section, page_start=page_start, page_end=page_end)
                buffer = []
                current_size = 0
                page_start = element_page
                page_end = element_page
            current_section = element.section or current_section

            if page_start is None and element_page is not None:
                page_start = element_page
            if page_end is None and element_page is not None:
                page_end = element_page

            projected_size = current_size + len(text)
            if projected_size > self.max_chunk_size and buffer:
                self._flush(chunks=chunks, buffer=buffer, section=current_section, page_start=page_start, page_end=page_end)

                overlap = self._build_overlap(buffer)

                buffer = ([overlap] if overlap else [])

                current_size = len(overlap) if overlap else 0

                page_start = element_page
                page_end = element_page

            buffer.append(text)

            current_size += len(text)

        if buffer:
            self._flush(chunks=chunks, buffer=buffer, section=current_section, page_start=page_start, page_end=page_end)

        return chunks


    def _flush(self, *, chunks: list[ChunkData], buffer: list[str], section: str, page_start: int| None, page_end: int| None):
        chunk_content = "\n\n".join(buffer).strip()

        if not chunk_content:
            return

        chunks.append(ChunkData(
            text=chunk_content,
            section=section,
            page_start=page_start,
            page_end=page_end,
            chunk_index=len(chunks),
        ))

    def _build_overlap(self, buffer: list[str]) -> str:
        """
        Build the overlap string from the buffer based on the specified overlap size.

        Args:
            buffer (list[str]): The buffer containing the text elements.
        """
        previous = "\n\n".join(buffer)
        if len(previous) <= self.overlap_chars:
            return previous
        return previous[-self.overlap_chars:]

