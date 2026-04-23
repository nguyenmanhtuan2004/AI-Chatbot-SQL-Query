from fastapi import APIRouter
from pydantic import BaseModel
from rag.qdrant_retriever import get_context_from_qdrant

router = APIRouter()

class QueryRequest(BaseModel):
    query: str
    top_k: int = 5

@router.post("/rag/retrieve")
async def retrieve_context(req: QueryRequest):
    """
    API test thử việc trích xuất Vector DB (RAG)
    """
    try:
        context = get_context_from_qdrant(req.query, req.top_k)
        return {
            "status": "success", 
            "query": req.query,
            "context": context
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
