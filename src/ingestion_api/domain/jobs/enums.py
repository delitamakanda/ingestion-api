from enum import StrEnum

class JobStatus(StrEnum):
    PENDING = "pending"
    PARSING = "parsing"
    ENRICHING = "enriching"
    CHUNKING = "chunking"
    EMBEDDING = "embedding"
    INDEXING = "indexing"
    COMPLETED = "completed"
    FAILED = "failed"


class ProcessingStep(StrEnum):
    PARSING = "parsing"
    ENRICHING = "enriching"
    CHUNKING = "chunking"
    EMBEDDING = "embedding"
    INDEXING = "indexing"
