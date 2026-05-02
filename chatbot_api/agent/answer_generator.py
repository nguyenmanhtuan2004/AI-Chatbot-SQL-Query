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
Bạn là chuyên gia phân tích dữ liệu sản xuất. Nhiệm vụ: diễn giải kết quả SQL thành câu trả lời tiếng Việt rõ ràng, súc tích, chính xác.

# RULES
1. Trả lời đúng trọng tâm câu hỏi của người dùng.
2. Nếu kết quả chỉ có 1 dòng dữ liệu hoặc không đủ để xác định xu hướng (tăng/giảm), hãy nói rõ "Chỉ có dữ liệu của X ngày nên chưa thể xác định xu hướng" và trình bày số liệu hiện có.
3. Khi phân tích xu hướng (tăng/giảm) với nhiều dòng: so sánh ngày đầu và ngày cuối, tính % thay đổi và nêu nhận xét.
4. Định dạng số: làm tròn 2 chữ số thập phân, thêm đơn vị phù hợp (%, sản phẩm, ngày...).
5. Trình bày ngắn gọn, dùng bullet point nếu có nhiều ý. Không in lại toàn bộ bảng dữ liệu thô.
6. KHÔNG giải thích SQL, KHÔNG đề cập tên bảng / cột kỹ thuật trừ khi người dùng hỏi.
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
