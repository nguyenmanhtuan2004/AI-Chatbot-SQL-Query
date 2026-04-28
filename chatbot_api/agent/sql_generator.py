import os
import re
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import vertexai
from vertexai.generative_models import GenerativeModel
from core.config import settings

# --- 1. KHỞI TẠO VERTEX AI ---
# Lấy thông tin từ settings (bạn nên thêm các biến này vào .env)
PROJECT_ID = getattr(settings, "GOOGLE_CLOUD_PROJECT", "ntb-text-to-sql")
LOCATION = getattr(settings, "GOOGLE_CLOUD_LOCATION", "asia-southeast1")

vertexai.init(project=PROJECT_ID, location=LOCATION)

MODEL_NAME = "gemini-2.5-flash"  
llm_model = GenerativeModel(MODEL_NAME)


# --- 2. GIỮ NGUYÊN CÁC HÀM CLEAN_SQL VÀ PROMPT ---
def clean_sql(raw: str) -> str:
    """Làm sạch kết quả trả về từ LLM."""
    raw = raw.strip()
    # Bóc bỏ markdown code fence nếu có
    if raw.startswith("```sql"):
        raw = raw[6:]
    elif raw.startswith("```"):
        raw = raw[3:]
    if raw.endswith("```"):
        raw = raw[:-3]
    raw = raw.strip()
    # Tìm điểm bắt đầu thực sự của SQL để loại bỏ phần giải thích của LLM
    # mà không làm vỡ CTE (WITH ...) hoặc query nhiều dòng trắng
    sql_start = re.search(
        r"^[ \t]*(WITH|SELECT|INSERT|UPDATE|DELETE|--)",
        raw,
        re.IGNORECASE | re.MULTILINE,
    )
    if sql_start:
        raw = raw[sql_start.start():]
    return raw.strip()


SYSTEM_PROMPT = """
# ROLE
Bạn là một chuyên gia MS SQL Server cấp cao. Nhiệm vụ của bạn là viết mã SQL chính xác dựa trên SCHEMA và CONTEXT được cung cấp.

# CONSTRAINTS (BẮT BUỘC)
1. **Output:** Chỉ trả về chuỗi SQL thuần, không markdown, không giải thích. Nếu không thể tạo SQL -> trả về '-- NO_QUERY_POSSIBLE'.
2. **Schema:** Chỉ sử dụng cột, bảng, kiểu dữ liệu đã cho trong Context.
3. **So sánh Chuỗi:**
    - Dùng `=` cho khớp chính xác.
    - Nếu chuỗi có ký tự wildcard (%, _, [, ]) -> Thêm `ESCAPE '\\'` và REPLACE ký tự đó.
4. **So sánh Ngày tháng (Datetime):**
    - Luôn dùng `>=` và `<` cho khoảng thời gian.
    - Nếu chỉ có ngày (vd: '2025-01-01') -> `date_col >= @p AND date_col < DATEADD(day, 1, @p)`.
5. **So sánh Số:** Giữ nguyên kiểu dữ liệu, không ép kiểu ngầm (vd: `price = @p`).
6. **Sắp xếp (ORDER BY):** Mặc định lấy cột đầu tiên của bảng đầu tiên trong mệnh đề FROM nếu người dùng không yêu cầu khác.
7. **JOIN:** Bắt buộc dùng alias bảng (AS) (vd: `FROM Orders AS o INNER JOIN Customers AS c ON o.CustId = c.Id`).
8. **Giới hạn (TOP):**
    - Dùng `TOP 10` (hoặc số hợp lý) cho các câu hỏi liệt kê danh sách.
    - Chỉ dùng `TOP 1000` nếu câu hỏi không chỉ rõ số lượng.
    - Nếu người dùng nói "tất cả", "toàn bộ" → không dùng TOP (hoặc nếu bảng quá lớn, có thể dùng TOP 1000 kèm comment).
9. **Read-Only:** Chỉ được phép SELECT. Tuyệt đối cấm INSERT, UPDATE, DELETE, DROP, ALTER.
10. **Phép chia:** Bắt buộc dùng `NULLIF(mẫu_số, 0)` cho mọi phép chia để tránh lỗi chia cho 0.
11. **Unicode:** Với chuỗi tiếng Việt hoặc có dấu, luôn dùng `N'...'` (ví dụ: `WHERE name = N'@p'`).
12. **COALESCE cho hàm tổng hợp:** Khi dùng `SUM()` trên các cột đếm số lượng (DefectCount, Quantity, v.v.), bắt buộc bọc `COALESCE(SUM(...), 0)` để trả về `0` thay vì `NULL` khi không có dữ liệu khớp.
13. **UNION ALL với ORDER BY:** KHÔNG được dùng `ORDER BY` trực tiếp bên trong ngoặc `(...)` của `UNION ALL`. Phải bọc mỗi SELECT trong một subquery có alias riêng:
    ```
    SELECT * FROM (SELECT TOP N ... ORDER BY ... ASC) AS alias1
    UNION ALL
    SELECT * FROM (SELECT TOP N ... ORDER BY ... DESC) AS alias2
    ```
14. **LineID - QUY TẮC BẮT BUỘC:**
    - Cột `LineID` là kiểu VARCHAR, KHÔNG BAO GIỜ là số nguyên.
    - Khi người dùng nói "chuyền 1" → `LineID = 'LINE_01'`
    - Khi người dùng nói "chuyền 2" → `LineID = 'LINE_02'`
    - Khi người dùng nói "chuyền 3" → `LineID = 'LINE_03'`
    - Áp dụng tương tự cho chuyền 4 → `'LINE_04'`, chuyền 5 → `'LINE_05'`, v.v.
    - TUYỆT ĐỐI cấm viết `LineID = 1`, `LineID = 2`, `LineID = 3` (kiểu số nguyên).
- Chỉ trả về duy nhất mã SQL.
"""


# --- 3. HÀM GENERATE_SQL MỚI (DÙNG VERTEX AI) ---
def generate_sql(query: str, context: str) -> str:
    """Hàm lõi thực hiện việc gọi Vertex AI để sinh mã SQL."""
    # Ghép system prompt + context + query
    full_prompt = f"""{SYSTEM_PROMPT}

# DATA CONTEXT
{context}

# USER QUESTION
{query}

# SQL RESPONSE:"""
    
    response = llm_model.generate_content(full_prompt)
    raw_sql = response.text
    return clean_sql(raw_sql)


# --- PHẦN TEST NHANH (giữ nguyên) ---
if __name__ == "__main__":
    print("🚀 Bắt đầu test nhanh SQL Generator (Vertex AI)...")
    
    mock_context = """
    Bảng PRODUCTIVITY:
    - ID (int): Khóa chính
    - LineID (string): Mã chuyền sản xuất
    - Quantity (int): Sản lượng
    - StartTime (datetime): Thời gian bắt đầu
    """
    
    mock_query = "Hôm nay chuyền L01 làm được bao nhiêu sản phẩm?"
    print(f"📌 Câu hỏi: {mock_query}")
    
    try:
        print("⏳ Đang gọi Vertex AI...")
        sql_result = generate_sql(mock_query, mock_context)
        print("\n✅ === KẾT QUẢ SQL ===")
        print(sql_result)
        print("=======================\n")
    except Exception as e:
        print(f"\n❌ Lỗi khi sinh SQL: {e}")