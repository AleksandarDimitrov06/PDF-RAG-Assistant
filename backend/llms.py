from langchain.chat_models import init_chat_model
from backend.config import settings

class LLMsService:
    def __init__(self):
            self.llm = init_chat_model(
                settings.llm_model,
                model_provider=settings.llm_provider,
                temperature=0.3,
                max_retries=1,
            )
            self.question_rewrite_llm = init_chat_model(
                settings.question_rewrite_model,
                model_provider=settings.llm_provider,
                temperature=0.3,
                max_retries=1,
            )