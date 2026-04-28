from fastapi import APIRouter
from pydantic import BaseModel
from typing import Any, List, Optional
from decimal import Decimal
from datetime import date, datetime
import json

from rag.qdrant_retriever import get_context_from_qdrant
from agent.graph import app as agent_app

router = APIRouter()


# ---------- Schema ----------

class QueryRequest(BaseModel):
    query: str
    top_k: int = 5

class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    success: bool
    query: str
    generated_sql: Optional[str] = None
    sql_result: Optional[List[Any]] = None
    context: Optional[str] = None
    error: Optional[str] = None


# ---------- Helper ----------

def _serialize(obj: Any) -> Any:
    """Chuyển Decimal / date / datetime sang kiểu JSON-safe."""
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


# ---------- Endpoints ----------

@router.post("/chat", response_model=ChatResponse, summary="Gửi câu hỏi tới AI Chatbot")
async def chat(req: ChatRequest):
    """
    Nhận câu hỏi tự nhiên, chạy toàn bộ agent pipeline (RAG → SQL → Execute)
    và trả về kết quả dạng JSON cho frontend.
    """
    initial_state = {
        "query": req.query,
        "context": None,
        "generated_sql": None,
        "sql_result": None,
        "error": None,
        "sql_success": False,
        "retry_count": 0,
    }

    try:
        result = agent_app.invoke(initial_state)

        # Serialize dữ liệu trả về (Decimal, date...)
        raw_data = result.get("sql_result")
        if raw_data:
            safe_data = json.loads(json.dumps(raw_data, default=_serialize))
        else:
            safe_data = None

        return ChatResponse(
            success=result.get("sql_success", False),
            query=req.query,
            generated_sql=result.get("generated_sql"),
            sql_result=safe_data,
            context=result.get("context"),
            error=result.get("error"),
        )
    except Exception as e:
        return ChatResponse(
            success=False,
            query=req.query,
            error=str(e),
        )


@router.post("/rag/retrieve", summary="Test trích xuất Vector DB (RAG)")
async def retrieve_context(req: QueryRequest):
    """
    API test thử việc trích xuất Vector DB (RAG).
    """
    try:
        context = get_context_from_qdrant(req.query, req.top_k)
        return {
            "status": "success",
            "query": req.query,
            "context": context,
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
