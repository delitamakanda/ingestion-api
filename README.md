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