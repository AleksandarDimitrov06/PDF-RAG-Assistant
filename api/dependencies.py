from backend.llm import LLMService
from backend.vectorstore import QdrantService
from backend.RAG_logic import RAGCore
from backend.RustFSService import RustFSService

llm_service = LLMService()
vector_service = QdrantService(embeddings=llm_service.embeddings)
rag_builder = RAGCore(llm_service=llm_service)
rustfs_service = RustFSService()


def get_vector_service() -> QdrantService:
    return vector_service

def get_rag_builder() -> RAGCore:
    return rag_builder

def get_rustfs_service() -> RustFSService:
    return rustfs_service