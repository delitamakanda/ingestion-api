import hashlib
from pathlib import Path
from uuid import uuid4
from typing import Annotated

from fastapi import APIRouter, File, UploadFile as FastAPIUploadFile, HTTPException, Depends
from pydantic import WithJsonSchema

from ingestion_api.core.config import settings

from sqlalchemy.ext.asyncio import AsyncSession

from ingestion_api.domain.ingestion.pipeline import IngestionPipeline

from ingestion_api.core.config import settings
from ingestion_api.core.database import get_db

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

@router.post("/documents")
async def upload_documents(files: list[SwaggerUploadFile] = File(...), session: AsyncSession = Depends(get_db)):
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)

    pipeline = IngestionPipeline(session)


    documents = []

    for f in files:
        original_filename = f.filename or ""
        extension = Path(original_filename).suffix.lower()

        if extension not in ALLOWED_EXTENSIONS:
            documents.append({
                "original_filename": original_filename,
                "stored_filename": None,
                "content_hash": None,
                "size": 0,
                "status": "failed",
                "error": f"File type {extension} is not allowed"
            })
            continue

        content = await f.read()

        content_hash = hashlib.sha256(content).hexdigest()

        stored_filename = (
            f"{uuid4()}{extension}"
        )

        path = upload_dir / stored_filename

        path.write_bytes(content)


        try:
            document = await pipeline.ingest(
                file_path=path,
                content_hash=content_hash,
                original_filename=original_filename
            )
            await session.commit()
            documents.append({
                "original_filename": original_filename,
                "stored_filename": stored_filename,
                "content_hash": content_hash,
                "size": len(content),
                "status": document.status
            })

        except Exception as exc:
            await session.rollback()
            documents.append({
                "original_filename": original_filename,
                "stored_filename": stored_filename,
                "content_hash": content_hash,
                "size": len(content),
                "status": "failed",
                "error": str(exc)
            })

    return {
        "count": len(documents),
        "documents": documents
    }


