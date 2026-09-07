from ingestion_api.domain.ingestion.enrichment.deterministic import DeterminisiticMetadataExtractor
from ingestion_api.domain.ingestion.enrichment.llm import LLMExtractedMetadata, LLMMetadataExtractor
from ingestion_api.domain.ingestion.enrichment.normalizer import MetadataNormalizer


class MetadataExtractor:

    def  __init__(self, deterministic_extractor: DeterminisiticMetadataExtractor, llm_extractor: LLMMetadataExtractor, normalizer: MetadataNormalizer):
        self.deterministic_extractor = deterministic_extractor
        self.llm_extractor = llm_extractor
        self.normalizer = normalizer

    async def extract_metadata(self, document):
        deterministic = (
            await self.deterministic_extractor.extract_metadata(document)
        )

        llm_metadata = await self.llm_extractor.extract_metadata(document)

        return self.normalizer.merge(deterministic, llm_metadata)