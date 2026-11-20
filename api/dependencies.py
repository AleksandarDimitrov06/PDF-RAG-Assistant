from fastapi import Request
from backend.llms import LLMsService
from backend.vectorstore import QdrantService
from backend.RAG_logic import RAGCore
from backend.RustFSService import RustFSService
from backend.embeddings import EmbeddingsService

class AppDependencies:
    def __init__(self):
        self._llms_service = LLMsService()
        self._embeddings_service = EmbeddingsService()
        self._vector_service = QdrantService(embeddings=self._embeddings_service.embeddings)
        self._rag_builder = RAGCore(llms_service=self._llms_service)
        self._rustfs_service = RustFSService()


    @property
    def llms_service(self) -> LLMsService:
        return self._llms_service

    @property
    def embeddings_service(self) -> EmbeddingsService:
        return self._embeddings_service

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