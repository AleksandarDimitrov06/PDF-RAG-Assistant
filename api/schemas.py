from pydantic import BaseModel

class QueryRequest(BaseModel):
    session_id: str
    document_hash: str
    question: str

class QueryResponse(BaseModel):
    answer: str

class UploadResponse(BaseModel):
    session_id: str
    filename: str
    document_hash: str
    message: str