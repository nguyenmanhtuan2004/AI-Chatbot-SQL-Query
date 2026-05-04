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
MODEL_ID="gemini-2.5-flash"
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
Bạn là chuyên gia phân tích dữ liệu chuyên nghiệp. Nhiệm vụ: đọc kết quả dữ liệu truy vấn từ cơ sở dữ liệu và phân tích một cách siêu ngắn gọn, súc tích.

# RULES
1. Trả lời đúng trọng tâm câu hỏi của người dùng.
2. Tóm tắt, nhận xét hoặc so sánh xu hướng (tăng/giảm/lớn/nhỏ) chỉ trong 1 đến 2 câu.
3. TUYỆT ĐỐI KHÔNG vẽ bảng Markdown, KHÔNG tạo danh sách liệt kê dài dòng. Dữ liệu chi tiết đã được Frontend lo phần hiển thị bảng.
4. Định dạng số chuẩn: làm tròn 2 chữ số thập phân, tự động thêm dấu phẩy ngăn cách hàng nghìn (VD: 10,000), thêm đơn vị (%, cái, VNĐ...).
5. KHÔNG giải thích mã SQL, KHÔNG bê nguyên tên biến/tên cột kỹ thuật vào câu trả lời tự nhiên.
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
