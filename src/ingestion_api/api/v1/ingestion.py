import hashlib
from pathlib import Path
from uuid import uuid4
from typing import Annotated

from fastapi import APIRouter, File, UploadFile as FastAPIUploadFile
from pydantic import WithJsonSchema

from ingestion_api.core.config import settings

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
async def upload_documents(files: list[SwaggerUploadFile] = File(...)):
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)

    documents = []

    for f in files:
        extension = Path(f.filename or "").suffix.lower()
        if extension not in ALLOWED_EXTENSIONS:
            continue

        content = await f.read()

        content_hash = hashlib.sha256(content).hexdigest()

        filename = (
            f"{uuid4()}{extension}"
        )

        path = upload_dir / filename

        path.write_bytes(content)

        documents.append({
            "original_filename": f.filename,
            "stored_filename": filename,
            "content_hash": content_hash,
            "size": len(content),
        })

    return {
        "count": len(documents),
        "documents": documents
    }


