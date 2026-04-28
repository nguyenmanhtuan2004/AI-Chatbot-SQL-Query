import os
import json
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
import vertexai
from vertexai.language_models import TextEmbeddingModel
from google.oauth2 import service_account

# 1. Khởi tạo Clients
qdrant = QdrantClient(url="http://localhost:6333")

# Lấy đường dẫn tuyệt đối đến file service account key
SERVICE_ACCOUNT_FILE = os.path.join(os.path.dirname(__file__), '..', 'chatbot_api', 'ntb-text-to-sql-9d0c44f85945.json')

# Khởi tạo xác thực
credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE)

# Khởi tạo Vertex AI
# Bạn cần thay đổi <YOUR_PROJECT_ID> thành Project ID thực tế trên Google Cloud của bạn
vertexai.init(project="ntb-text-to-sql", location="asia-southeast1", credentials=credentials) 
# Model hỗ trợ tiếng Việt tốt nhất hiện nay của Google
embedding_model = TextEmbeddingModel.from_pretrained("text-multilingual-embedding-002")

def get_embedding(text):
    # Vertex AI SDK trả về một danh sách, lấy phần tử đầu tiên
    embeddings = embedding_model.get_embeddings([text])
    return embeddings[0].values

# 2. Quét thư mục
folder_path = "data_rules"
points = []
point_id = 1 # Qdrant yêu cầu ID là số nguyên (Integer) hoặc chuỗi UUID

for filename in os.listdir(folder_path):
    if not filename.endswith(".json"): continue
    
    file_path = os.path.join(folder_path, filename)
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
        # Xử lý: File Rule JSON là Array dạng [{}, {}], Schema Table là Object {}
        items = data if isinstance(data, list) else [data]
        
        for item in items:
            metadata = item.get("metadata", {})
            content = item.get("content", {})
            
            # 3. Nén JSON thành chuỗi văn bản (Semantic Text) để Embedding hiệu quả nhất
            embed_text = ""
            if metadata.get("type") == "table_schema":
                cols = ", ".join([c["name"] for c in content.get("columns", [])])
                rels = " ".join(content.get("relationships", []))
                embed_text = f"Bảng {metadata.get('table_name')} (Lĩnh vực: {metadata.get('domain')}): {content.get('description')} " \
                             f"Bao gồm các cột: {cols}. " \
                             f"Liên kết: {rels}"
            elif metadata.get("type") == "business_rule":
                embed_text = f"Quy tắc tính năng: {metadata.get('metric_name')}. " \
                             f"Từ khóa hỏi đáp: {', '.join(metadata.get('trigger_keywords', []))}. " \
                             f"Ý nghĩa: {content.get('description')} " \
                             f"Logic SQL: {content.get('sql_logic')}. Điều kiện: {content.get('conditions')}"

            # Nhúng dữ liệu thành dãy số Vector
            vector = get_embedding(embed_text)
            
            # 4. Đóng gói (Lưu PointStruct)
            points.append(PointStruct(
                id=point_id, 
                vector=vector, 
                payload={
                    "raw_json": item, # Lưu nguyên JSON trả về cho prompt Prompt sau này
                    **metadata        # Cài thêm các bộ lọc
                }
            ))
            point_id += 1

# 5. Push toàn bộ vào Vector DB
qdrant.upsert(
    collection_name="factory_data_dictionary",
    points=points
)
print(f"Thành công! Đã đẩy {len(points)} vector vào Qdrant.")
