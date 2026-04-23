from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from agent.state import AgentState
from rag.qdrant_retriever import get_context_from_qdrant
import os

# Khởi tạo mô hình ngôn ngữ
# Đọc GOOGLE_API_KEY từ biến môi trường đã được load bởi dotenv trong main hoặc config
llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0)

def retrieve_context_node(state: AgentState):
    """Lấy dữ liệu từ điển (schema & business rules) từ Qdrant."""
    query = state["query"]
    context = get_context_from_qdrant(query)
    return {"context": context}

def generate_sql_node(state: AgentState):
    """Sử dụng LLM để sinh ra câu truy vấn SQL từ câu hỏi và context."""
    query = state["query"]
    context = state.get("context", "")
    
    prompt_template = """Bạn là một chuyên gia về hệ quản trị cơ sở dữ liệu MS SQL Server.
Nhiệm vụ của bạn là viết câu lệnh truy vấn SQL chính xác để trả lời câu hỏi của người dùng dựa trên thông tin SCHEMA và QUY TẮC NGHIỆP VỤ (Context) dưới đây.

Lưu ý quan trọng:
- CHỈ trả về duy nhất chuỗi câu truy vấn SQL, KHÔNG chứa định dạng Markdown như ```sql hay giải thích thêm.
- Sử dụng đúng tên bảng, tên cột và công thức đã cung cấp trong quy tắc.

[CONTEXT]
{context}

[CÂU HỎI CỦA NGƯỜI DÙNG]
{query}"""
    
    prompt = ChatPromptTemplate.from_template(prompt_template)
    chain = prompt | llm
    
    response = chain.invoke({"query": query, "context": context})
    sql_query = response.content.replace("```sql", "").replace("```", "").strip()
    return {"sql_query": sql_query}