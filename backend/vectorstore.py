from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_qdrant import QdrantVectorStore
from qdrant_client.models import FieldCondition, Filter, MatchValue
from backend.config import settings

class QdrantService:
    def __init__(self,embeddings):
        self.embeddings = embeddings
        self.url = settings.qdrant_url
        self.collection_name = settings.collection_name
        self.vector_store = QdrantVectorStore.from_existing_collection(
                    embedding=self.embeddings,
                    url=self.url,
                    collection_name=self.collection_name,
                )


    def process_and_index_pdf(self, pdf_path: str, session_id:str, filename:str, document_hash:str) -> QdrantVectorStore:
        docs = PyPDFLoader(pdf_path).load()
        chunks = RecursiveCharacterTextSplitter(
            chunk_size=2500, 
            chunk_overlap=500
        ).split_documents(docs)

        for chunk in chunks:
            chunk.metadata["session_id"]=session_id
            chunk.metadata["document_hash"]=document_hash
            chunk.metadata["filename"]=filename

        vector_store = QdrantVectorStore.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            url=self.url,
            collection_name=self.collection_name,
        )
        return vector_store



    def get_retriever(self, session_id: str, document_hash: str):
        session_filter = Filter(
            must=[
                FieldCondition(
                    key="metadata.session_id",
                    match=MatchValue(value=session_id)
                ),
                FieldCondition(
                    key="metadata.document_hash",
                    match=MatchValue(value=document_hash)
                )
            ]
        )
        return self.vector_store.as_retriever(search_kwargs={"k": 4, "filter": session_filter})