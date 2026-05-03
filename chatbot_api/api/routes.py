from fastapi import APIRouter
import json

from node.qdrant_retriever import get_context_from_qdrant
from agent.graph import app as agent_app
from api.schemas import ChatRequest, ChatResponse, QueryRequest
from api.helpers import serialize_to_json

router = APIRouter()

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
        # Dùng `is not None` thay vì `if raw_data` để phân biệt
        # "SQL trả về 0 hàng" ([] → []) với "SQL chưa chạy" (None → None)
        raw_data = result.get("sql_result")
        if raw_data is not None:
            safe_data = json.loads(json.dumps(raw_data, default=serialize_to_json))
        else:
            safe_data = None

        return ChatResponse(
            status="success" if result.get("sql_success", False) else "error",
            data={
                "answer": result.get("answer") or "",
                "sql_result": safe_data,
                "sql_query": result.get("generated_sql")
            },
            error=result.get("error") if not result.get("sql_success", False) else None
        )
    except Exception as e:
        return ChatResponse(
            status="error",
            error=str(e)
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
