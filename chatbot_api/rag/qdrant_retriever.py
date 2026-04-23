from qdrant_client import QdrantClient
from langchain_google_vertexai import VertexAIEmbeddings
from core.config import settings

# 1. Khởi tạo Qdrant Client
qdrant_client = QdrantClient(url=settings.QDRANT_URL)

# 2. Khởi tạo Mô hình Nhúng (Embedding)
try:
    embeddings = VertexAIEmbeddings(
        model_name="text-multilingual-embedding-002",
        project="ntb-text-to-sql",
        location="asia-southeast1"
    )
except Exception as e:
    print(f"Cảnh báo: Không thể khởi tạo Vertex AI Embeddings. Lỗi: {e}")
    embeddings = None

def get_context_from_qdrant(query: str, top_k: int = 5) -> str:
    """
    Tìm kiếm và định dạng Context từ Qdrant cho câu hỏi.
    Sử dụng trực tiếp Qdrant Client thay vì LangChain VectorStore để tự do đọc Payload custom.
    """
    if not embeddings:
        return "Lỗi: Chưa cấu hình xong Vertex AI Embeddings."

    # Nhúng câu hỏi thành vector
    query_vector = embeddings.embed_query(query)

    # Tìm kiếm trực tiếp trên Qdrant
    hits = qdrant_client.query_points(
        collection_name="factory_data_dictionary",
        query=query_vector,
        limit=top_k
    ).points
    
    if not hits:
        return "Không tìm thấy dữ liệu liên quan trong Từ điển."

    context_parts = []
    for hit in hits:
        payload = hit.payload or {}
        item_type = payload.get("type", "")
        
        # Payload gốc lưu trong key "raw_json"
        raw_json = payload.get("raw_json", {}).get("content", {})
        
        if item_type == "table_schema":
            cols = ", ".join([c.get("name", "") for c in raw_json.get("columns", [])])
            rels = " ".join(raw_json.get("relationships", []))
            part = (
                f"BẢNG {payload.get('table_name')} (Lĩnh vực: {payload.get('domain')}):\n"
                f"- Mô tả: {raw_json.get('description')}\n"
                f"- Các cột: {cols}\n"
                f"- Liên kết: {rels}"
            )
            context_parts.append(part)
            
        elif item_type == "business_rule":
            part = (
                f"QUY TẮC [{payload.get('metric_name')}]:\n"
                f"- Ý nghĩa: {raw_json.get('description')}\n"
                f"- SQL Logic: {raw_json.get('sql_logic')}\n"
                f"- Điều kiện áp dụng: {raw_json.get('conditions')}"
            )
            context_parts.append(part)
            
    return "\n\n------------------\n\n".join(context_parts)

if __name__ == "__main__":
    test_query = "Tỉ lệ lỗi của chuyền 1 được tính như thế nào?"
    print(f"🔍 Đang nhúng câu hỏi và tìm kiếm trong Qdrant: '{test_query}'...\n")
    try:
        context = get_context_from_qdrant(test_query)
        print("✅ Kết quả (Context) lấy được:\n")
        print(context)
    except Exception as ex:
        print(f"❌ Lỗi tìm kiếm: {ex}")
