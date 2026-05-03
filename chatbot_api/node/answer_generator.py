import os
import sys
import json
import requests
import google.auth
import google.auth.transport.requests

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import settings

# Khởi tạo cấu hình Vertex AI REST API
PROJECT_ID = getattr(settings, "GOOGLE_CLOUD_PROJECT", "ntb-text-to-sql")
MODEL_ID = "gemini-3.1-pro-preview"
ENDPOINT = (
    f"https://aiplatform.googleapis.com/v1/projects/{PROJECT_ID}"
    f"/locations/global/publishers/google/models/{MODEL_ID}:generateContent"
)

def get_auth_token():
    credentials, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    auth_req = google.auth.transport.requests.Request()
    credentials.refresh(auth_req)
    return credentials.token

_ANSWER_SYSTEM_PROMPT = """
# ROLE
Bạn là chuyên gia phân tích dữ liệu sản xuất. Nhiệm vụ: diễn giải kết quả SQL thành câu trả lời tiếng Việt rõ ràng, súc tích, chính xác và trực quan.

# RULES
1. Trả lời đúng trọng tâm câu hỏi của người dùng.
2. CẤU TRÚC TRẢ LỜI 2 PHẦN:
   - Phần 1 (Phân tích): Trình bày ngắn gọn số liệu tổng quan, nhận xét hoặc so sánh xu hướng (tăng/giảm) nếu có.
   - Phần 2 (Bảng dữ liệu): Luôn luôn vẽ một BẢNG MARKDOWN chi tiết dựa trên dữ liệu JSON nhận được (trừ khi chỉ có 1 con số duy nhất). Đổi tên cột trong bảng sang tiếng Việt cho dễ hiểu (ví dụ: 'Quantity' thành 'Sản lượng').
3. Định dạng số: làm tròn 2 chữ số thập phân, thêm ký tự phân cách hàng nghìn (ví dụ: 10,000) và đơn vị phù hợp (%, VNĐ, cái...).
4. KHÔNG giải thích SQL, KHÔNG đề cập tên bảng / tên biến kỹ thuật quá sâu.
""".strip()

def generate_answer(query: str, generated_sql: str, sql_result: any) -> str:
    """Dùng LLM diễn giải kết quả truy vấn SQL thành câu trả lời tự nhiên."""
    result_text = json.dumps(sql_result, ensure_ascii=False, default=str)
    
    prompt = f"""{_ANSWER_SYSTEM_PROMPT}

# CÂU HỎI CỦA NGƯỜI DÙNG
{query}

# CÂU TRUY VẤN SQL ĐÃ THỰC THI
{generated_sql}

# KẾT QUẢ TRUY VẤN (JSON)
{result_text}

# TRẢ LỜI (tiếng Việt):"""

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {get_auth_token()}",
    }
    
    body = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt}],
            }
        ]
    }

    resp = requests.post(ENDPOINT, headers=headers, data=json.dumps(body))
    resp.raise_for_status()
    data = resp.json()

    text_parts = data["candidates"][0]["content"]["parts"]
    answer = "".join(p.get("text", "") for p in text_parts)
    
    return answer.strip()
