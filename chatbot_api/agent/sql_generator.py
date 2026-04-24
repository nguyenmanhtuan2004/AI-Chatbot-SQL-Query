from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from core.config import settings

# Khởi tạo mô hình với API Key từ settings
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite", 
    temperature=0,
    google_api_key=settings.GOOGLE_API_KEY
)

def clean_sql(raw: str) -> str:
    """Làm sạch kết quả trả về từ LLM."""
    raw = raw.strip()
    # Loại bỏ markdown code block
    if raw.startswith("```sql"):
        raw = raw[6:]
    elif raw.startswith("```"):
        raw = raw[3:]
    if raw.endswith("```"):
        raw = raw[:-3]
    # Lấy khối cuối cùng nếu LLM có dẫn giải
    raw = raw.split("\n\n")[-1]
    return raw.strip()

# Định nghĩa Prompt Template theo Markdown + Structured Messages
SYSTEM_PROMPT = """
# ROLE
Bạn là một chuyên gia MS SQL Server cấp cao. Nhiệm vụ của bạn là viết mã SQL chính xác dựa trên SCHEMA và CONTEXT được cung cấp.

# CONSTRAINTS (BẮT BUỘC)
1. **Output:** Chỉ trả về chuỗi SQL thuần, không markdown, không giải thích. Nếu không thể tạo SQL -> trả về '-- NO_QUERY_POSSIBLE'.
2. **Schema:** Chỉ sử dụng cột, bảng, kiểu dữ liệu đã cho trong Context.
3. **Tham số hóa:** Luôn dùng tham số hóa: @p1, @p2,... cho giá trị người dùng. KHÔNG ghép chuỗi trực tiếp.
4. **So sánh Chuỗi:**
    - Dùng `=` cho khớp chính xác.
    - Dùng `LIKE '%' + @p + '%'` chỉ khi có từ khóa: "tìm kiếm", "chứa", "gần đúng". 
    - Nếu chuỗi có ký tự wildcard (%, _, [, ]) -> Thêm `ESCAPE '\\'` và REPLACE ký tự đó.
5. **So sánh Ngày tháng (Datetime):**
    - Luôn dùng `>=` và `<` cho khoảng thời gian.
    - Nếu chỉ có ngày (vd: '2025-01-01') -> `date_col >= @p AND date_col < DATEADD(day, 1, @p)`.
6. **So sánh Số:** Giữ nguyên kiểu dữ liệu, không ép kiểu ngầm (vd: `price = @p`).
7. **Sắp xếp (ORDER BY):** Mặc định lấy cột đầu tiên của bảng đầu tiên trong mệnh đề FROM nếu người dùng không yêu cầu khác.
8. **JOIN:** Bắt buộc dùng alias bảng (AS) (vd: `FROM Orders AS o INNER JOIN Customers AS c ON o.CustId = c.Id`).
9. **Giới hạn (TOP):**
    - Dùng `TOP 10` (hoặc số hợp lý) cho các câu hỏi liệt kê danh sách.
    - Chỉ dùng `TOP 1000` nếu câu hỏi không chỉ rõ số lượng.
    - Nếu người dùng nói "tất cả", "toàn bộ" → không dùng TOP (hoặc nếu bảng quá lớn, có thể dùng TOP 1000 kèm comment).
10. **Read-Only:** Chỉ được phép SELECT. Tuyệt đối cấm INSERT, UPDATE, DELETE, DROP, ALTER.
11. **Phép chia:** Bắt buộc dùng `NULLIF(mẫu_số, 0)` cho mọi phép chia để tránh lỗi chia cho 0.
12. **Unicode:** Với chuỗi tiếng Việt hoặc có dấu, luôn dùng `N'...'` (ví dụ: `WHERE name = N'@p'`).
# OUTPUT FORMAT
- Chỉ trả về duy nhất mã SQL.
"""

USER_PROMPT_TEMPLATE = """
# DATA CONTEXT
{context}

# USER QUESTION
{query}

# SQL RESPONSE:
"""

prompt_template = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("user", USER_PROMPT_TEMPLATE)
])

def generate_sql(query: str, context: str) -> str:
    """Hàm lõi thực hiện việc gọi LLM để sinh mã SQL."""
    chain = prompt_template | llm
    response = chain.invoke({"query": query, "context": context})
    
    raw_sql = response.content
    return clean_sql(raw_sql)
