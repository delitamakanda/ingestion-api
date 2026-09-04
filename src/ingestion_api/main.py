from fastapi import FastAPI
from ingestion_api.api.router import api_router

app = FastAPI(
    title="Ingestion API",
    version="0.1.0",
    description="Ingestion API",
    docs_url="/docs",
)

app.include_router(api_router)

@app.get("/health")
async def health():
    return {"status": "ok", "service": "ingestion-api"}