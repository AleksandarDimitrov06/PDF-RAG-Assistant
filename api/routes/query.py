from fastapi import APIRouter, Depends, HTTPException
from api.dependencies import AppDependencies, get_app_dependencies
from api.schemas import QueryRequest, QueryResponse
from langchain_google_genai.chat_models import GoogleAPIError

router = APIRouter()


@router.post("/query", response_model=QueryResponse)
async def query_rag(
    request: QueryRequest, 
    dependencies: AppDependencies = Depends(get_app_dependencies)
    ):
    try:
        retriever = dependencies.vector_service.get_retriever(request.session_id, request.document_hash)
        chain = dependencies.rag_builder.build_rag_chain(retriever)

        response = chain.invoke(
            {"input": request.question},
            config={"configurable": {"session_id": request.session_id}},
        )
        return QueryResponse(answer=response["answer"])
    except GoogleAPIError as exc:
        raise HTTPException(status_code=503,detail=str(exc)) from exc
