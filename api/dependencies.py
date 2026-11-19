from fastapi import Request
from backend.llm import LLMService
from backend.vectorstore import QdrantService
from backend.RAG_logic import RAGCore
from backend.RustFSService import RustFSService

class AppDependencies:
    def __init__(self):
        self._llm_service = LLMService()
        self._vector_service = QdrantService(embeddings=self._llm_service.embeddings)
        self._rag_builder = RAGCore(llm_service=self._llm_service)
        self._rustfs_service = RustFSService()


    @property
    def llm_service(self) -> LLMService:
        return self._llm_service

    @property
    def vector_service(self) -> QdrantService:
        return self._vector_service

    @property
    def rag_builder(self) -> RAGCore:
        return self._rag_builder

    @property
    def rustfs_service(self) -> RustFSService:
        return self._rustfs_service

def get_app_dependencies(request: Request) -> AppDependencies:
    return request.app.state.dependencies