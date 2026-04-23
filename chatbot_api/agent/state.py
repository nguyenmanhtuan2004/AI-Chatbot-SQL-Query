from typing import TypedDict, Optional

class AgentState(TypedDict):
    query: str
    context: Optional[str]
    sql_query: Optional[str]
    error: Optional[str]