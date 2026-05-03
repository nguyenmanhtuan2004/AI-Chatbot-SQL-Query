from pydantic import BaseModel
from typing import Any, List, Optional, Dict

class QueryRequest(BaseModel):
    query: str
    top_k: int = 5

class ChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = None

class ChatResponseData(BaseModel):
    answer: str
    sql_result: Optional[List[Dict[str, Any]]] = None
    sql_query: Optional[str] = None

class ChatResponse(BaseModel):
    status: str
    data: Optional[ChatResponseData] = None
    error: Optional[str] = None
