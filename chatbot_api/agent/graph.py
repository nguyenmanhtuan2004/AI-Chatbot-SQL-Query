from langgraph.graph import StateGraph, END
from agent.state import AgentState
from agent.nodes import (
    retrieve_context_node, 
    generate_sql_node, 
    execute_sql_node, 
    generate_answer_node,
    handle_error_node
)
from agent.edges import after_retrieve, after_generate, after_execute

# 1. Khởi tạo đồ thị với AgentState
workflow = StateGraph(AgentState)

# 2. Thêm các nodes vào đồ thị
workflow.add_node("retrieve_context", retrieve_context_node)
workflow.add_node("generate_sql", generate_sql_node)
workflow.add_node("execute_sql", execute_sql_node)
workflow.add_node("generate_answer", generate_answer_node)
workflow.add_node("handle_error", handle_error_node)

# 3. Định nghĩa các luồng (edges)
workflow.set_entry_point("retrieve_context")

# Rẽ nhánh sau khi lấy context
workflow.add_conditional_edges(
    "retrieve_context",
    after_retrieve,
    {
        "generate_sql": "generate_sql",
        "handle_error": "handle_error"
    }
)

# Rẽ nhánh sau khi sinh SQL
workflow.add_conditional_edges(
    "generate_sql",
    after_generate,
    {
        "execute_sql": "execute_sql",
        "handle_error": "handle_error"
    }
)

# Rẽ nhánh sau khi thực thi SQL
workflow.add_conditional_edges(
    "execute_sql",
    after_execute,
    {
        "generate_answer": "generate_answer",
        "generate_sql": "generate_sql",
        "handle_error": "handle_error"
    }
)

# Sau khi sinh câu trả lời → kết thúc
workflow.add_edge("generate_answer", END)

# handle_error dẫn đến kết thúc
workflow.add_edge("handle_error", END)

# 4. Biên dịch đồ thị thành ứng dụng
app = workflow.compile()