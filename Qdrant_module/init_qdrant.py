from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

# Kết nối tới Qdrant đang chạy trong Docker
client = QdrantClient(url="http://localhost:6333") 

# Bỏ comment dòng dưới để xóa DB cũ làm lại từ đầu (nếu test nhiều lần)
# client.delete_collection(collection_name="factory_data_dictionary")

# Tạo collection (Lưu ý: vector size của Vertex AI là 768 thay vì 1536)
client.recreate_collection(
    collection_name="factory_data_dictionary",
    vectors_config=VectorParams(size=768, distance=Distance.COSINE),
)

print("Khởi tạo Qdrant collection 'factory_data_dictionary' thành công!")
