from ingestion_api.domain.ingestion.enrichment.models import ExtractedMetadata

class MetadataNormalizer:

    def merge(self, deterministic: ExtractedMetadata, llm_metadata) -> ExtractedMetadata:
        result = deterministic.model_copy(
            deep=True
        )

        if not result.countries:
            result.countries = llm_metadata.countries
            if result.countries:
                result.confidence.countries = 0.75

        if not result.language:
            result.language = llm_metadata.language
            if result.language:
                result.confidence.language = 0.8

        if not result.authority:
            result.authority = llm_metadata.authority
            if result.authority:
                result.confidence.authority = 0.8

        if not result.source_type:
            result.source_type = llm_metadata.source_type
            if result.source_type:
                result.confidence.source_type = 0.8

        if not result.publication_date:
            result.publication_date = llm_metadata.publication_date
            if result.publication_date:
                result.confidence.publication_date = 0.8

        if not result.effective_date:
            result.effective_date = llm_metadata.effective_date
            if result.effective_date:
                result.confidence.effective_date = 0.8

        if not result.expiration_date:
            result.expiration_date = llm_metadata.expiration_date
            if result.expiration_date:
                result.confidence.expiration_date = 0.8

        result.legal_references = sorted(
            set(result.legal_references) | set(llm_metadata.legal_references)
        )

        result.topics = sorted(set(llm_metadata.topics))

        return result