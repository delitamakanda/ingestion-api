import re
from datetime import date

from ingestion_api.domain.ingestion.enrichment.legal_references import extract_legal_references
from ingestion_api.domain.ingestion.enrichment.models import ExtractedMetadata

from ingestion_api.domain.ingestion.schemas import ParsedDocument

COUNTRY_PATTERN = {
    "FR": [
        r"\bfrance\b",
        r"\bfrench\b",
    ],
    "DE": [
        r"\bgermany\b",
        r"\bgerman\b",
        r"\bdeutschland\b",
    ],
    "ES": [
        r"\bspain\b",
        r"\bspanish\b",
        r"\bespaña\b",
    ],
    "BE": [
        r"\bbelgium\b",
        r"\bbelgian\b",
        r"\bbelgië\b",
    ],
    "NL": [
        r"\bnetherlands\b",
        r"\bnetherland\b",
        r"\bnederland\b",
    ],
    "IT": [
        r"\bitaly\b",
        r"\bitalian\b",
        r"\bitalia\b",
    ],
    "PT": [
        r"\bportugal\b",
        r"\bportuguese\b",
    ],
    "GB": [
        r"\bunited kingdom\b",
        r"\buk\b",
        r"\bengland\b",
        r"\bscotland\b",
        r"\bwales\b",
        r"\bnorthern ireland\b",
    ],
    "US": [
        r"\bunited states\b",
        r"\bus\b",
        r"\bamerica\b",
    ],
}

DATE_PATTERN = [
    r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",  # Matches dates like 12/31/2020 or 31-12-2020
    r"\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b",  # Matches dates like 2020/12/31 or 2020-12-31
    r"\b\d{1,2}\s+\w+\s+\d{4}\b",  # Matches dates like 31 December 2020
    r"\b\w+\s+\d{1,2},\s+\d{4}\b",  # Matches dates like December 31, 2020
    r"\b\d{1,2}\s+\w+\s+\d{2}\b",  # Matches dates like 31 December 20
    r"\b\w+\s+\d{1,2},\s+\d{2}\b",  # Matches dates like December 31, 20
    r"\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}\b",
]


class DeterminisiticMetadataExtractor:
    """
    A deterministic metadata extractor that uses regex patterns to extract metadata from a document.
    """

    async def extract_metadata(self, parsed_document: ParsedDocument) -> ExtractedMetadata:
        """
        Extracts metadata from the given parsed document.

        Args:
            parsed_document (ParsedDocument): The parsed document from which to extract metadata.)
        """
        text = self._build_sample(parsed_document)
        metadata = ExtractedMetadata()

        # Extract country from the document text
        metadata.countries = (
            self._extract_countries(text)
        )

        if metadata.countries:
            metadata.confidence.countries = 0.9  # High confidence for deterministic extraction
        metadata.legal_references = (
            extract_legal_references(text)
        )
        if metadata.legal_references:
            metadata.confidence.legal_references = 0.9  # High confidence for deterministic extraction

        metadata.language = self._guess_language(text)
        if metadata.language:
            metadata.confidence.language = 0.9  # High confidence for deterministic extraction

        metadata.publication_date = self._extract_publication_date(text)
        if metadata.publication_date:
            metadata.confidence.publication_date = 0.9  # High confidence for deterministic extraction

        return metadata

    def _extract_country(self, text: str) -> str:
        """
        Extracts the country from the given text using regex patterns.

        Args:
            text (str): The text from which to extract the country.

        Returns:
            str: The extracted country code, or None if no country is found.
        """
        for country_code, patterns in self.country_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return country_code
        return None

    def _build_sample(self, parsed_document: ParsedDocument) -> str:
        """
        Builds a sample text from the parsed document for metadata extraction.

        Args:
            parsed_document (ParsedDocument): The parsed document from which to build the sample text.
        """
        parts = [
            parsed_document.title or "",
            parsed_document.filename or "",
        ]
        for element in parsed_document.elements[:10]:  # Limit to the first 10 elements for performance
            parts.append(element.content or "")
        return "\n".join(parts)

    def _extract_countries(self, text: str) -> list[str]:
        """
        Extracts all countries mentioned in the given text using regex patterns.

        Args:
            text (str): The text from which to extract countries.
        """
        text = text.lower()
        countries = []
        for country_code, patterns in COUNTRY_PATTERN.items():
            if any(re.search(pattern, text) for pattern in patterns):
                countries.append(country_code)
        return countries

    def _guess_language(self, text: str) -> str | None:
        """
        Guesses the language from the given text using regex patterns.

        Args:
            text (str): The text from which to guess the language.
        """
        text = text.lower()

        markers = {
            "fr": [
                " le ",
                " la ",
                " des ",
                " biométhane",
                " déjà ",
                " mais ",
            ],
            "en": [
                " the ",
                " and ",
                " of ",
                " to ",
                " in ",
            ],
            "de": [
                " der ",
                " die ",
                " das ",
                " und ",
                " zu ",
            ],
            "ja": [
                " の ",
                " です ",
                " ます ",
                " する ",
                " いる ",
            ],
            "zh": [
                " 的 ",
                " 是 ",
                " 在 ",
                " 有 ",
                " 不 ",
            ],
            "ko": [
                " 의 ",
                " 는 ",
                " 이 ",
                " 에 ",
                " 가 ",
            ],
        }

        scores = {
            language: sum(text.count(marker) for marker in markers_list)
            for language, markers_list in markers.items()
        }

        language = max(scores, key=scores.get)
        return language if scores[language] > 0 else None

    def _extract_publication_date(self, text: str) -> date | None:
        for pattern in DATE_PATTERN:
            match = re.search(pattern, text)
            if match:
                try:
                    return date.fromisoformat(match.group())
                except ValueError:
                    continue
        return None
