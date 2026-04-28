from typing import TypedDict, Optional, List

class AgentState(TypedDict):
    query: str
    context: Optional[str]
    generated_sql: Optional[str]
    sql_result: Optional[List]
    answer: Optional[str]
    error: Optional[str]
    sql_success: bool
    retry_count: int