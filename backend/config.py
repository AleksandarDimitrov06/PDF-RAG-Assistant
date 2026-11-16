import os
from dotenv import load_dotenv

load_dotenv(override=True)

class Settings:
    
    @property
    def llm_model(self) -> str:
        return os.getenv("LLM_MODEL")

    @property
    def question_rewrite_model(self) -> str:
        return os.getenv("QUESTION_REWRITE_MODEL")

    @property
    def llm_provider(self) -> str:
        return os.getenv("LLM_PROVIDER")

    @property
    def embedding_model(self) -> str:
        return os.getenv("EMBEDDING_MODEL")

    @property
    def qdrant_url(self) -> str:
        return os.getenv("QDRANT_URL", "http://localhost:6333")

    @property
    def collection_name(self) -> str:
        return "pdf_documents"

    @property
    def rustfs_endpoint(self) -> str:
        return os.getenv("RUSTFS_ENDPOINT", "http://localhost:9000")

    @property
    def rustfs_bucket(self) -> str:
        return os.getenv("RUSTFS_BUCKET", "documents")

    @property
    def rustfs_access_key(self) -> str:
        return os.getenv("RUSTFS_ACCESS_KEY", "")

    @property
    def rustfs_secret_key(self) -> str:
        return os.getenv("RUSTFS_SECRET_KEY", "")

settings = Settings()