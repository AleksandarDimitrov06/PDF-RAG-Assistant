from langchain_classic.chains.history_aware_retriever import create_history_aware_retriever
from langchain_classic.chains.retrieval import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from backend.memory import get_session_history


class RAGCore:
    def __init__(self,llm_service):
        self.llm = llm_service.llm
        self.question_rewrite_llm = llm_service.question_rewrite_llm
    
    def build_rag_chain(self, retriever):

        question_prompt = ChatPromptTemplate.from_messages([
            ("system",
            "Given the chat history and the latest user question, "
            "rewrite the latest question so it can be understood without the chat history."
            "Do not answer the question, just rewrite it."
            ),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ])

        history_aware_retriever = create_history_aware_retriever(
            self.question_rewrite_llm,
            retriever,
            question_prompt
        )



        prompt = ChatPromptTemplate.from_messages([
            ("system",
             "You are a helpful assistant. Answer the question using ONLY the "
             "context below. Be concise. If the answer is not in the context, "
             "say you do not know. If the question is not related to the context, "
             "politely respond: I amtuned to only answer questions that are related to the context. "
             "\n\nContext:\n{context}"),
             MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ])

        question_answer_chain = create_stuff_documents_chain(
            self.llm,
            prompt,
        )

        rag_chain = create_retrieval_chain(
            history_aware_retriever,
            question_answer_chain
        )

        return RunnableWithMessageHistory(
            rag_chain, 
            get_session_history, 
            input_messages_key="input", 
            history_messages_key="chat_history",
            output_messages_key="answer",
        )
        







