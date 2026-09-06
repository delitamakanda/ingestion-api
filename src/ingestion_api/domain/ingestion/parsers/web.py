import httpx
from bs4 import BeautifulSoup

from ingestion_api.domain.ingestion.schemas import DocumentElement, ParsedDocument


class WebParser:
    async def parse(self, url: str) -> ParsedDocument:
        async with httpx.AsyncClient(
                follow_redirects=True,
                timeout=30,
                verify=False,
                headers={
                    "User-Agent": (
                            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                            "AppleWebKit/537.36 (KHTML, like Gecko) "
                            "Chrome/152.0.0.0 Safari/537.36"
                    ),
                    "Accept": (
                            "text/html,application/xhtml+xml,application/xml;q=0.9,"
                            "application/pdf;q=0.8,*/*;q=0.7"
                    ),
                    "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
                }
        ) as client:
            response = await client.get(url)
            response.raise_for_status()
            html_content = response.text

        soup = BeautifulSoup(html_content, 'html.parser')

        for element in soup(['style', 'script', 'nav', 'footer']):
            element.decompose()

        elements = []

        current_section = None
        for node in soup.find_all(["h1", "h2", "h3", "h4", "p", "li", "table"]):
            text_content = node.get_text('', strip=True)
            if not text_content:
                continue
            if node.name.startswith("h"):
                current_section = text_content
                elements.append(DocumentElement(type="heading", content=text_content, section=current_section))
            elif node.name == "table":
                elements.append(DocumentElement(type="table", content=text_content, section=current_section))
            else:
                elements.append(DocumentElement(type="paragraph", content=text_content, section=current_section))

        title = (
            soup.title.string.strip() if soup.title and soup.title.string else url
        )

        return ParsedDocument(filename=url, elements=elements, title=title,
                              metadata={"source_url": url, "content_type": "web"})
