from langchain_google_genai import ChatGoogleGenerativeAI
from agent.state import AgentState
from rag.qdrant_retriever import get_context_from_qdrant
from agent.sql_generator import generate_sql
from tools.sql_executor import execute_sql_query

# Khởi tạo mô hình ngôn ngữ
def retrieve_context_node(state: AgentState):
    """Lấy dữ liệu từ điển (schema & business rules) từ Qdrant."""
    query = state["query"]
    try:
        context = get_context_from_qdrant(query)
        if not context or "Không tìm thấy" in context:
            return {"context": None, "sql_success": False, "error": "Không tìm thấy dữ liệu nghiệp vụ liên quan."}
        return {"context": context, "sql_success": True, "error": None}
    except Exception as e:
        return {"sql_success": False, "error": f"Lỗi truy xuất context: {str(e)}"}

def generate_sql_node(state: AgentState):
    """Sử dụng SQL Generator để sinh ra mã SQL từ câu hỏi và context."""
    query = state["query"]
    context = state.get("context", "")
    
    if not context:
        return {"sql_success": False, "error": "Thiếu ngữ cảnh để sinh SQL."}
    
    try:
        sql = generate_sql(query, context)
        if sql.startswith("-- NO"):
            return {"generated_sql": sql, "sql_success": False, "error": "LLM không thể tạo câu truy vấn phù hợp."}
        return {"generated_sql": sql, "sql_success": True, "error": None}
    except Exception as e:
        return {"sql_success": False, "error": f"Lỗi sinh SQL: {str(e)}"}

def execute_sql_node(state: AgentState):
    sql = state.get("generated_sql")
    try:
        data = execute_sql_query(sql)   # giả sử trả về list of rows
        return {"sql_result": data, "sql_success": True, "error": None}
    except Exception as e:
        return {"sql_success": False, "error": f"Lỗi thực thi SQL: {str(e)}"}

def handle_error_node(state: AgentState):
    error_msg = state.get("error", "Đã xảy ra lỗi không xác định.")
    print(f"--- LOG HỆ THỐNG: {error_msg} ---")
    # Reset các trạng thái để đảm bảo an toàn
    return {
        "error": f"⚠️ Thông báo Agent: {error_msg}",
        "sql_success": False,
        "generated_sql": "-- NO_QUERY_POSSIBLE",
        "sql_result": None
    }