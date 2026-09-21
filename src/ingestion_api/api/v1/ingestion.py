import hashlib
from functools import lru_cache
from pathlib import Path
from uuid import uuid4
from typing import Annotated

from fastapi import APIRouter, File, UploadFile as FastAPIUploadFile, Depends
from pydantic import WithJsonSchema

from sqlalchemy.ext.asyncio import AsyncSession

from ingestion_api.core.config import settings
from ingestion_api.core.database import get_db
from ingestion_api.domain.jobs.repository import JobRepository
from ingestion_api.llm.embeddings.sentence_transformer import SentenceTransformerEmbeddingService
from ingestion_api.workers.broker import ArqJobBroker
from ingestion_api.core.logging import get_logger

logger = get_logger(__name__)

broker = ArqJobBroker()

router = APIRouter(
    prefix="/ingestion",
    tags=["ingestion"],
    responses={404: {"description": "Not found"}},
)

SwaggerUploadFile = Annotated[
    FastAPIUploadFile,
    WithJsonSchema({
        "type": "string",
        "format": "binary",
    })
]

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}

@lru_cache()
def get_embedding_service():
    return SentenceTransformerEmbeddingService(model_name=settings.embedding_model)

@router.post("/documents")
async def upload_documents(files: list[SwaggerUploadFile] = File(...), session: AsyncSession = Depends(get_db)):
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)

    job_repository = JobRepository(session)

    jobs = []

    for file in files:
        original_filename = (file.filename or "")
        extension = Path(original_filename).suffix.lower()
        if extension not in ALLOWED_EXTENSIONS:
            jobs.append({
                "original_filename": original_filename,
                "stored_filename": None,
                "content_hash": None,
                "size": 0,
                "status": "failed",
                "error": f"File type {extension} is not allowed"
            })
            continue
        content = await file.read()

        content_hash = hashlib.sha256(content).hexdigest()

        existing_job = await job_repository.find_by_content_hash(content_hash)
        if existing_job:
            jobs.append({
                "job_id": str(existing_job.id),
                "original_filename": original_filename,
                "status": existing_job.status,
                "duplicate": True,
            })
            continue

        stored_filename = f"{uuid4()}{extension}"

        path = upload_dir / stored_filename
        path.write_bytes(content)

        job = await job_repository.create_job(original_filename=original_filename, stored_filename=stored_filename, content_hash=content_hash)

        logger.info("ingestion.job.created", job_id=str(job.id), original_filename=original_filename, content_hash=content_hash)

        jobs.append({
            "job_id": str(job.id),
            "original_filename": original_filename,
            "status": job.status,
        })

        await session.commit()

        await broker.enqueue_ingestion(job.id)

    return {
        "count": len(jobs),
        "jobs": jobs
    }
