from prometheus_client import Counter, Histogram


INGESTION_JOBS_TOTAL = Counter(
    "ingestion_jobs_total",
    "Total number of ingestion jobs",
    ["job_type", "status"],
)

INGESTION_DURATION_SECONDS = Histogram(
    "ingestion_duration_seconds",
    "Duration of ingestion jobs in seconds",
    ["job_type"],
)

RETRIEVAL_REQUESTS_TOTAL = Counter(
    "retrieval_jobs_total",
    "Total number of retrieval jobs",
    ["status"],
)

RETRIEVAL_DURATION_SECONDS = Histogram(
    "retrieval_duration_seconds",
    "Duration of retrieval jobs in seconds",
)
RETRIEVAL_RESULTS = Histogram(
    "retrieval_results",
    "Number of results returned by retrieval jobs",
)

LLM_REQUESTS_TOTAL = Counter(
    "llm_requests_total",
    "Total number of LLM requests",
    ["status"],
)

LLM_DURATION_SECONDS = Histogram(
    "llm_duration_seconds",
    "Duration of LLM requests in seconds",
)

RERANKER_REQUESTS_TOTAL = Counter(
    "reranker_requests_total",
    "Total number of reranker requests",
)

RERANKER_DURATION_SECONDS = Histogram(
    "reranker_duration_seconds",
    "Duration of reranker requests in seconds",
)

RERANKER_CANDIDATES = Histogram(
    "reranker_candidates",
    "Number of candidates returned by reranker requests",
)