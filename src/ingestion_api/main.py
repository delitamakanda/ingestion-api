from fastapi import FastAPI

app = FastAPI(
    title="Ingestion API",
    version="0.1.0",
    description="Ingestion API",
    docs_url="/docs",
    openapi_tags=[{"name": "Ingestion API", "description": "Ingestion API"}],
)

@app.get("/health")
async def health():
    return {"status": "ok", "service": "ingestion-api"}