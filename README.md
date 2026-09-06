# Ingestion API

```text
ingestion-api/
│
├── pyproject.toml
├── alembic.ini
├── docker-compose.yml
├── .env.example
│
├── alembic/
│   └── versions/
│
├── src/ingestion_api/
│   ├── main.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── logging.py
│   │   └── exceptions.py
│   │
│   ├── api/
│   │   ├── router.py
│   │   └── v1/
│   │       ├── documents.py
│   │       ├── ingestion.py
│   │       ├── search.py
│   │       └── jobs.py
│   │
│   ├── domain/
│   │   ├── documents/
│   │   │   ├── models.py
│   │   │   ├── schemas.py
│   │   │   ├── repository.py
│   │   │   └── service.py
│   │   │
│   │   ├── search/
│   │   │   ├── schemas.py
│   │   │   ├── enums.py
│   │   │   ├── router.py
│   │   │   │
│   │   │   └── strategies/
│   │   │       ├── base.py
│   │   │       ├── keyword.py
│   │   │       ├── text.py
│   │   │       └── natural_language.py
│   │   │
│   │   └── ingestion/
│   │       ├── schemas.py
│   │       ├── pipeline.py
│   │       │
│   │       ├── parsers/
│   │       │   ├── base.py
│   │       │   ├── docx.py
│   │       │   ├── pdf.py
│   │       │   └── web.py
│   │       │
│   │       ├── chunking/
│   │       │   ├── semantic.py
│   │       │   └── tables.py
│   │       │
│   │       └── enrichment/
│   │           ├── metadata.py
│   │           ├── countries.py
│   │           └── legal_references.py
│   │
│   ├── retrieval/
│   │   ├── lexical.py
│   │   ├── vector.py
│   │   ├── hybrid.py
│   │   ├── reranker.py
│   │   └── filters.py
│   │
│   ├── llm/
│   │   ├── client.py
│   │   ├── embeddings.py
│   │   ├── prompts.py
│   │   │
│   │   └── agents/
│   │       ├── query_planner.py
│   │       ├── retrieval.py
│   │       ├── regulation.py
│   │       ├── temporal.py
│   │       └── synthesis.py
│   │
│   └── workers/
│       ├── broker.py
│       └── ingestion.py
│
└── tests/
    ├── ingestion/
    ├── retrieval/
    └── search/
```

## Getting Started

```bash
uv run uvicorn ingestion_api.main:app --reload
```

or with docker

```bash
docker-compose up -d
```

## Inital Setup

Initial alembic setup

```bash
uv run alembic init alembic
uv run alembic revision --autogenerate -m "create documents"
or 
uv run alembic revision -m "add trigram search index"
uv run alembic upgrade head
```

## Actiivate PGVector
```bash
docker compose exec postgres psql -U ingestion -d ingestion
```

in postgres
```text
CREATE EXTENSION IF NOT EXISTS vector;

CREATE EXTENSION IF NOT EXISTS pg_trgm;

CREATE EXTENSION IF NOT EXISTS pg_trgm;
```

## acces to postgres database
```bash
docker compose exec postgres psql -U ingestion -d ingestion

SELECT
    id,
    file_name,
    title,
    status
FROM documents;

SELECT
    document_id,
    chunk_index,
    page_start,
    page_end,
    LEFT(text, 200)
FROM document_chunks
ORDER BY document_id, chunk_index;


SELECT
    chunk_index,
    sections,
    search_vector
FROM document_chunks
LIMIT 5

SELECT
    COUNT(*) AS total,
    COUNT(embedding) AS embedded
FROM document_chunks;

SELECT
    vector_dims(embedding)
FROM document_chunks
WHERE embedding IS NOT NULL
LIMIT 1;
```