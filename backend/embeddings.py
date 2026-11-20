from langchain_google_genai import GoogleGenerativeAIEmbeddings
from backend.config import settings

class EmbeddingsService:
    def __init__(self):
            self.embeddings = GoogleGenerativeAIEmbeddings(
                model=settings.embedding_model
            )
            