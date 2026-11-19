from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.models import FieldCondition, Filter, MatchValue
from backend.config import settings

class QdrantService:
    def __init__(self,embeddings):
        self.embeddings = embeddings
        self.url = settings.qdrant_url
        self.collection_name = settings.collection_name
        self.client = QdrantClient(url=self.url)
        self.vector_store = None


    def _get_vector_store(self) -> QdrantVectorStore:
        if self.vector_store is None:
            if not self.client.collection_exists(self.collection_name):
                raise RuntimeError(
                    f"Qdrant collection '{self.collection_name}' does not exist"
                )

            self.vector_store = QdrantVectorStore.from_existing_collection(
                embedding=self.embeddings,
                url=self.url,
                collection_name=self.collection_name,
            )

        return self.vector_store


    def _document_is_indexed(self, session_id: str, document_hash: str) -> bool:
        if not self.client.collection_exists(self.collection_name):
            return False
        
        document_filter = Filter(
            must=[
                FieldCondition(
                    key="metadata.session_id",
                    match=MatchValue(value=session_id),
                ),
                FieldCondition(
                    key="metadata.document_hash",
                    match=MatchValue(value=document_hash),
                ),
            ]
        )

        result = self.client.count(
            collection_name=self.collection_name,
            count_filter=document_filter,
            exact=True,
        )

        return result.count > 0
    

    def process_and_index_pdf(self, pdf_path: str, session_id:str, filename:str, document_hash:str) -> None:

        if self._document_is_indexed(session_id, document_hash):
            self._get_vector_store()
            return
        
        docs = PyPDFLoader(pdf_path).load()
        chunks = RecursiveCharacterTextSplitter(
            chunk_size=2500, 
            chunk_overlap=500
        ).split_documents(docs)

        for chunk in chunks:
            chunk.metadata["session_id"]=session_id
            chunk.metadata["document_hash"]=document_hash
            chunk.metadata["filename"]=filename

        self.vector_store = QdrantVectorStore.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            url=self.url,
            collection_name=self.collection_name,
        )



    def get_retriever(self, session_id: str, document_hash: str):
        vector_store = self._get_vector_store()

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
        return vector_store.as_retriever(search_kwargs={"k": 4, "filter": session_filter})