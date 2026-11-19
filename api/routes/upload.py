from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from api.dependencies import AppDependencies, get_app_dependencies
from api.schemas import UploadResponse
import hashlib
import tempfile
import os

router = APIRouter()


@router.post("/upload", response_model=UploadResponse)
async def upload_pdf(session_id: str = Query(...),
                     file: UploadFile = File(...),
                     dependencies: AppDependencies = Depends(get_app_dependencies)
):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    file_bytes = await file.read()
    document_hash = hashlib.sha256(file_bytes).hexdigest()

    object_key = f"{session_id}/{document_hash}/{file.filename}"
    dependencies.rustfs_service.upload_pdf(file_bytes, object_key)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        temp_file.write(file_bytes)
        temp_path = temp_file.name 
    try:
        dependencies.vector_service.process_and_index_pdf(temp_path, session_id, file.filename, document_hash)
    finally:
        os.unlink(temp_path)

    return UploadResponse(session_id=session_id, filename=file.filename, document_hash=document_hash, message="PDF processed successfully!")


