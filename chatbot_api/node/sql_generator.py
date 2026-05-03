import os
import re
import sys
import requests
import json
import google.auth
import google.auth.transport.requests

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import settings

# --- 1. KHỞI TẠO CẤU HÌNH VERTEX AI BẰNG REST API CỦA GCP ($300 CREDIT) ---
PROJECT_ID = getattr(settings, "GOOGLE_CLOUD_PROJECT", "ntb-text-to-sql")
MODEL_ID="gemini-3-flash-preview"


ENDPOINT = (
    f"https://aiplatform.googleapis.com/v1/projects/{PROJECT_ID}"
    f"/locations/global/publishers/google/models/{MODEL_ID}:generateContent"
)

def get_auth_token():
    credentials, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    auth_req = google.auth.transport.requests.Request()
    credentials.refresh(auth_req)
    return credentials.token


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
- Chỉ trả về duy nhất mã SQL.
"""


# --- 3. HÀM GENERATE_SQL MỚI (DÙNG VERTEX AI) ---
FIX_SQL_PROMPT = """
# ROLE & TASK
Bạn là chuyên gia MS SQL Server. Câu truy vấn SQL trước đó bạn viết đã gặp lỗi khi thực thi. 
Nhiệm vụ của bạn là phân tích nguyên nhân lỗi và VIẾT LẠI câu SQL cho đúng.

# DATA CONTEXT
{context}

# USER QUESTION
{query}

# PREVIOUS SQL (BỊ LỖI)
{previous_sql}

# ERROR MESSAGE TỪ HỆ THỐNG
{error_message}

# INSTRUCTIONS ĐỂ SỬA LỖI
1. Đọc kỹ ERROR MESSAGE. Nếu là lỗi sai tên cột/bảng (Invalid object name, Invalid column name...), hãy xem lại DATA CONTEXT xem tên chính xác là gì.
2. Nếu là lỗi Logic (chia cho 0, thiếu ngoặc, sai kiểu dữ liệu), hãy sửa lại cú pháp.
3. Chỉ trả về mã SQL thuần sau khi sửa, KHÔNG bọc markdown, KHÔNG giải thích gì thêm.
"""

def generate_sql(query: str, context: str, previous_sql: str = None, error_msg: str = None) -> str:
    """Hàm lõi thực hiện việc gọi Vertex AI để sinh mã SQL."""
    if previous_sql and error_msg:
        full_prompt = FIX_SQL_PROMPT.format(
            context=context,
            query=query,
            previous_sql=previous_sql,
            error_message=error_msg
        )
    else:
        full_prompt = f"""{SYSTEM_PROMPT}

# DATA CONTEXT
{context}

# USER QUESTION
{query}

# SQL RESPONSE:"""
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {get_auth_token()}",
    }

    body = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": full_prompt}],
            }
        ]
    }

    resp = requests.post(ENDPOINT, headers=headers, data=json.dumps(body))
    resp.raise_for_status()
    data = resp.json()

    text_parts = data["candidates"][0]["content"]["parts"]
    raw_sql = "".join(p.get("text", "") for p in text_parts)
    
    return clean_sql(raw_sql)


# --- PHẦN TEST NHANH (giữ nguyên) ---
if __name__ == "__main__":
    from node.qdrant_retriever import get_context_from_qdrant
    
    print("🚀 Bắt đầu test nhanh SQL Generator (Vertex AI)...")
    
    mock_query = "Hôm nay chuyền 1 làm được bao nhiêu sản phẩm?"
    print(f"📌 Câu hỏi: {mock_query}")
    
    print("⏳ Đang lấy context từ Qdrant...")
    mock_context = get_context_from_qdrant(mock_query)
    print(f"\n✅ === CONTEXT TỪ QDRANT ===\n{mock_context}\n===========================\n")
    
    try:
        print("⏳ Đang gọi Vertex AI...")
        sql_result = generate_sql(mock_query, mock_context)
        print("\n✅ === KẾT QUẢ SQL ===")
        print(sql_result)
        print("=======================\n")
    except Exception as e:
        print(f"\n❌ Lỗi khi sinh SQL: {e}")