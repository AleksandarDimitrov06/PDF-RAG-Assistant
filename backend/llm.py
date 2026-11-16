from langchain.chat_models import init_chat_model
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from backend.config import settings

class LLMService:
    def __init__(self):
            self.llm = init_chat_model(
                settings.llm_model,
                model_provider=settings.llm_provider,
                temperature=0.3,
                max_retries=1,
            )
            self.embeddings = GoogleGenerativeAIEmbeddings(
                model=settings.embedding_model
            )
            self.question_rewrite_llm = init_chat_model(
                settings.question_rewrite_model,
                model_provider=settings.llm_provider,
                temperature=0.3,
                max_retries=1,
            )