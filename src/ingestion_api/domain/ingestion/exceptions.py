class IngestionError(Exception):
    """Base class for ingestion errors."""


class RetryableIngestionError(IngestionError):
    """Exception raised for retryable ingestion errors."""


class PermanentIngestionError(IngestionError):
    """Exception raised for permanent ingestion errors."""
