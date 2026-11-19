from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from api.dependencies import get_vector_service, get_rustfs_service
from api.schemas import UploadResponse
from backend.vectorstore import QdrantService
from backend.RustFSService import RustFSService
import hashlib
import tempfile
import os

router = APIRouter()


@router.post("/upload", response_model=UploadResponse)
async def upload_pdf(session_id: str = Query(...),
                     file: UploadFile = File(...),
                     vector_service: QdrantService = Depends(get_vector_service),
                     object_storage: RustFSService = Depends(get_rustfs_service)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    file_bytes = await file.read()
    document_hash = hashlib.sha256(file_bytes).hexdigest()

    object_key = f"{session_id}/{document_hash}/{file.filename}"
    object_storage.upload_pdf(file_bytes, object_key)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        temp_file.write(file_bytes)
        temp_path = temp_file.name 
    try:
        vector_service.process_and_index_pdf(temp_path, session_id, file.filename, document_hash)
    finally:
        os.unlink(temp_path)

    return UploadResponse(session_id=session_id, filename=file.filename, document_hash=document_hash, message="PDF processed successfully!")


