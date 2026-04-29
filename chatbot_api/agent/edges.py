from agent.state import AgentState
from langgraph.graph import END

def after_retrieve(state: AgentState) -> str:
    """Quyết định đi tiếp sang sinh SQL hay báo lỗi sau khi lấy context."""
    if state.get("error") is None and state.get("context"):
        return "generate_sql"
    return "handle_error"

def after_generate(state: AgentState) -> str:
    """Quyết định đi tiếp sang thực thi SQL hay báo lỗi sau khi sinh mã."""
    # Kiểm tra nếu SQL sinh ra báo lỗi hoặc không thành công
    sql = state.get("generated_sql")
    if state.get("sql_success") and sql and not sql.startswith("-- NO"):
        return "execute_sql"
    return "handle_error"

def after_execute(state: AgentState) -> str:
    if state.get("sql_success") and state.get("sql_result") is not None:
        return "generate_answer"
    
    retry_count = state.get("retry_count", 0)
    if retry_count < 2:
        return "generate_sql"
    return "handle_error"