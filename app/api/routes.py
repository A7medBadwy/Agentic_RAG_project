import tempfile
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.core.config import settings
from app.ingestion.pipeline import process_file, ALLOWED
from app.services.vector_store import upsert_chunks, list_documents, delete_document
from app.agents.orchestrator import Orchestrator
from app.schemas import ChatRequest, ChatResponse

router = APIRouter()
orchestrator = Orchestrator()

@router.get("/health")
async def health():
    return {"status": "ok", "service": settings.app_name}

@router.post("/upload")
async def upload_documents(files: list[UploadFile] = File(...)):
    results = []
    for upload in files:
        suffix = Path(upload.filename or "").suffix.lower()
        if suffix not in ALLOWED:
            raise HTTPException(400, f"Unsupported file: {upload.filename}. Allowed: PDF, DOCX, TXT")
        content = await upload.read()
        if len(content) > settings.max_upload_mb * 1024 * 1024:
            raise HTTPException(413, f"{upload.filename} exceeds {settings.max_upload_mb} MB")
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir) / f"upload{suffix}"
            temp_path.write_bytes(content)
            chunks = process_file(temp_path, Path(upload.filename).name)
        upsert_chunks(chunks)
        results.append({
            "filename": upload.filename,
            "document_id": chunks[0]["document_id"] if chunks else None,
            "chunks_indexed": len(chunks)
        })
    return {"uploaded": results}

@router.get("/documents")
async def documents():
    return {"documents": list_documents()}

@router.delete("/documents/{document_id}")
async def remove_document(document_id: str):
    delete_document(document_id)
    return {"deleted": document_id}

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        result = await orchestrator.run(request.question)
        return result
    except Exception as exc:
        raise HTTPException(500, f"Chat workflow failed: {exc}") from exc
