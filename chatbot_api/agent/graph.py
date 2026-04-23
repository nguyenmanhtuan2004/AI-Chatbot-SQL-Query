from langgraph.graph import StateGraph, END
from agent.state import AgentState
from agent.nodes import retrieve_context_node, generate_sql_node

# 1. Khởi tạo đồ thị với AgentState
workflow = StateGraph(AgentState)

# 2. Thêm các nodes vào đồ thị
workflow.add_node("retrieve_context", retrieve_context_node)
workflow.add_node("generate_sql", generate_sql_node)

# 3. Định nghĩa các luồng (edges)
workflow.set_entry_point("retrieve_context")
workflow.add_edge("retrieve_context", "generate_sql")
workflow.add_edge("generate_sql", END)

# 4. Biên dịch đồ thị thành ứng dụng
app = workflow.compile()