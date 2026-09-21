class IngestionError(Exception):
    """Base class for ingestion errors."""
    pass

class RetryableIngestionError(IngestionError):
    """Exception raised for retryable ingestion errors."""
    pass

class PermanentIngestionError(IngestionError):
    """Exception raised for permanent ingestion errors."""
    pass