from fastapi import APIRouter, Depends
from api.dependencies import get_rag_builder, get_vector_service
from api.schemas import QueryRequest, QueryResponse
from backend.RAG_logic import RAGCore
from backend.vectorstore import QdrantService

router = APIRouter()


@router.post("/query", response_model=QueryResponse)
async def query_rag(
    request: QueryRequest, 
    vector_service: QdrantService = Depends(get_vector_service),
    rag_builder: RAGCore = Depends(get_rag_builder)
    ):
    retriever = vector_service.get_retriever(request.session_id, request.document_hash)
    chain = rag_builder.build_rag_chain(retriever)

    response = chain.invoke(
        {"input": request.question},
        config={"configurable": {"session_id": request.session_id}},
    )
    return QueryResponse(answer=response["answer"])