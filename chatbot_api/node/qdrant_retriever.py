import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qdrant_client import QdrantClient
from core.config import settings
import requests
import json
import google.auth
import google.auth.transport.requests

# 1. Khởi tạo Qdrant Client
qdrant_client = QdrantClient(url=settings.QDRANT_URL)

# 2. Khởi tạo cấu hình Vertex AI REST API cho Embedding
PROJECT_ID = getattr(settings, "GOOGLE_CLOUD_PROJECT", "ntb-text-to-sql")
EMBEDDING_MODEL = "text-multilingual-embedding-002"

ENDPOINT = (
    f"https://aiplatform.googleapis.com/v1/projects/{PROJECT_ID}"
    f"/locations/global/publishers/google/models/{EMBEDDING_MODEL}:predict"
)

def get_auth_token():
    credentials, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    auth_req = google.auth.transport.requests.Request()
    credentials.refresh(auth_req)
    return credentials.token

def get_embedding(text: str):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {get_auth_token()}",
    }
    body = {
        "instances": [{
            "content": text,
            "task_type": "RETRIEVAL_QUERY"
        }],
    }
    resp = requests.post(ENDPOINT, headers=headers, data=json.dumps(body))
    resp.raise_for_status()
    data = resp.json()
    return data["predictions"][0]["embeddings"]["values"]

def get_context_from_qdrant(query: str, top_k: int = 3) -> str:
    """
    Tìm kiếm và định dạng Context từ Qdrant cho câu hỏi.
    Sử dụng trực tiếp Qdrant Client thay vì LangChain VectorStore để tự do đọc Payload custom.
    """
    # Nhúng câu hỏi thành vector bằng REST API
    try:
        query_vector = get_embedding(query)
    except Exception as e:
        return f"Lỗi: Không thể lấy vector embedding. Chi tiết: {e}"

    # Tìm kiếm trực tiếp trên Qdrant
    hits = qdrant_client.query_points(
        collection_name="factory_data_dictionary",
        query=query_vector,
        limit=top_k,
        score_threshold=0.6
    ).points
    
    if not hits:
        return "Không tìm thấy dữ liệu liên quan trong Từ điển."

    schemas = []
    rules = []
    
    for hit in hits:
        payload = hit.payload or {}
        item_type = payload.get("type", "")
        raw_json = payload.get("raw_json", {}).get("content", {})
        
        if item_type == "table_schema":
            col_parts = []
            for c in raw_json.get("columns", []):
                col_str = f"{c.get('name', '')} ({c.get('type', '')})"
                if c.get("example_values"):
                    col_str += f" -- ví dụ: {c['example_values']}"
                col_parts.append(col_str)
            cols = ", ".join(col_parts)
            rels = " ".join(raw_json.get("relationships", []))
            part = (
                f"BẢNG {payload.get('table_name')} (Lĩnh vực: {payload.get('domain')}):\n"
                f"- Mô tả: {raw_json.get('description')}\n"
                f"- Các cột: {cols}\n"
                f"- Liên kết: {rels}"
            )
            schemas.append(part)
            
        elif item_type == "business_rule":
            # Trích xuất few-shot example để mồi cho LLM
            few_shot = raw_json.get("few_shot_example", {})
            example_text = ""
            if few_shot:
                example_text = f"\n- VÍ DỤ MẪU:\n  + Câu hỏi: {few_shot.get('user_query')}\n  + SQL: {few_shot.get('expected_sql')}"

            part = (
                f"QUY TẮC [{payload.get('metric_name')}]:\n"
                f"- Ý nghĩa: {raw_json.get('description')}\n"
                f"- SQL Logic: {raw_json.get('sql_logic')}\n"
                f"- Điều kiện áp dụng: {raw_json.get('conditions')}"
                f"{example_text}"
            )
            rules.append(part)
            
    # Gộp tất cả Schema lên trước, Rules xuống sau
    final_context = "=== THÔNG TIN CÁC BẢNG (SCHEMA) ===\n" + "\n\n------------------\n\n".join(schemas) if schemas else ""
    if rules:
        final_context += "\n\n=== QUY TẮC NGHIỆP VỤ (BUSINESS RULES) ===\n" + "\n\n------------------\n\n".join(rules)
        
    return final_context.strip()

if __name__ == "__main__":
    test_query = "Tôi biết số lượng lỗi nghiêm trọng xảy ra ở chuyền 3 trong tuần này?"
    print(f"🔍 Đang nhúng câu hỏi và tìm kiếm trong Qdrant: '{test_query}'...\n")
    try:
        context = get_context_from_qdrant(test_query)
        print("✅ Kết quả (Context) lấy được:\n")
        print(context)
    except Exception as ex:
        print(f"❌ Lỗi tìm kiếm: {ex}")
