import json
from agent.state import AgentState
from node.qdrant_retriever import get_context_from_qdrant
from node.sql_generator import generate_sql
from node.answer_generator import generate_answer
from node.sql_executor import execute_sql_query

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
    previous_sql = state.get("generated_sql")
    error_msg = state.get("error")
    retry_count = state.get("retry_count", 0)
    
    if not context:
        return {"sql_success": False, "error": "Thiếu ngữ cảnh để sinh SQL."}
    
    is_retry = (retry_count > 0 and previous_sql and error_msg)
    
    try:
        if is_retry:
            print(f"♻️ [RETRY {retry_count}] AI đang cố gắng tự sửa lỗi SQL...")
            sql = generate_sql(query, context, previous_sql, error_msg)
        else:
            sql = generate_sql(query, context)
            
        if sql.startswith("-- NO"):
            return {"generated_sql": sql, "sql_success": False, "error": "LLM không thể tạo câu truy vấn phù hợp."}
        return {"generated_sql": sql, "sql_success": True, "error": None}
    except Exception as e:
        return {"sql_success": False, "error": f"Lỗi sinh SQL: {str(e)}"}

def execute_sql_node(state: AgentState):
    sql = state.get("generated_sql")
    retry_count = state.get("retry_count", 0)
    try:
        data = execute_sql_query(sql)   # giả sử trả về list of rows
        return {"sql_result": data, "sql_success": True, "error": None, "retry_count": retry_count}
    except Exception as e:
        print(f"❌ [LỖI THỰC THI SQL]: {str(e)}")
        return {"sql_success": False, "error": f"Lỗi thực thi SQL: {str(e)}", "retry_count": retry_count + 1}


def generate_answer_node(state: AgentState):
    """Dùng module answer_generator để diễn giải kết quả SQL thành câu trả lời ngôn ngữ tự nhiên."""
    query = state.get("query", "")
    sql_result = state.get("sql_result")
    generated_sql = state.get("generated_sql", "")

    try:
        answer = generate_answer(query, generated_sql, sql_result)
        return {"answer": answer}
    except Exception as e:
        return {"answer": f"Không thể diễn giải kết quả: {str(e)}"}


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